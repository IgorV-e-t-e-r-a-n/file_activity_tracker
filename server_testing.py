import smtplib

EMAIL_HOST = "127.0.0.1"
EMAIL_PORT = 1025

try:
    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        print("Connected to SMTP server!")
        server.sendmail("test@localhost", "admin@example.com", "Test email body")
        print("Test email sent!")
except smtplib.SMTPException as e:
    print(f"Failed to send email: {e}")