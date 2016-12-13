# -*- coding: utf-8 -*-

from flask_sqlalchemy import BaseQuery 
from flask import url_for
#from flask import current_app, request, url_for
from werkzeug import cached_property
from . import db
import Article
#, keywords_split, to_bytes
from . import BODY_FORMAT

class TagQuery(BaseQuery):

    def search(self, keyword):
        keyword = u'%{0}%'.format(keyword.strip())
        return self.filter(Tag.name.ilike(keyword))


class Tag(db.Model):
    """Этикетка (Tag)"""

    __tablename__ = "tags"

    query_class = TagQuery

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, index=True, nullable=False)

    # SEO info
    seotitle = db.Column(db.String(128))
    seokey = db.Column(db.String(128))
    seodesc = db.Column(db.String(300))

    thumbnail = db.Column(db.String(255))
    template = db.Column(db.String(255))

    body = db.Column(db.Text)
    body_html = db.Column(db.Text)

    __mapper_args__ = {'order_by': [id.desc()]}

    def __repr__(self):
        return '<Tag %r>' % (self.name)

    def __unicode__(self):
        return self.name

    @cached_property
    def link(self):
        return url_for('main.tag', name=self.name.lower(), _external=True)

    @cached_property
    def shortlink(self):
        return url_for('main.tag', name=self.name.lower())

    @cached_property
    def count(self):
        return Article.query.public().filter(Article.tags.any(id=self.id)).count()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        if BODY_FORMAT == 'html':
            target.body_html = value
        else:
            target.body_html = markitup(value)

db.event.listen(Tag.body, 'set', Tag.on_changed_body)


