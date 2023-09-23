import smtplib
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import getpass
from app_config import get_mail_host, get_mail_port, get_mail_username
mail_server: SMTP
email_password: str


def connect(reconnect: bool):
    global mail_server
    global email_password
    print("Connecting to SMTP server...")
    mail_server = smtplib.SMTP(get_mail_host(), get_mail_port())
    print("Connected!")
    mail_server.ehlo()
    mail_server.starttls()
    if not reconnect:
        email_password = getpass.getpass(prompt="Please insert mail account password ({}): ".format(get_mail_username()))
    mail_server.login(get_mail_username(), email_password)


def send_mail(recipient, subject, content):
    from_mail = get_mail_username()

    msg = MIMEMultipart()
    msg['From'] = from_mail
    msg['To'] = recipient
    msg['Subject'] = subject
    message = content
    msg.attach(MIMEText(message))
    try:
        mail_server.sendmail(from_mail, recipient, msg.as_string())
    except smtplib.SMTPSenderRefused as e:
        print("SMTP Connection has timed out... reconnecting")
        connect(True)
    print(f"Email was sent to {recipient}")
    mail_server.quit()
