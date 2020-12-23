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
        token = self.register_and_login(first_name="B", last_name="C", email="test@firepot.ca", password="testing")
        req = self.app.test_client().get("/store/products", headers={'Authorization': 'Bearer {0}'.format(token)})
