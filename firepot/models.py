from uuid import uuid4

from firepot.database import SurrogatePK, SqlModel, Column, relationship
from firepot.extensions import db, hashing

import logging

LOGGER = logging.getLogger(__name__)

class SetupRecord(SurrogatePK, SqlModel):
    __tablename__ = "firepot_setup"

    status = db.Column(db.Text, default="incomplete")

    def __init__(self, status):
        super().__init__(
            status=status
        )


class OrderItem(SurrogatePK, SqlModel):
    __tablename__ = "order_items"

    order_id = db.Column(db.Integer, db.ForeignKey("order.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))

    name = db.Column(db.Text)

    amount = db.Column(db.Integer)

    price = db.Column(db.Integer)

    def __init__(self, order_id, product_id, name, amount, price):
        super().__init__(
            order_id=order_id,
            product_id=product_id,
            name=name,
            amount=amount,
            price=price
        )


class Order(SurrogatePK, SqlModel):
    __tablename__ = "order"

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    items = relationship("OrderItem", backref=db.backref('order'), uselist=True, lazy=True)

    def __init__(self, user_id):
        super().__init__(
            user_id=user_id,
        )

    def add_item(self, cart_item):
        self.items.append(
            OrderItem(self.id, cart_item.product_id, f'{cart_item.product.item.name} {cart_item.product.name}',
                      cart_item.amount, cart_item.product.get_cost())
        )


class CartItem(SqlModel):
    """
    Users cart is not an object but an array of CartItem that gets moved
    to an order when sold.
    """
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), primary_key=True)

    amount = db.Column(db.Integer, nullable=False, default=1)

    user = relationship("User", back_populates="cart_items", uselist=False)
    product = relationship("Product", backref=db.backref("carts"), uselist=False)

    def __init__(self, user_id, product_id, amount=1):
        super().__init__(user_id=user_id, product_id=product_id, amount=amount)

    def to_dict(self):
        return dict(
            user_id=self.user_id,
            product_id=self.product_id,
            amount=self.amount
        )


class Image(SurrogatePK, SqlModel):
    """
    Images are used on items for display.
    """
    __tablename__ = "image"

    name = db.Column(db.Text, unique=True)
    data = db.Column(db.Text)

    item_id = db.Column(db.Integer, db.ForeignKey("item.id"))

    def __init__(self, name, data):
        super().__init__(
            name=name,
            data=data
        )

    def to_dict(self):
        return dict(
            name=self.name,
            data=self.data
        )


class Product(SurrogatePK, SqlModel):
    """
    Parent class to item that holds individual sale item,
    and is grouped together in retrieving to create inventory catalog.
    """
    __tablename__ = "products"

    name = db.Column(db.Text, nullable=False)

    item_id = db.Column(db.Integer, db.ForeignKey("item.id"))
    item = relationship("Item", uselist=False)

    cost = db.Column(db.Integer, nullable=False)
    sale_cost = db.Column(db.Integer, nullable=True, default=0)

    stock_weight = db.Column(db.Integer, nullable=False, default=1)

    def __init__(self, name, item_id, cost, sale_cost=0, stock_weight=1):
        super().__init__(
            name=name,
            item_id=item_id,
            cost=cost,
            sale_cost=sale_cost,
            stock_weight=stock_weight
        )

    def to_dict(self):
        return dict(
            name=self.name,
            item_id=self.item_id,
            cost=self.cost,
            sale_cost=self.sale_cost,
            stock_weight=self.stock_weight
        )

    def get_item(self):
        return Item.query.filter_by(id=self.item_id).first()

    def get_cost(self):
        """
        Returns the lowest number of the two defined cost values for this.
        :return:
        """
        return self.sale_cost if 0 < self.sale_cost < self.cost else self.cost


item_tags_table = db.Table(
    'item_tags',
    db.Column('item_id', db.Integer, db.ForeignKey('item.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'))
)


