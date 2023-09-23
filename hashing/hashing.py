from app_config import get_from_config
from hashlib import sha256
import re


def _get_secret_key():
    secret_key = get_from_config("secret_key")

    if secret_key is None:
        raise ValueError("Invalid or empty secret key in config.yml")

    return secret_key


def generate_hash(email, uuid):
    secret_key = _get_secret_key()

    if not email or not uuid:
        raise ValueError("Missing email or uuid, cannot generate hash!")

    string_to_hash = secret_key.join([email, uuid])
    string_to_hash = string_to_hash.encode()

    return sha256(string_to_hash)


def validate_hash(email, uuid, encoded_hash):
    if not email or not uuid:
        raise ValueError("Missing email or uuid, cannot decode hash!")

    if not re.match("^[a-fA-F0-9]{64}$", encoded_hash):
        raise ValueError("Hash is invalid.")

    generated_hash = generate_hash(email, uuid)

    if generated_hash.hexdigest() != encoded_hash:
        raise ValueError("Hash comparison failed, hash is invalid.")

    return True
