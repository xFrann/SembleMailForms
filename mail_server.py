import smtplib
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import getpass
from app_config import get_mail_host, get_mail_port, get_mail_username
email_password: str


def connect(reconnect: bool):
    global email_password
    print("Connecting to SMTP server...")
    mail_server = smtplib.SMTP(get_mail_host(), get_mail_port())
    print("Connected!")
    mail_server.ehlo()
    mail_server.starttls()
    if not reconnect:
        email_password = getpass.getpass(prompt="Please insert mail account password ({}): ".format(get_mail_username()))
    mail_server.login(get_mail_username(), email_password)
    return mail_server


def send_mail(recipient, subject, content):

    success = False
    mail_server = connect(False) if email_password is None else connect(True)

    from_mail = get_mail_username()
    msg = MIMEMultipart()
    msg['From'] = from_mail
    msg['To'] = recipient
    msg['Subject'] = subject
    message = content
    msg.attach(MIMEText(message))

    try:
        print(f"Sending mail: [from: {from_mail}, recipient: {recipient}]")
        mail_server.sendmail(from_mail, recipient, msg.as_string())
        success = True
    except smtplib.SMTPException as e:
        print(f"Exception while trying to send email {e.strerror}")
        return success

    if success:
        print(f"Email was sent to {recipient}")
    else:
        print(f"FAILURE TO SEND EMAIL TO {recipient}")

    mail_server.quit()
    return success
