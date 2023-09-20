import yaml

config: dict
recipient_map: dict


def load_config():
    global config
    global recipient_map
    recipient_map = _read_yaml("configs/recipient_map.yml")
    config = _read_yaml("configs/config.yml")
    print("Loaded configuration file")


def _read_yaml(path):
    stream = open(path, 'r')
    yaml_data = yaml.safe_load(stream)
    stream.close()
    return yaml_data


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


def get_recipients(uuid):
    if uuid in recipient_map:
        return recipient_map[uuid]
    else:
        return []
