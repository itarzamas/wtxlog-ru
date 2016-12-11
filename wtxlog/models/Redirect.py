# -*- coding: utf-8 -*-

from ..ext import db

class Redirect(db.Model):
    """Перенаправление (редирект)"""

    __tablename__ = 'redirects'

    id = db.Column(db.Integer, primary_key=True)
    old_path = db.Column(db.String(128), nullable=False)
    new_path = db.Column(db.String(128), nullable=False)
    note = db.Column(db.String(400))

    __mapper_args__ = {'order_by': [id.desc()]}

    def __repr__(self):
        return '<Redirect %r>' % (self.old_path)

    def __unicode__(self):
        return self.old_path


