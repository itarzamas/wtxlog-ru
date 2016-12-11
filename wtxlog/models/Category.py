# -*- coding: utf-8 -*-
import re
import json
import hashlib
from datetime import datetime
from werkzeug import cached_property
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer
from jinja2.filters import do_striptags, do_truncate
#from flask_sqlalchemy import BaseQuery
from flask import current_app as app
from flask import url_for

from ..ext import db, keywords_split, to_bytes
import Article

class Category(db.Model):
    """каталог (категория)"""

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(64), nullable=False)
    longslug = db.Column(db.String(255), unique=True, index=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)

    parent_id = db.Column(db.Integer(), db.ForeignKey('categories.id'))
    parent = db.relationship('Category',
                             primaryjoin=('Category.parent_id == Category.id'),
                             remote_side=id, backref=db.backref("children"))

    # SEO page title
    seotitle = db.Column(db.String(128))
    seokey = db.Column(db.String(128))
    seodesc = db.Column(db.String(300))

    thumbnail = db.Column(db.String(255))
    template = db.Column(db.String(255))
    article_template = db.Column(db.String(255))

    body = db.Column(db.Text)
    body_html = db.Column(db.Text)

    __mapper_args__ = {'order_by': [longslug]}

    def __repr__(self):
        return '<Category %r>' % (self.name)

    def __unicode__(self):
        return self.longslug or self.name

    @cached_property
    def link(self):
        return url_for('main.category', longslug=self.longslug, _external=True)

    @cached_property
    def shortlink(self):
        return url_for('main.category', longslug=self.longslug)

    @cached_property
    def count(self):
        cates = db.session.query(Category.id).filter(Category.longslug.startswith(self.longslug)).all()
        cate_ids = [cate.id for cate in cates]
        return Article.query.public().filter(Article.category_id.in_(cate_ids)).count()

    @cached_property
    def parents(self):
        lst = []
        lst.append(self)
        c = self.parent
        while c is not None:
            lst.append(c)
            c = c.parent
        lst.reverse()
        return lst

    @staticmethod
    def tree():
        """TreeList"""
        cates = Category.query.all()
        out = []
        for cate in cates:
            indent = len(cate.longslug.split('/')) - 1
            out.append((indent, cate))
        return out

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        if BODY_FORMAT == 'html':
            target.body_html = value
        else:
            target.body_html = markitup(value)

    def on_changed_longslug(target, value, oldvalue, initiator):
        '''Если столбцы подстолбцах, вы не можете изменитьlongslug，Это может привести к longslug непоследовательный'''
        if target.children and value != oldvalue:
            raise Exception('Category has children, longslug can not be change!')

    def gen_longslug(self):
        '''генерироватьlongslug'''
        if self.parent:
            _longslug = '/'.join([self.parent.longslug, self.slug]).lower()
        else:
            _longslug = self.slug.lower()
        self.longslug = _longslug

    @staticmethod
    def before_insert(mapper, connection, target):
        target.gen_longslug()

        _c = Category.query.filter_by(longslug=target.longslug).first()
        # Когда новый судья longslug Независимо от того, чтобы повторить
        if _c:
            raise Exception('Category longslug "%s" already exist' % _c.longslug)

    @staticmethod
    def before_update(mapper, connection, target):
        target.gen_longslug()

        _c = Category.query.filter_by(longslug=target.longslug).first()
        # Определить, является ли дубликат обновления longslug
        if _c and _c.id != target.id:
            raise Exception('Category longslug "%s" already exist' % _c.longslug)

db.event.listen(Category.body, 'set', Category.on_changed_body)
db.event.listen(Category.longslug, 'set', Category.on_changed_longslug)
db.event.listen(Category, 'before_insert', Category.before_insert)
db.event.listen(Category, 'before_update', Category.before_update)
