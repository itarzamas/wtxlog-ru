# -*- coding: utf-8 -*-


from werkzeug import cached_property
from flask import url_for
import re
pattern_hasmore = re.compile(r'<!--more-->', re.I)
from Category import  Category
from Topic import Topic
from User import User
#from Tag import Tag

from . import BODY_FORMAT, db, TaskQuery

class Task(db.Model):
    """Сообщения (статья)"""

    __tablename__ = "tasks"

    query_class = TaskQuery #создать в  __ini__.py , прежде чем использовать копия Article
    
    PER_PAGE = 10

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(200))
    title = db.Column(db.String(200), nullable=False)
    category_id = db.Column(db.Integer(), db.ForeignKey(Category.id), nullable=False,)
    category = db.relationship(Category, backref=db.backref("task"))

    topic_id = db.Column(db.Integer(), db.ForeignKey(Topic.id))
    topic = db.relationship(Topic, backref=db.backref("tasks"))

    #tags = db.relationship(Tag, secondary=article_tags_table, backref=db.backref("tasks"))

    #thumbnail = db.Column(db.String(255))
    #thumbnail_big = db.Column(db.String(255))
    #template = db.Column(db.String(255))

    #summary = db.Column(db.String(2000))
    body = db.Column(db.Text, nullable=False)
    body_html = db.Column(db.Text)

    published = db.Column(db.Boolean, default=True)
    #ontop = db.Column(db.Boolean, default=False)
    #recommend = db.Column(db.Boolean, default=False)

    #hits = db.Column(db.Integer, default=0)

    #author_id = db.Column(db.Integer, db.ForeignKey(User.id))
    #author = db.relationship(User, backref=db.backref("tasks"))

    created = db.Column(db.DateTime())
    #last_modified = db.Column(db.DateTime())

    __mapper_args__ = {'order_by': id.desc()}

    def __repr__(self):
        return '<Task %r>' % (self.title)

    def __unicode__(self):
        return self.title

    @cached_property
    def has_more(self):
            pass
#            return pattern_hasmore.search(self.body) is not None or \
#            self.summary.find('...') >= 0

    @cached_property
    def link(self):
        return url_for('main.task', task_id=self.id, _external=True)

    @cached_property
    def shortlink(self):
        return url_for('main.task', task_id=self.id)

    @cached_property
    def get_next(self):
        _query = db.and_(Task.category_id.in_([self.category.id]),
                         Task.id > self.id)
        return self.query.public().filter(_query) \
                         .order_by(Task.id.asc()) \
                         .first()

    @cached_property
    def get_prev(self):
        _query = db.and_(Task.category_id.in_([self.category.id]),
                         Task.id < self.id)
        return self.query.public().filter(_query) \
                         .order_by(Task.id.desc()) \
                         .first()

    @staticmethod
    def before_insert(mapper, connection, target):
        def _format(_html):
            return do_truncate(do_striptags(_html), length=200)

        #value = target.body
        #if target.summary is None or target.summary.strip() == '':
        #    # Когда вы добавляете статью, если summary пуст, автоматически генерируется
        #    # !!!!!!!!!!!!!!!!!!!!!!!!!
        #    if BODY_FORMAT == 'html':
        #        target.summary = _format(value)
        #    else:
        ##        _match = pattern_hasmore.search(value)
        #       if _match is not None:
        #            more_start = _match.start()
        #            target.summary = _format(markitup(value[:more_start]))
        #        else:
        #            target.summary = _format(target.body_html)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        if BODY_FORMAT == 'html':
            target.body_html = value
        else:
            target.body_html = markitup(value)

db.event.listen(Task.body, 'set', Task.on_changed_body)
db.event.listen(Task, 'before_insert', Task.before_insert)

