from flask import Blueprint, request, jsonify

from firepot.models import User
from firepot.utils import error_message, payload, encode_auth_token, decode_auth_token, validate_auth_token, \
    status_message
from firepot import messages

auth_blueprint = Blueprint(__name__, "auth", url_prefix="/auth")


@auth_blueprint.route('/', methods=['GET'])
@validate_auth_token
def index():
    return status_message(msg="Welcome")


@auth_blueprint.route("/login/", methods=['POST'])
def login():
    _json = request.get_json()

    email = _json['email']
    password = _json['password']

    if email is None:
        return error_message(messages.NO_EMAIL_PROVIDED)

    if password is None:
        return error_message(messages.NO_PASSWORD_PROVIDED)

    user = User.query.filter_by(email=email).first()

    if user is None:
        return error_message(messages.LOGIN_FAILED)

    if not user.check_password(password):
        # todo login log error log inform user of invalid login

        return error_message(messages.LOGIN_FAILED)

    try:
        authentication_token = encode_auth_token(user.id).decode("utf-8")
    except:
        authentication_token = encode_auth_token(user.id)

    return payload(messages.LOGIN_SUCCESS, {
        "id": user.id,
        "email": user.phone_number,
        "name": user.first_name,
        "auth": authentication_token,
        "admin": user.has_permission("firepot.admin")
    })


@auth_blueprint.route("/register/", methods=['POST'])
def register():
    _json = request.get_json()

    email = _json['email']
    first_name = _json['first_name']
    last_name = _json['last_name']
    password = _json['password']

    if email is None:
        return error_message(messages.NO_EMAIL_PROVIDED)

    if first_name is None or last_name is None:
        return error_message(messages.NO_NAME_PROVIDED)

    if password is None:
        return error_message(messages.NO_PASSWORD_PROVIDED)

    user = User.query.filter_by(email=email).first()

    if user is not None:
        return error_message(messages.EMAIL_ALREADY_CLAIMED)

    user = User(first_name=first_name, last_name=last_name, email=email, password=password)
    user.save(commit=True)

    try:
        authentication_token = encode_auth_token(user.id).decode("utf-8")
    except:
        authentication_token = encode_auth_token(user.id)

    return payload(messages.REGISTRATION_SUCCESSFUL, {
        'auth': authentication_token,
        'name': user.first_name,
        'id': user.id
    })
