import os
import tempfile
import unittest

from firepot.factory import create_app

from firepot.config import Config, TestConfig

from firepot.extensions import db


def clean_db(db):
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())


class TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super(TestCase, cls).setUpClass()

        cls.app = create_app(testing=True)
        cls.db = db
        cls.db.app = cls.app
        cls.app.testing = True
        with cls.app.app_context():
            import firepot.models
            db.create_all(app=cls.app)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.db.drop_all()
        super(TestCase, cls).tearDownClass()

    def setUp(self):
        super(TestCase, self).setUp()
        self.app_context = self.app.app_context()
        self.app_context.push()
        import firepot.models
        clean_db(self.db)

    def tearDown(self):
        # db.session.rollback()
        # db.drop_all()
        # self.app_context.pop()
        # os.close(self.db_fb)
        # os.unlink(self.app.config['DATABASE'])
        self.db.session.rollback()
        self.app_context.pop()

        super(TestCase, self).tearDown()
