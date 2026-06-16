import os
import smtplib
from email.message import EmailMessage

from flask import current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

RESET_SALT = 'password-reset'


def _serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt=RESET_SALT)


def generate_reset_token(email):
    """Signed, self-contained token — no DB column needed."""
    return _serializer().dumps(email)


def verify_reset_token(token, max_age=3600):
    """Return the email if the token is valid and unexpired, else None."""
    try:
        return _serializer().loads(token, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None


def send_email(to, subject, text_body, html_body=None):
    """Send via SMTP using env-var config. Returns True on success.

    Required env vars: SMTP_USER, SMTP_PASSWORD (a Gmail App Password).
    Optional: SMTP_HOST (default smtp.gmail.com), SMTP_PORT (default 587),
    SMTP_FROM (defaults to SMTP_USER).
    If unconfigured, logs the message and returns False so the flow still works
    in dev/testing.
    """
    host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
    port = int(os.environ.get('SMTP_PORT', '587'))
    user = os.environ.get('SMTP_USER')
    password = os.environ.get('SMTP_PASSWORD')
    sender = os.environ.get('SMTP_FROM', user)

    if not user or not password:
        print(f"[email] SMTP not configured — would send to {to}: {subject}")
        print(f"[email] body:\n{text_body}")
        return False

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to
    msg.set_content(text_body)
    if html_body:
        msg.add_alternative(html_body, subtype='html')

    try:
        with smtplib.SMTP(host, port, timeout=20) as server:
            server.starttls()
            server.login(user, password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"[email] send failed: {e}")
        return False
