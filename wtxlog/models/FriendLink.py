# -*- coding: utf-8 -*-

from . import db

class FriendLink(db.Model):
    """ссылки на друзей (связи)"""

    __tablename__ = 'friendlinks'

    id = db.Column(db.Integer, primary_key=True)
    anchor = db.Column(db.String(64), nullable=False)
    title = db.Column(db.String(128))
    url = db.Column(db.String(255), nullable=False)
    actived = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=1)
    note = db.Column(db.String(400))

    __mapper_args__ = {'order_by': [actived.desc(), order.asc()]}

    def __repr__(self):
        return '<FriendLink %r>' % (self.anchor)

    def __unicode__(self):
        return self.anchor


