from flask import Blueprint, jsonify
from firepot.utils import validate_auth_token, payload, status_message

from firepot.models import Product

store_blueprint = Blueprint(__name__, "store_blueprint", url_prefix="/store")


@store_blueprint.route("/products", methods=['GET'])
@validate_auth_token
def store_products():
    """
    Return (in json to client) all the products in stock.
    """

    products = Product.query.filter(Product.stock >= 1).all()

    if len(products) == 0:
        return status_message(msg="Currently no stock available")

    items_map = {}

    for product in products:
        if product.stock < 1:
            continue

        _product_map = product.to_dict()

        item_id = _product_map['item_id']

        if item_id not in items_map.keys():
            items_map[item_id] = product.get_item().to_dict()
            items_map[item_id]['products'] = list()  # Map of items.

        items_map[item_id]['products'].append(product.to_dict())

    return payload(msg="Store Products List", payload={
        'items': items_map
    })
