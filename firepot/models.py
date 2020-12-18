from uuid import uuid4

from firepot.database import SurrogatePK, SqlModel, Column, relationship
from firepot.extensions import db, hashing


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
        hashed_password = hashing.hash_value(password, salt=self.salt_code)

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
