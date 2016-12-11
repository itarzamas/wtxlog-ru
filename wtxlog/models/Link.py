# -*- coding: utf-8 -*-

import re
import json
import hashlib
from datetime import datetime
from werkzeug import cached_property
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer
from jinja2.filters import do_striptags, do_truncate
from flask_sqlalchemy import BaseQuery
from flask import current_app, request, url_for
from flask_login import UserMixin, AnonymousUserMixin

from ..ext import db

class Link(db.Model):
    """Внутренние ссылки"""

    __tablename__ = 'links'

    id = db.Column(db.Integer, primary_key=True)
    anchor = db.Column(db.String(64), nullable=False)
    title = db.Column(db.String(128))
    url = db.Column(db.String(255), nullable=False)
    note = db.Column(db.String(200))

    __mapper_args__ = {'order_by': [id.desc()]}

    def __repr__(self):
        return '<Link %r>' % (self.anchor)

    def __unicode__(self):
        return self.anchor


