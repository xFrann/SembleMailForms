import os.path

from app_config import get_from_rec_map, get_from_config


def parse_placeholders(text, body):
    placeholders = ["%name%", "%subject%", "%from%", "%message%"]
    config_placeholders = ["%friendly_name%"]

    for placeholder in config_placeholders:
        text = replace_if_exists(text, placeholder, get_from_rec_map(body['uuid'])[placeholder.strip("%")])

    for placeholder in placeholders:
        text = replace_if_exists(text, placeholder, body.get(placeholder.strip("%")))

    return text


def parse_unsubscribe(text, link):
    return replace_if_exists(text, "%unsubscribe_link%", link)


def replace_if_exists(original_string, to_replace, string):
    modified_string = original_string

    if string is None:
        modified_string = modified_string.replace(to_replace, "")
    elif string is not None and to_replace in original_string:
        modified_string = modified_string.replace(to_replace, string)

    return modified_string


def validate_body(post_body):
    mandatory_body_params = ['name', 'message', 'uuid']

    missing_params = False
    missing_parameters = []

    for key in mandatory_body_params:
        if key not in post_body:
            missing_params = True
            missing_parameters.append(key)

    if missing_params:
        raise ValueError(f"{', '.join(missing_parameters)} missing from the request body")


def log_ip(request):
    if get_from_config("logIp"):
        print(f"HTTP Request source IP: ${request.remote_addr}")


def get_template_as_string(template_name):
    root_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = root_dir[:-4]
    template_path = f"{root_dir}\\email_templates\\{template_name}\\{template_name}.html"
    template = open(template_path, 'r').read()
    return template
