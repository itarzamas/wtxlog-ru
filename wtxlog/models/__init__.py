# -*- coding: utf-8 -*-

__author__ = 'itarzamas'
from ..ext import db
from flask_sqlalchemy import BaseQuery
from flask import url_for
class Permission:
    ''' Определение привилегий '''

    #:Право написания статей, без права публикации
    WRITE_ARTICLES = 0x04

    #: Статьи могут быть опубликованы
    PUBLISH_ARTICLES = 0x08

    #: Права на загрузку файлов
    UPLOAD_FILES = 0x10

    #: Права администратора
    ADMINISTER = 0x80


article_tags_table = db.Table(
    'article_tags',
    db.Model.metadata,
    db.Column('article_id', db.Integer, db.ForeignKey("articles.id", ondelete='CASCADE')),
    db.Column('tag_id', db.Integer, db.ForeignKey("tags.id", ondelete='CASCADE')),
)


class ArticleQuery(BaseQuery):
 
    def public(self):
        return self.filter_by(published=True)

    def search(self, keyword):
        criteria = []

        for keyword in keywords_split(keyword):
            keyword = u'%{0}%'.format(keyword)
            criteria.append(db.or_(Article.title.ilike(keyword),))

        q = reduce(db.or_, criteria)
        return self.public().filter(q)

    def archives(self, year, month):
        if not year:
            return self

        criteria = []
        criteria.append(db.extract('year', Article.created) == year)
        if month:
            criteria.append(db.extract('month', Article.created) == month)

        q = reduce(db.and_, criteria)
        return self.public().filter(q)


from AnonymousUser import AnonymousUser
from .Article import Article
from .Category import Category
from .Flatpage import Flatpage
from .FriendLink import FriendLink
from .Label import Label
from .Link import Link
from .Redirect import Redirect
from .Role import Role
from .Setting import Setting
from .Tag import Tag
from .Topic import Topic
from .User import User
#from  import
#from  import