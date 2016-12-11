# -*- coding: utf-8 -*-

from ..ext import db



class Label(db.Model):
    """HTML фрагмент"""

    __tablename__ = 'labels'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(32), nullable=False)
    title = db.Column(db.Unicode(100), nullable=False, )
    html = db.Column(db.Text, nullable=False)

    __mapper_args__ = {'order_by': [id.desc()]}

    def __repr__(self):
        return '<Label %r>' % (self.title)

    def __unicode__(self):
        return self.title

