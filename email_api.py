import json

from flask import Flask, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from mail_server import send_mail
from app_config import get_email_ratelimit, get_recipients, get_subscription_ratelimit, get_friendly_name, \
    get_from_rec_map, get_subject_format

api = Flask(__name__)
limiter = Limiter(app=api, key_func=get_remote_address)


@api.route("/email", methods=['POST'])
@limiter.limit(get_email_ratelimit)
def post_mail():
    post_body = request.json

    recipients = get_recipients(post_body['uuid'])

    try:
        validate_body(post_body)

        if not recipients:
            return json.dumps({"error": "UUID Is invalid or no recipients found server side"}), 400

    except ValueError as error:
        return json.dumps({"error": error.args[0]}), 400

    print(f"Received POST Request with data: {post_body}")
    email_subject = parse_subject_placeholders(get_subject_format(post_body['uuid']), post_body)
    send_mail(recipients, email_subject, str(post_body['message']))
    return json.dumps({"success": "Email was sent successfully to recipients"}), 200


def parse_subject_placeholders(subject, body):
    placeholders = ["%name%", "%subject%"]
    config_placeholders = ["%friendly_name%"]

    for placeholder in config_placeholders:
        subject = replace_if_exists(subject, placeholder, get_from_rec_map(body['uuid'])[placeholder.strip("%")])

    for placeholder in placeholders:
        subject = replace_if_exists(subject, placeholder, body.get(placeholder.strip("%")))

    return subject


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
