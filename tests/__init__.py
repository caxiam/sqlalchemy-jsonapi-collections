# -*- coding: utf-8 -*-
from unittest import TestCase
from flask import Flask

from tests import settings
from tests.database import db

import sys


sys.dont_write_bytecode = True


class UnitTestCase(TestCase):

    def setUp(self):
        """Create app test client"""
        self.app = Flask(__name__)
        self.app.config.from_object(settings)
        if db is not None:
            db.init_app(self.app)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        db.session.commit()
        self.addCleanup(self.cleanup)

    def cleanup(self):
        """Tear down database"""
        db.session.remove()
        db.drop_all()
        db.get_engine(self.app).dispose()
        self.app_context.pop()
