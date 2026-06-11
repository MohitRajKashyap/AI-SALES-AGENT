import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


async def send_email(
    to_email: str,
    subject: str,
    body_text: str,
    body_html: Optional[str] = None,
    from_name: str = "AI Sales Agent",
) -> bool:
    """
    Send an email via SMTP. Returns True on success, False on failure.
    In production, swap this for SendGrid/SES/Mailgun for better deliverability.
    """
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.warning("SMTP not configured — email not sent")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{from_name} <{settings.EMAILS_FROM_EMAIL}>"
    msg["To"] = to_email

    msg.attach(MIMEText(body_text, "plain"))
    if body_html:
        msg.attach(MIMEText(body_html, "html"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.ehlo()
            server.starttls(context=context)
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAILS_FROM_EMAIL, to_email, msg.as_string())
        logger.info(f"Email sent to {to_email}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


def build_tracking_pixel_html(tracking_id: str, base_url: str) -> str:
    """Inject a 1x1 tracking pixel into an email body for open tracking."""
    pixel_url = f"{base_url}/api/v1/track/open/{tracking_id}"
    return f'<img src="{pixel_url}" width="1" height="1" alt="" style="display:none;" />'


def build_tracked_link(url: str, tracking_id: str, base_url: str) -> str:
    """Wrap a link through the click-tracking endpoint."""
    from urllib.parse import quote
    encoded = quote(url, safe="")
    return f"{base_url}/api/v1/track/click/{tracking_id}?url={encoded}"


def plain_to_html(text: str, tracking_id: str, base_url: str) -> str:
    """Convert plain-text email body to HTML with tracking pixel."""
    html_body = text.replace("\n", "<br>")
    pixel = build_tracking_pixel_html(tracking_id, base_url)
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif; font-size: 15px; color: #333; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px;">
{html_body}
{pixel}
</body>
</html>"""
