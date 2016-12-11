# -*- coding: utf-8 -*-

#from flask import current_app, request, url_for

from ..ext import db 
#, keywords_split, to_bytes
#from Permission import Permission

class Role(db.Model):

    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    __mapper_args__ = {'order_by': [id.desc()]}

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.WRITE_ARTICLES |
                          Permission.PUBLISH_ARTICLES, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name

    def __unicode__(self):
        return self.name


