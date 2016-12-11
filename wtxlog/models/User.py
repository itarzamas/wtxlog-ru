# -*- coding: utf-8 -*-
from datetime import datetime
import hashlib
from itsdangerous import URLSafeTimedSerializer as Serializer

from flask_login import UserMixin, AnonymousUserMixin
from flask import  current_app, request
from werkzeug.security import generate_password_hash, check_password_hash
from ..ext import db, to_bytes
from Role import Role
from . import Permission
from config import Config

class User(UserMixin, db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64))
    role_id = db.Column(db.Integer, db.ForeignKey(Role.id))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    about_me = db.Column(db.String(1000))
    member_since = db.Column(db.DateTime(), default=datetime.now)
    last_seen = db.Column(db.DateTime(), default=datetime.now)
    avatar_hash = db.Column(db.String(32))

    __mapper_args__ = {'order_by': [confirmed.desc(), id.desc()]}

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == Config.APP_ADMIN:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()

    @staticmethod
    def authenticate(username, password):
        """
        Проверка пользователя

        :param username: Имя пользователя или адрес электронной почты
        :param password: пароль пользователя
        """
        user = User.query.filter(db.or_(User.username == username,
                                        User.email == username)).first()
        if isinstance(user, User):
            if user.verify_password(password):
                return None, user
            else:
                return 'Invalid Password', None
        return 'Invalid Username', None

    @staticmethod
    def make_unique_username(username):
        if User.query.filter_by(username=username).first() is None:
            return username
        version = 2
        while True:
            new_username = '%s%s' % (username, str(version))
            if User.query.filter_by(username=new_username).first() is None:
                break
            version += 1
        return new_username

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        _hash = to_bytes(self.password_hash)
        return check_password_hash(_hash, password)

    def generate_confirmation_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'confirm': self.id})

    def confirm(self, token, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=expiration)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def generate_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=expiration)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        db.session.commit()
        return True

    def generate_email_change_token(self, new_email):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=expiration)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        db.session.commit()
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER) & self.confirmed

    def ping(self):
        self.last_seen = datetime.now()
        db.session.add(self)
        db.session.commit()

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        url = 'https://secure.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def __repr__(self):
        return '<User %r>' % (self.name or self.username)

    def __unicode__(self):
        return self.name or self.username


# Create M2M table
#article_tags_table = db.Table(
#    'article_tags',
#    db.Model.metadata,
#    db.Column('article_id', db.Integer, db.ForeignKey("articles.id", ondelete='CASCADE')),
#    db.Column('tag_id', db.Integer, db.ForeignKey("tags.id", ondelete='CASCADE')),
#)


