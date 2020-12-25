from tests import TestCase

import json
import random
from firepot.utils import encode_auth_token, decode_auth_token, validate_auth_token


class TestApplicationRoutes(TestCase):
    def tearDown(self):
        super().tearDown()

    def register_and_login(self, first_name, last_name, email, password):
        name = self.register(first_name=first_name, last_name=last_name, email=email, password=password)

        token, id = self.login(email=email, password=password)
        self.assertEqual(id, decode_auth_token(token)['sub'])

        return token

    def register(self, first_name, last_name, email, password):
        data = dict(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )

        print("Sending with: {0}".format(json.dumps(data)))

        request = self.app.test_client().post('/auth/register/', data=json.dumps(data), follow_redirects=True,
                                              content_type='application/json')

        print(request.data)

        _json = json.loads(request.data)

        self.assertEqual(_json['status'], 'success', msg=_json['message'])

        return _json['payload']['name']

    def login(self, email, password):
        """
        Login to an account and retrieve the auth token
        :param email:
        :param password:
        :return:
        """

        login_data = dict(
            email=email,
            password=password
        )

        request = self.app.test_client().post('/auth/login/', data=json.dumps(login_data), follow_redirects=True,
                                              content_type='application/json')
        _json = json.loads(request.data)

        self.assertEqual(_json['status'], 'success', msg=_json['message'])

        token = _json['payload']['auth']
        id = _json['payload']['id']
        return token, id

    def test_login_and_register(self):
        from firepot.models import User
        auth_token = self.register_and_login(first_name="B", last_name="C", email="test@firepot.ca", password="testing")

        self.assertIsNotNone(auth_token)

        decoded = decode_auth_token(auth_token)

        self.assertIsNot(decoded, False)

        self.assertEqual(decoded['sub'], User.query.filter_by(email="test@firepot.ca").first().id)

    def test_products_list(self):
        from firepot.models import Item, Product, Image, Tag
        token = self.register_and_login(first_name="B", last_name="C", email="test@firepot.ca", password="testing")
        req = self.app.test_client().get("/store/products", headers={'Authorization': 'Bearer {0}'.format(token)})

        _json = json.loads(req.data)

        self.assertEqual(_json['message'], "Currently no stock available")

        silver_haze_img = Image(name="silver_haze_1", data="Base64 of super silver haze bb")
        silver_haze_img.save(commit=True)

        self.assertIsNotNone(Image.query.filter_by(name="silver_haze_1").first())

        sativa_tag = Tag(name="Sativa")
        sativa_tag.save(commit=True)

        self.assertIsNotNone(Tag.query.filter_by(name="Sativa").first())

        silver_haze = Item(name="Super Silver Haze", description="Epic Sativa AAAA Exotic level",
                           cover_image_id=silver_haze_img.id, images=[silver_haze_img], tags=[sativa_tag])

        silver_haze.save(commit=True)

        self.assertIsNotNone(Item.query.filter_by(name="Super Silver Haze").first())

        product = Product(name="Super Silver Haze (1g)", item_id=silver_haze.id, cost=10, stock=28)
        product.save(commit=True)

        self.assertGreaterEqual(len(Product.query.filter_by(item_id=silver_haze.id).all()), 1)

        req = self.app.test_client().get("/store/products", headers={'Authorization': 'Bearer {0}'.format(token)})

        _json = json.loads(req.data)

        self.assertEqual(_json['message'], "Store Products List")

        _items = _json['payload']['items']

        self.assertGreaterEqual(len(_items.keys()), 1)
