import yaml

config: dict


def load_config():
    file_stream = open("configs/config.yml", 'r')
    global config
    config = yaml.safe_load(file_stream)
    print("Loaded configuration file")


def get_host():
    return config['host']


def get_port():
    return config['port']


def get_mail_host():
    return config['mail_host']


def get_mail_port():
    return config['mail_port']


def get_mail_username():
    return config['mail_username']


def get_email_ratelimit():
    return config["email_ratelimit"]
