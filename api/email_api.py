import json

from flask import Flask, request, make_response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from api.cors_handler import add_headers_to_response
from api.api_utilities import parse_placeholders, validate_body, log_ip, get_template_as_string, parse_unsubscribe, check_required_field
from mail_server import send_mail
from app_config import get_email_ratelimit, get_recipients, get_subscription_ratelimit, get_friendly_name, \
    get_subject_format, is_uuid_valid, remove_recipient_from_website, get_host, get_port, get_from_rec_map
from hashing.hashing import generate_hash, validate_hash

api = Flask(__name__)
limiter = Limiter(app=api, key_func=get_remote_address)


@api.route("/email", methods=['POST', 'OPTIONS'])
@limiter.limit(get_email_ratelimit)
def post_mail():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")

        return response

    post_body = request.json

    log_ip(request)
    recipients = get_recipients(post_body['uuid'])
    try:
        validate_body(post_body)

        if not recipients:
            response = make_response(json.dumps({"error": "UUID Is invalid or no recipients found server side"}), 400)
            add_headers_to_response(response)
            return response

        required_fields = get_from_rec_map(post_body['uuid'])['required_fields']
        required_missing = check_required_field(required_fields, post_body)

        if required_missing:
            error_response = "Required field missing: "
            for missing_field in required_missing:
                error_response += missing_field
            response = make_response(json.dumps({"error": error_response}), 400)
            add_headers_to_response(response)
            return response



    except ValueError as error:
        response = make_response(json.dumps({"error": error.args[0]}), 400)
        add_headers_to_response(response)
        return response

    print(f"Received POST Request with data: {post_body}")
    email_subject = parse_placeholders(get_subject_format(post_body['uuid']), post_body)
    failures = 0

    template_name = "default"
    template_name_from_config = get_from_rec_map(uuid=post_body["uuid"], key="template")

    if template_name_from_config is not None:
        template_name = template_name_from_config

    html_message = get_template_as_string(template_name)
    html_parsed_message = parse_placeholders(html_message, post_body)

    for recipient in recipients:
        html_parsed_message = parse_unsubscribe(html_parsed_message,
                                                str(generate_unsubscribe_link(recipient, post_body['uuid'])))
        print(
            f"Received Post Request to send email with the following parameters [recipient: {recipient}] [subject: {email_subject}]")
        mail_sent = send_mail(recipient, email_subject, html_parsed_message)
        if not mail_sent:
            failures += 1

    response = make_response(
        {"success": "Email was sent to recipients, failed to send to (" + str(failures) + ") recipients"}, 200)
    add_headers_to_response(response)

    return response


@api.route("/subscription", methods=['POST', 'OPTIONS'])
@limiter.limit(get_subscription_ratelimit)
def unsubscribe():
    post_body = request.json
    log_ip(request)
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
