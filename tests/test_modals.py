from tests import TestCase


class TestModels(TestCase):

    def _create_user(self, first_name, last_name, password, email):
        from firepot.models import User
        from firepot.extensions import hashing

        user_1 = User(first_name=first_name, last_name=last_name, email=email, password=password)
        user_1.save(commit=True)

        user = User.query.filter_by(email=email).first()

        self.assertIsNotNone(user)

        hashe = hashing.hash_value(password, salt=user.salt_code)

        self.assertIsNotNone(hashing.check_value(hashe, password, user.salt_code))

        return user_1

    def test_user_creation(self):
        from firepot.models import User
        user = self._create_user(first_name="Brandon", last_name="Curtis", password="testing", email="test@test.com")

        self.assertIsNotNone(user)

        user_again = User.query.filter_by(first_name="Brandon").first()

        self.assertIsNotNone(user_again)

    def test_user_permissions(self):
        from firepot.models import User, UserPermission, Permission

        user = self._create_user(first_name="b", last_name="c", password="testing", email="test@firepot.ca")

        self.assertIsNotNone(user)

        permission = Permission(node="firepot.administration")
        permission.save(commit=True)

        self.assertIsNotNone(Permission.query.filter_by(node="firepot.administration").first())

        user_perm = UserPermission(user=user, permission=permission)
        user_perm.save(commit=True)

        # user.add_permission("firepot.administration")
        self.assertTrue(user.has_permission("firepot.administration"))

    def test_item_and_product_creation(self):
        from firepot.models import Item, Image, Tag, Product

        item_image = Image(name="silver_haze_1", data="test_data")
        item_image.save(commit=True)

        item_image_search = Image.query.filter_by(name="silver_haze_1").first()
        self.assertIsNotNone(item_image_search)

        hybrid_tag = Tag(name="Hybrid")
        hybrid_tag.save(commit=True)

        self.assertIsNotNone(Tag.query.filter_by(name="Hybrid").first())

        item = Item(name="Super Silver Haze", description="AAA+ Excellent Kush", cover_image_id=item_image.id,
                    images=[item_image], tags=[hybrid_tag])
        item.save(commit=True)

        item_search = Item.query.filter_by(name="Super Silver Haze").first()
        self.assertIsNotNone(item_search)

        silver_haze_1g = Product(name="Super Silver Haze (1g)", item_id=item.id, cost=10)
        silver_haze_1g.save(commit=True)

        self.assertIsNotNone(Product.query.filter_by(name="Super Silver Haze (1g)").first())
        self.assertGreaterEqual(len(Product.query.filter_by(name="Super Silver Haze (1g)").all()), 1)
