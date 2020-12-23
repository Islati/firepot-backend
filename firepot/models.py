from uuid import uuid4

from firepot.database import SurrogatePK, SqlModel, Column, relationship
from firepot.extensions import db, hashing


class Image(SurrogatePK, SqlModel):
    __tablename__ = "image"

    name = db.Column(db.Text, unique=True)
    data = db.Column(db.Text)

    item_id = db.Column(db.Integer, db.ForeignKey("item.id"))

    def __init__(self, name, data):
        super().__init__(
            name=name,
            data=data
        )


class Product(SurrogatePK, SqlModel):
    __tablename__ = "products"

    name = db.Column(db.Text, nullable=False)

    item_id = db.Column(db.Integer, db.ForeignKey("item.id"))

    cost = db.Column(db.Integer, nullable=False)
    sale_cost = db.Column(db.Integer, nullable=True, default=0)

    stock = db.Column(db.Integer,nullable=True,default=0)

    def __init__(self, name, item_id, cost, sale_cost=0,stock=0):
        super().__init__(
            name=name,
            item_id=item_id,
            cost=cost,
            sale_cost=sale_cost,
            stock=stock
        )


item_tags_table = db.Table(
    'item_tags',
    db.Column('item_id', db.Integer, db.ForeignKey('item.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'))
)


class Item(SurrogatePK, SqlModel):
    __tablename__ = "item"

    name = db.Column(db.Text)
    description = db.Column(db.Text)

    cover_image_id = db.Column(db.Integer, nullable=True, default=-1)
    images = relationship("Image", backref=db.backref('item', cascade="all,delete"), lazy=True, uselist=True)
    tags = relationship('Tag', backref=db.backref("tag", lazy="joined"), lazy=True, uselist=True,
                        secondary=item_tags_table)

    def __init__(self, name, description, cover_image_id, images, tags):
        super().__init__(
            name=name,
            description=description,
            cover_image_id=cover_image_id,
            images=images,
            tags=tags
        )


class Tag(SurrogatePK, SqlModel):
    __tablename__ = "tags"

    name = db.Column(db.Text, unique=True)

    items = relationship('Item', secondary=item_tags_table, back_populates="tags")

    def __init__(self, name):
        super().__init__(name=name)


class UserPermissions(SurrogatePK, SqlModel):
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
            user=user,
            permission=permission
        )


class Permission(SurrogatePK, SqlModel):
    """
    Permission nodes which are used to determine permission
    """
    __tablename__ = "permission"

    node = Column(db.Text, unique=True)

    users = relationship("UserPermissions", back_populates="permission")

    def __init__(self, node):
        super().__init__(
            node=node
        )


class User(SurrogatePK, SqlModel):
    """
    User of the website.
    """
    __tablename__ = "user"

    permissions = relationship("UserPermissions", back_populates="user")

    salt_code = Column(db.Text, nullable=False)  # generated on model creation

    first_name = Column(db.Text, nullable=False)  # Users name - used for display, and when greeting them.
    last_name = Column(db.Text, nullable=False)  # Users name - used for display, and when greeting them.

    email = Column(db.Text, nullable=False, unique=True)
    password = Column(db.Text, nullable=False)

    def __init__(self, first_name, last_name, email, password):
        salt_code = str(uuid4()).strip('-')  # generated saltcode
        hashed_password = hashing.hash_value(password, salt_code)

        super().__init__(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_password,
            salt_code=salt_code
        )

    def set_password(self, password):
        self.password = hashing.hash_value(password, self.salt_code)

    def check_password(self, password):
        return hashing.check_value(self.password, password, self.salt_code)
