# -*- coding: utf-8 -*-

from werkzeug import cached_property
from flask import  request, url_for

from ..models import db, BODY_FORMAT

class Topic(db.Model):
    """Тема """

    __tablename__ = "topics"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(64), unique=True, index=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)

    # SEO page title
    seotitle = db.Column(db.String(128))
    seokey = db.Column(db.String(128))
    seodesc = db.Column(db.String(300))

    thumbnail = db.Column(db.String(255))
    template = db.Column(db.String(255))

    body = db.Column(db.Text)
    body_html = db.Column(db.Text)

    __mapper_args__ = {'order_by': [id.desc()]}

    def __repr__(self):
        return '<Topic %r>' % (self.name)

    def __unicode__(self):
        return self.name

    @cached_property
    def link(self):
      return url_for('main.topic', slug=self.slug, _external=True)

    @cached_property
    def shortlink(self):
      return url_for('main.topic', slug=self.slug)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        if BODY_FORMAT == 'html':
            target.body_html = value
        else:
            target.body_html = markitup(value)
db.event.listen(Topic.body, 'set', Topic.on_changed_body)

