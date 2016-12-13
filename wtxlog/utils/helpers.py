# -*- coding: utf-8 -*-

import xmlrpclib
from flask import current_app, request, url_for
from flask_themes2 import render_theme_template, get_theme
from ..models import Category


def get_current_theme():
    return get_theme(current_app.config.get('THEME', 'default'))


def render_template(template, **context):
    return render_theme_template(get_current_theme(), template, **context)


def get_category_ids(longslug=''):
    """ID список назад к началу всех столбцов, указанных longslug"""

    cates = Category.query.filter(Category.longslug.startswith(longslug))
    if cates:
        return [cate.id for cate in cates.all()]
    else:
        return []


def page_url(page):
    """Назад к номеру страницыL"""
    _kwargs = request.view_args
    if 'page' in _kwargs:
        _kwargs.pop('page')
    if page > 1:
        return url_for(request.endpoint, page=page, **_kwargs)
    return url_for(request.endpoint, **_kwargs)


