import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

SMTP_PRESETS = {
    "gmail.com": ("smtp.gmail.com", 587),
    "googlemail.com": ("smtp.gmail.com", 587),
    "outlook.com": ("smtp.office365.com", 587),
    "hotmail.com": ("smtp.office365.com", 587),
    "yahoo.com": ("smtp.mail.yahoo.com", 587),
}

def resolve_smtp_settings(email_address: str) -> tuple[str, int]:
    """Auto-detects SMTP host and port based on email domain, defaults to Gmail."""
    domain = email_address.strip().lower().split("@")[-1]
    return SMTP_PRESETS.get(domain, ("smtp.gmail.com", 587))

def test_smtp_credentials(email_address: str, password: str, host: str, port: int) -> tuple[bool, str]:
    """Tests authentication against the SMTP server."""
    try:
        if port == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(host, port, context=context, timeout=15) as server:
                server.login(email_address, password)
        else:
            with smtplib.SMTP(host, port, timeout=15) as server:
                server.ehlo()
                server.starttls(context=ssl.create_default_context())
                server.ehlo()
                server.login(email_address, password)
        return True, "SMTP Authentication successful"
    except smtplib.SMTPAuthenticationError as e:
        return False, (
            "Authentication failed. If using Gmail, make sure you are using a 16-character "
            "App Password (not your normal account password). "
            f"Details: {e}"
        )
    except Exception as e:
        return False, f"SMTP Connection error: {str(e)}"

def send_email_with_attachment(
    sender_name: str,
    sender_email: str,
    password: str,
    recipient_email: str,
    subject: str,
    body_text: str,
    attachment_path: str | None,
    host: str,
    port: int
) -> tuple[bool, str]:
    """Sends a single cold email with optional attachment."""
    try:
        msg = MIMEMultipart()
        msg["From"] = f"{sender_name} <{sender_email}>"
        msg["To"] = recipient_email
        msg["Subject"] = subject

        # Attach text body
        msg.attach(MIMEText(body_text, "plain", "utf-8"))

        # Attach PDF Resume if present
        if attachment_path and os.path.exists(attachment_path):
            filename = os.path.basename(attachment_path)
            with open(attachment_path, "rb") as f:
                part = MIMEBase("application", "pdf")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{filename}"'
            )
            msg.attach(part)

        # Dispatch via SMTP
        if port == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(host, port, context=context, timeout=20) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, recipient_email, msg.as_string())
        else:
            with smtplib.SMTP(host, port, timeout=20) as server:
                server.ehlo()
                server.starttls(context=ssl.create_default_context())
                server.ehlo()
                server.login(sender_email, password)
                server.sendmail(sender_email, recipient_email, msg.as_string())

        return True, "Sent successfully"
    except Exception as e:
        return False, f"Failed to send: {str(e)}"

