# -*- coding: utf-8 -*-

from flask import Blueprint

myapi = Blueprint('myapi', __name__)

from . import views
