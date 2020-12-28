from flask import Blueprint, request

from firepot.models import Item, Product, Tag, Image
from firepot.utils import status_message, payload, admins_only

admin_blueprint = Blueprint(__name__, "admin", url_prefix="/admin")


@admin_blueprint.route('/')
@admins_only
def index():
    return status_message(msg="Welcome")


@admin_blueprint.route('/images/save', methods=['POST'])
@admins_only
def images_save():
    _json = request.get_json()

    name = _json['name']
    data = _json['data']

    image = Image.query.filter_by(name=name).first()

    if image is not None:
        return status_message("An image with that name already exists", status="error")

    # todo verify it's base64 image data somewhere here.

    image = Image(name=name, data=data)
    image.save(commit=True)

    return payload("Image saved", payload=dict(image_id=image.id))


@admin_blueprint.route('/inventory/new/', methods=['POST'])
@admins_only
def new_inventory_item():
    _json = request.get_json()

    name = _json['name']
    description = _json['description']
    cover_image_name = _json['cover_image_name']
    cover_image_data = _json['cover_image_data']

    tags_list = _json['tags'].split(',')

    item = Item.query.filter_by(name=name).first()

    if item is not None:
        return status_message('An item with this name already exists', status='error')

    item_image = Image.query.filter_by(name=name).first()

    if item_image is not None:
        return status_message('An image with that name already exists', status='error')

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

    item = Item(name=name, description=description, cover_image_id=item_image.id, images=[item_image], tags=tags)
    item.save(commit=True)

    return payload(msg="Item created", payload={
        'item': item.to_dict()
    })


@admin_blueprint.route('/inventory/product/new', methods=['POST'])
def new_inventory_item_product():
    pass


@admin_blueprint.route("/inventory/edit", methods=['POST'])
def edit_inventory_item():
    pass
