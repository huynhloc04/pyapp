import os
import smtplib
from celery import Celery
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

celery = Celery(__name__)
celery.conf.broker_url = os.getenv("CELERY_BROKER_URL")
celery.conf.result_backend = os.getenv("CELERY_RESULT_BACKEND")

print(os.getenv("CELERY_BROKER_URL"))
print(os.getenv("CELERY_RESULT_BACKEND"))


@celery.task
def send_email_task(mail_subject: str, mail_body: str, customer_email: str):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "haiharo04@gmail.com"
    smtp_password = "djub sstm dvrx ryyb"

    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = customer_email
    msg["Subject"] = mail_subject
    msg.attach(MIMEText(mail_body, "plain"))

    # Send email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, customer_email, msg.as_string())
    except Exception as e:
        print(f"Error: {e}")
