from flask import Blueprint, request
from flask_cors import cross_origin

from firepot import messages
from firepot.models import Item, Product, Tag, Image
from firepot.utils import status_message, payload, admins_only

admin_blueprint = Blueprint(__name__, "admin", url_prefix="/admin")


@admin_blueprint.route('/')
@admins_only
def index():
    return status_message(msg="Welcome")


@admins_only
@admin_blueprint.route('/inventory/delete/', methods=['POST'])
def delete_item():
    _json = request.get_json()

    item_id = _json['id']

    item = Item.query.filter_by(id=int(item_id)).first()

    if item is None:
        return status_message(msg="Unable to find item with id {0}".format(item_id), status="error")

    item.delete(commit=True)
    return payload(msg="Item Deleted", payload={})

@admin_blueprint.route('/images/save', methods=['POST'])
@admins_only
def images_save():
    _json = request.get_json()

    name = _json['name']
    data = _json['data']

    image = Image.query.filter_by(name=name).first()

    if image is not None:
        return status_message(messages.DUPLICATE_IMAGE_NAME, status="error")

    # todo verify it's base64 image data somewhere here.

    image = Image(name=name, data=data)
    image.save(commit=True)

    return payload("Image saved", payload=dict(image_id=image.id))


@admin_blueprint.route('/inventory/list/', methods=['GET'])
@admins_only
def list_inventory_items():
    _json = request.get_json()

    items = Item.query.all()

    item_data = []

    for item in items:
        item_data.append(item.to_dict())

    return payload(msg="Inventory Listings", payload=item_data)


@admin_blueprint.route('/inventory/new/', methods=['POST'])
@admins_only
def new_inventory_item():
    _json = request.get_json()

    name = _json['name']
    description = _json['description']
    cover_image_name = _json['cover_image_name']
    cover_image_data = _json['cover_image_data']

    stock = _json['stock']

    tags_list = _json['tags'].split(',')

    products = _json['products']

    item = Item.query.filter_by(name=name).first()

    if item is not None:
        return status_message(messages.DUPLICATE_ITEM_NAME, status='error')

    item_image = Image.query.filter_by(name=name).first()

    if item_image is not None:
        return status_message(messages.DUPLICATE_IMAGE_NAME, status='error')

    tags = []

    for tag in tags_list:
        _tag = Tag.query.filter_by(name=tag).first()

        if _tag is None:
            _tag = Tag(name=tag)
            _tag.save(commit=True)

        tags.append(_tag)

    # todo secure image data

    # todo secure description

    item_image = Image(name=cover_image_name, data=cover_image_data)
    item_image.save(commit=True)

    item = Item(name=name, description=description, cover_image_id=item_image.id, images=[item_image], tags=tags,
                stock=int(stock))
    item.save(commit=True)

    for product in products:
        item_product = Product(name=product['name'], item_id=item.id, cost=int(product['cost']),
                               sale_cost=int(product['cost']),
                               stock_weight=float(product['stock_weight']))
        item_product.save(commit=True)

    return payload(msg=messages.ITEM_CREATED, payload={
        'item': item.to_dict()
    })


@admin_blueprint.route('/inventory/product/new/', methods=['POST'])
@admins_only
def new_inventory_item_product():
    _json = request.get_json()

    item_id = _json['item_id']
    name = _json['name']
    cost = _json['cost']
    sale_cost = _json['sale_cost']
    stock_weight = _json['stock_weight']

    item = Item.get_by_id(item_id)

    if item is None:
        return status_message(msg=messages.INVALID_ITEM_ID, status="error")

    product = Product.query.filter_by(name=name).first()
    if product is not None:
        return status_message(msg=messages.DUPLICATE_PRODUCT_NAME.format(name), status="error")

    product = Product(name=name, item_id=item_id, cost=cost, sale_cost=sale_cost, stock_weight=stock_weight)
    product.save(commit=True)

    return payload(msg=messages.PRODUCT_CREATED, payload={'product': product.to_dict()})


@admin_blueprint.route("/inventory/edit", methods=['POST'])
def edit_inventory_item():
    pass
