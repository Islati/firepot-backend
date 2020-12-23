from flask import Blueprint

store_blueprint = Blueprint(__name__,"store_blueprint",url_prefix="/store")

@store_blueprint.route("/products",methods=['GET'])
def store_products():
    """
    Return (in json to client) all the products in stock.
    """

