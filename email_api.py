import json

from flask import Flask, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from mail_server import send_mail
from app_config import get_email_ratelimit
api = Flask(__name__)
limiter = Limiter(app=api, key_func=get_remote_address)


@api.route("/email", methods=['POST'])
@limiter.limit(get_email_ratelimit)
def post_mail():
    post_body = request.json
    print("Received POST Request with data: {}".format(post_body))
    send_mail("contact@frann.dev", "Website mail - {}".format(post_body['name']), str(post_body['message']))
    return json.dumps({"success": "Email was sent successfully to recipients"})
