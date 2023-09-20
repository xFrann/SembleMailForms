import mail_server
from app_config import load_config, get_host, get_port
from email_api import api


def run_app():
    load_config()
    mail_server.connect()
    api.run(host=get_host(), port=get_port())


if __name__ == '__main__':
    run_app()
