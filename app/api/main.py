from fastapi import FastAPI
from app.api.routes import router as api_router
from app.core.config import settings
from app.db.session import engine
from app.db.utils import create_db_and_tables
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi_events.middleware import EventHandlerASGIMiddleware
from fastapi_events.handlers.local import local_handler


def get_application():
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        docs_url="/docs",
    )
    app.include_router(api_router)
    return app


app = get_application()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(EventHandlerASGIMiddleware, handlers=[local_handler])
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def on_startup():
    await create_db_and_tables(engine)


@app.get("/", tags=["health"])
async def health():
    return dict(
        name=settings.PROJECT_NAME,
        version=settings.VERSION,
        status="OK",
        message="Visit /docs for more information.",
    )
