# -*- coding: utf-8 -*-
from werkzeug import cached_property
from flask import url_for

from ..ext import db

class Flatpage(db.Model):
    """Одна страница(плоская)"""

    __tablename__ = 'flatpages'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(32), nullable=False)
    title = db.Column(db.Unicode(100), nullable=False, )
    seotitle = db.Column(db.Unicode(200))
    seokey = db.Column(db.Unicode(128))
    seodesc = db.Column(db.Unicode(400))
    template = db.Column(db.String(255))
    body = db.Column(db.Text, nullable=False)
    body_html = db.Column(db.Text, nullable=False)

    __mapper_args__ = {'order_by': [id.desc()]}

    def __repr__(self):
        return '<Flatpage %r>' % (self.title)

    def __unicode__(self):
        return self.title

    @cached_property
    def link(self):
        return url_for('main.flatpage', slug=self.slug, _external=True)

    @cached_property
    def shortlink(self):
        return url_for('main.flatpage', slug=self.slug)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        if BODY_FORMAT == 'html':
            target.body_html = value
        else:
            target.body_html = markitup(value)

db.event.listen(Flatpage.body, 'set', Flatpage.on_changed_body)

