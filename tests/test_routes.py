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
        pass

    def register(self, first_name, last_name, email, password):
        data = dict(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )

        request = self.app.test_client().post('/auth/regster/', data=json.dumps(json), follow_redirects=True,
                                              content_type='application/json')
        _json = json.loads(request.data)

        self.assertEqual(_json['status'], 'success', msg=_json['msg'])

        return _json['name']

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

        self.assertEqual(_json['status'], 'success', msg=_json['msg'])

        token = _json['auth']
        id = _json['id']
        return token, id

    def test_login_and_register(self):
        auth_token = self.register_and_login()
