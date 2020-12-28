from flask import Blueprint, jsonify

from firepot import messages
from firepot.utils import validate_auth_token, payload, status_message

from firepot.models import Product, Item

store_blueprint = Blueprint(__name__, "store_blueprint", url_prefix="/store")


@store_blueprint.route("/products", methods=['GET'])
@validate_auth_token
def store_products():
    """
    Return (in json to client) all the products in stock.
    """

    items_in_stock = Item.query.filter(Item.stock >= 1).all()

    if len(items_in_stock) == 0:
        return status_message(msg=messages.NO_STOCK_AVAILABLE, status="error")

    items_map = {}

    for item in items_in_stock:
        item_products = Product.query.filter_by(item_id=item.id).all()

        if len(item_products) == 0:
            continue

        for product in item_products:
            _product_map = product.to_dict()

            item_id = _product_map['item_id']

            if item_id not in items_map.keys():
                items_map[item_id] = product.get_item().to_dict()
                items_map[item_id]['products'] = list()  # Map of items.

            items_map[item_id]['products'].append(product.to_dict())

        return payload(msg="Store Products List", payload={
            'items': items_map
        })
