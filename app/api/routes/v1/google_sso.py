from fastapi_sso.sso.google import GoogleSSO
from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_session
from app.repository.base import BaseRepository
from app.models.user import User, TokenSchema
from app.crud.user import DuplicateError
from app.core.security import (
    create_access_token,
    create_refresh_token,
)


router = APIRouter(prefix="/google", tags=["Google SSO"])


def get_google_sso() -> GoogleSSO:
    return GoogleSSO(
        settings.GOOGLE_CLIENT_ID,
        settings.GOOGLE_CLIENT_SECRET,
        redirect_uri=f"http://{settings.HOST}:{settings.PORT}/api/v1/google/callback",
        allow_insecure_http=True,
    )


@router.get("/login", summary="Login with SSO.")
async def google_login(
    google_sso: GoogleSSO = Depends(get_google_sso),
) -> RedirectResponse:
    try:
        redirect_uri = await google_sso.get_login_redirect(
            params={"prompt": "consent", "access_type": "offline"}
        )
        if not isinstance(redirect_uri, RedirectResponse):
            raise HTTPException(
                status_code=500, detail="Failed to get redirect response."
            )
        return redirect_uri
    except Exception as e:
        print(f"Error in google_login: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/callback", response_model=TokenSchema, summary="SSO callback.")
async def google_callback(
    request: Request,
    session: AsyncSession = Depends(get_session),
    google_sso: GoogleSSO = Depends(get_google_sso),
) -> TokenSchema:
    """Process login response from Google and return user info"""

    try:
        user = await google_sso.verify_and_process(request)
        try:  #   Check whether user is exist
            user = await BaseRepository(User).get_by_item(
                session=session, email=user.email, provider=user.provider
            )
        except:  #   User have not registered yet => Create a new user
            data_to_add = {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "provider": user.provider,
            }
            user = await BaseRepository(User).create(session=session, **data_to_add)
        return TokenSchema(
            access_token=create_access_token(
                subject=user.email, provider=user.provider
            ),
            refresh_token=create_refresh_token(
                subject=user.email, provider=user.provider
            ),
        )
    except DuplicateError as e:
        raise HTTPException(status_code=403, detail=f"{e}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred. Report this message to support: {e}",
        )
