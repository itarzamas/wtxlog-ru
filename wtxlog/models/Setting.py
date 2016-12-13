# -*- coding: utf-8 -*-

#from flask import current_app, request, url_for

from . import db
#, keywords_split, to_bytes
#from config import Config

class Setting(db.Model):

    __tablename__ = 'settings'

    FORMATS = (
        ('text', "text"),
        ('int', "int"),
        ('json', "json"),
        ('float', "float"),
    )

    DEFAULT_FORMATTER = lambda value: value

    STR_FORMATTER = lambda value: str(value)

    FORMATTERS = {
        'json': lambda value: json.loads(value),
        'text': DEFAULT_FORMATTER,
        'int': lambda value: int(value),
        'float': lambda value: float(value)
    }

    REVERSE_FORMATTERS = {
        'json': lambda value:
        value if isinstance(value, str) else json.dumps(value),
        'text': DEFAULT_FORMATTER,
        'int': DEFAULT_FORMATTER,
        'float': DEFAULT_FORMATTER
    }

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    rawvalue = db.Column(db.String(4096), nullable=False)
    formatter = db.Column(db.String(16), default='text', nullable=False)
    #: set True for Builtin Configuration Value
    builtin = db.Column(db.Boolean, default=False)
    description = db.Column(db.String(255))

    __mapper_args__ = {'order_by': [name.asc()]}

    @classmethod
    def get(cls, name, default=None):

        try:
            ret = cls.query.filter_by(name=name).first().value
        except:
            ret = None

        if not ret and name.isupper():
            ret = current_app.config.get(name)

        return ret or default

    @staticmethod
    def after_update(mapper, connection, target):
        # Try to update the config for the running app
        # AFAIK Flask apps are not thread safe
        if target.builtin and target.name.isupper():
            try:
                current_app.config.update({target.name: target.value})
            except:
                pass

    @property
    def value(self):
        return self.FORMATTERS.get(self.formatter,
                                   self.DEFAULT_FORMATTER)(self.rawvalue)

    @value.setter
    def value(self, value):
        self.rawvalue = self.REVERSE_FORMATTERS.get(self.formatter,
                                                    self.STR_FORMATTER)(value)

    def __repr__(self):
        return '<Setting %r>' % (self.name)

    def __unicode__(self):
        return u'{s.name} -> {s.value}'.format(s=self)

db.event.listen(Setting, 'after_insert', Setting.after_update)
db.event.listen(Setting, 'after_update', Setting.after_update)
