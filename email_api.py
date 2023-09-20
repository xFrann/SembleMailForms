import json

from flask import Flask, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from mail_server import send_mail
from app_config import get_email_ratelimit, get_recipients

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
            return json.dumps({"error": "UUID Is invalid or no recipients found server side"})

    except ValueError as error:
        return json.dumps({"error": error.args[0]})

    print(f"Received POST Request with data: {post_body}")
    send_mail(recipients, f"Website mail - {post_body['name']}", str(post_body['message']))
    return json.dumps({"success": "Email was sent successfully to recipients"})


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
