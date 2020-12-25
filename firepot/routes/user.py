from flask import Blueprint
from firepot.models import User

user_blueprint = Blueprint(__name__, "user", "/user")

@user_blueprint.route('/orders', methods=['GET'])
def user_orders_list():
    pass