class Item(SurrogatePK, SqlModel):
    """
    Items are the stock of the website.
    """
    __tablename__ = "item"

    name = db.Column(db.Text)
    description = db.Column(db.Text)

    cover_image_id = db.Column(db.Integer, nullable=True, default=-1)
    images = relationship("Image", backref=db.backref('item', cascade="all,delete"), lazy=True, uselist=True)
    tags = relationship('Tag', backref=db.backref("tag", lazy="joined"), lazy=True, uselist=True,
                        secondary=item_tags_table)

    stock = db.Column(db.Integer, nullable=True, default=0)

    products = relationship("Product", back_populates="item", lazy="dynamic", uselist=True)

    def __init__(self, name, description, cover_image_id, images, tags, stock=1):
        super().__init__(
            name=name,
            description=description,
            cover_image_id=cover_image_id,
            images=images,
            tags=tags,
            stock=stock
        )

    def to_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            description=self.description,
            cover_image_id=self.cover_image_id,
            images=[img.to_dict() for img in self.images],
            tags=[tag.to_dict() for tag in self.tags]
        )


class Tag(SurrogatePK, SqlModel):
    __tablename__ = "tags"

    name = db.Column(db.Text, unique=True)

    items = relationship('Item', secondary=item_tags_table, back_populates="tags")

    def __init__(self, name):
        super(). \
            __init__(name=name)

    def to_dict(self):
        return dict(
            id=self.id,
            name=self.name
        )


class UserPermission(SqlModel):
    """
    Handles the link between users and permissions
    Each entry here is one link for the user.
    """
    __tablename__ = "user_permissions"

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    permission_id = db.Column(db.Integer, db.ForeignKey("permission.id"), primary_key=True)

    user = relationship("User", back_populates="permissions")
    permission = relationship("Permission", back_populates="users")

    def __init__(self, user, permission):
        super().__init__(
            user_id=user.id,
            permission_id=permission.id
        )


class Permission(SurrogatePK, SqlModel):
    """
    Permission nodes which are used to determine permission
    """
    __tablename__ = "permission"

    node = Column(db.Text, unique=True)

    users = relationship("UserPermission", back_populates="permission")

    def __init__(self, node):
        super().__init__(
            node=node
        )


class User(SurrogatePK, SqlModel):
    """
    User of the website.
    """
    __tablename__ = "user"

    permissions = relationship("UserPermission", back_populates="user")

    cart_items = relationship("CartItem", back_populates="user", uselist=True)

    orders = relationship("Order", backref=db.backref("user"), uselist=True)

    salt_code = Column(db.Text, nullable=False)  # generated on model creation

    first_name = Column(db.Text, nullable=False)  # Users name - used for display, and when greeting them.
    last_name = Column(db.Text, nullable=False)  # Users name - used for display, and when greeting them.

    email = Column(db.Text, nullable=False, unique=True)
    phone_number = Column(db.Text, nullable=False, unique=True)
    password = Column(db.Text, nullable=False)

    birth_date = Column(db.DateTime,nullable=False)

    def __init__(self, first_name, last_name, email, phone_number, password,birth_date):
        salt_code = str(uuid4()).strip('-')  # generated saltcode
        hashed_password = hashing.hash_value(password, salt_code)

        super().__init__(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            password=hashed_password,
            salt_code=salt_code,
            birth_date=birth_date
        )

    def set_password(self, password):
        self.password = hashing.hash_value(password, self.salt_code)

    def check_password(self, password):
        return hashing.check_value(self.password, password, self.salt_code)

    def has_permission(self, node):

        perm_node = Permission.query.filter_by(node=node).first()

        if perm_node is None:
            LOGGER.debug("unable to locate requested node {0}".format(node))
            return False

        user_node = UserPermission.query.filter_by(user_id=self.id, permission_id=perm_node.id).first()

        if user_node is None:
            LOGGER.debug("User doesn't have node {0}".format(node))
            return False

        return True

    def add_permission(self, node):
        perm_node = Permission.query.filter_by(node=node).first()

        if perm_node is None:
            perm_node = Permission(node=node)
            perm_node.save(commit=True)

        new_user_perm = UserPermission(user=self, permission=perm_node)
        new_user_perm.save(commit=True)

        self.save(commit=True)

        return self.has_permission(node)

    def save_cart_as_order(self):
        order = Order(self.id)

        for cart_item in self.cart_items:
            order.add_item(cart_item)
            cart_item.delete()

        order.save(commit=True)

        self.save(commit=True)
