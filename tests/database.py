# -*- coding: utf-8 -*-
from flask import current_app
from flask_sqlalchemy import get_state, SQLAlchemy


def save(model):
    session = get_state(current_app).db.session
    session.add(model)
    session.commit()


db = SQLAlchemy()
