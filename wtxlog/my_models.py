__author__ = 'itarzamas'

from .ext import db
from models import  Permission, Role, Category, Tag, Topic, User, AnonymousUser, Setting, \
		    Article, FriendLink, Label, Setting, Flatpage,Redirect

# This file is used by alembic's autogenerate function
# Apparently it wants all the models in a single file.