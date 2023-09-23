import json

from flask import Flask, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from mail_server import send_mail
from app_config import get_email_ratelimit, get_recipients, get_subscription_ratelimit, get_friendly_name, \
    get_from_rec_map, get_subject_format, is_uuid_valid, remove_recipient_from_website, get_host, get_port
from hashing.hashing import generate_hash, validate_hash

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
    for recipient in recipients:
        message = str(post_body['message']) + "\n unsubscribe:" + str(generate_unsubscribe_link(recipient, post_body['uuid']))
        send_mail(recipient, email_subject, message)

    return json.dumps({"success": "Email was sent successfully to recipients"}), 200


@api.route("/subscription", methods=['POST'])
@limiter.limit(get_subscription_ratelimit)
def unsubscribe():
    post_body = request.json

    email = post_body.get("email")
    uuid = post_body.get("uuid")
    posted_hash = post_body.get("hash")

    if uuid is None:
        return json.dumps({"error": "UUID body parameter is missing"}), 400

    if not is_uuid_valid(uuid):
        return json.dumps({"error": "UUID Is invalid"}), 400

    recipients = get_recipients(uuid)

    if not recipients:
        return json.dumps({"error": "No recipients found server side with the provided id"}), 400

    hash_valid = validate_hash(email, uuid, posted_hash)

    if not hash_valid:
        return json.dumps({"error": "Not able to unsubscribe, user does not receive mails from this website"}), 400

    remove_recipient_from_website(email, uuid)
    friendly_name = get_friendly_name(uuid)
    return json.dumps({"success": f"Your email ({email}) has been unsubscribed from {friendly_name}\'s website."}), 200


def generate_unsubscribe_link(email, uuid):
    hashed_values = generate_hash(email, uuid)
    print(f"Hash for {email} from {get_friendly_name(uuid)} is: {hashed_values.hexdigest()}")
    return f"http://{get_host()}:{get_port()}/unsubscribe?email={email}&uuid={uuid}&hash={hashed_values.hexdigest()}"


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
