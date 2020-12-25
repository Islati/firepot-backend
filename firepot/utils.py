import datetime
import logging

import jwt
from flask import jsonify, request

from functools import wraps

import random
import math

from firepot.config import Config
from firepot.models import User

import base64

LOGGER = logging.getLogger(__name__)

def base64_encode_image(input):
    image_string = base64.b64encode(input.read())
    return image_string

def payload(msg, payload, status="success"):
    return jsonify({
        "status": status,
        "message": msg,
        "payload": payload
    })


def error_message(msg):
    return status_message(msg, status="error")


def status_message(msg, status="success"):
    return jsonify({
        'status': status,
        'message': msg
    })


def is_validated_user_request(request):
    """
    Checks whether or not the request passed is a validated user request by comparing the Authorization Header.
    :param request: request to check
    :return:
    """

    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return False

    # Split after 'Bearer '

    if ' ' not in auth_header:
        return False

    token = auth_header.split(' ')[1]

    if token == Config.DEBUG_USER_AUTHORIZATION_BEARER or token == Config.DEBUG_ADMIN_AUTHORIZATION_BEARER:
        return True

    payload = decode_auth_token(token)

    if payload is False:  # If we has no payload.
        return False

    return True


def admins_only(api_method):
    """
    Decorator to validate authentication token
    :param api_method:
    :return:
    """

    @wraps(api_method)
    @validate_auth_token
    def decorated_method(*args, **kwargs):
        user = get_user(request)

        if user is None:
            LOGGER.debug("Admin Only:: Unable to verify user")
            return jsonify({
                'status': 'error',
                'message': 'Unable to identify user'
            }), 401

        if not user.has_permission('firepot.administration'):
            LOGGER.debug("Admin Only:: Insufficient Permissions")
            return jsonify({
                'status': 'error',
                'message': 'Admin permissions required'
            }), 401

        return api_method(*args, **kwargs)

    return decorated_method


def validate_auth_token(api_method):
    """
    Decorator to validate authentication token
    :param api_method:
    :return:
    """

    @wraps(api_method)
    def decorated_method(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if auth_header is None:
            LOGGER.debug("Validate Auth Token:: Unable to locate authorization header")
            return jsonify({
                'status': 'error',
                'message': "Unable to locate authorization header"
            }), 401

        if ' ' not in auth_header:
            LOGGER.debug("Validate Auth Token: Invalid Authorization token")
            return jsonify({
                'status': 'error',
                'message': 'Invalid auth token'
            })

        # Split after 'Bearer '
        token = auth_header.split(' ')[1]

        LOGGER.debug(f'Authentication Token is {token}')

        if token == Config.DEBUG_ADMIN_AUTHORIZATION_BEARER or token == Config.DEBUG_USER_AUTHORIZATION_BEARER:
            return api_method(*args, **kwargs)

        payload = decode_auth_token(token)

        if payload is False:
            LOGGER.debug("Validate Auth Token: Expired Session")
            return jsonify({
                'status': 'error',
                'message': 'Expired session'
            }), 401

        return api_method(*args, **kwargs)

    return decorated_method


def encode_auth_token(user_id):
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id,
        }
        token = jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
        return token
    except Exception as e:
        print(e)
        return e


def decode_auth_token(token):
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        # todo handle expired signature
        pass
    except jwt.InvalidTokenError:
        # todo invalid token error
        pass

    return False


def get_auth_token(request):
    """
    Retrieve an authorization bearer token if present inside the request headers
    :param request: flask request object
    :return: jwt token (serialized) if available in request headers
    """

    auth_header = request.headers.get('Authorization')

    if not auth_header or ' ' not in auth_header:
        return None

    token = auth_header.split(' ')[1]

    return token


def get_user(request):
    """
    Helper method to retrieve a user based on the auth token passed via request headers
    :param request: request to retrieve the user object for
    :return: User or None
    """

    uid = get_user_id(request)

    if uid is None:
        return None

    user = User.query.filter_by(id=get_user_id(request)).first()

    return user


def get_user_id(request):
    """
    Retrieve a user id from decoding the authorization header payload and retrieving it.
    :param request: flask request object
    :return: user id if present.
    """

    value = None

    token = get_auth_token(request)

    if token == Config.DEBUG_USER_AUTHORIZATION_BEARER:
        debug_user = User.query.filter_by(email="testuser@firepot.ca").first()

        if debug_user is None:
            debug_user = User(name="Test User", password="testuserfirepot", email="testuser@firepot.ca")
            debug_user.save(commit=True)
            print("Created Test User for Firepot Debugging")

        return User.query.filter_by(email='testuser@firepot.ca').first().id

    if token == Config.DEBUG_ADMIN_AUTHORIZATION_BEARER:
        admin_user = User.query.filter_by(email="testadmin@firepot.ca").first()
        if admin_user is None:
            admin_user = User(name="Test Admin", password="testadminfirepotca", email="testadmin@firepot.ca")
            admin_user.save(commit=True)
            print("Created Test Admin for FirePot Debugging")

        return User.query.filter_by(email="testadmin@firepot.ca").first().id

    try:
        value = decode_auth_token(get_auth_token(request))['sub']
    except:  # todo logging
        pass

    return value


def json_only(api_method):
    """
    Decorator to only allow json payloads to be submitted with the request
    :param api_method:
    :return:
    """

    @wraps(api_method)
    def decorated_method(*args, **kwargs):
        if not request.is_json:
            LOGGER.warning("Request was not provided a json payload")
            return jsonify({
                'status': 'error',
                'message': "Request was not provided a json payload"
            })

        return api_method(*args, **kwargs)

    return decorated_method
