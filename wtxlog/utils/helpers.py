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
    """"ID список назад к началу всех столбцов, указанных longslug"""
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


#def baidu_ping(url):
#    """
#    :ref: http://zhanzhang.baidu.com/tools/ping
#
#    ОтправитьPing используя XML-RPC Запрос клиента должен включать в себя следующие элементы:
#    RPC Endpoint： http://ping.baidu.com/ping/RPC2
#    Назовите имя метода: weblogUpdates.extendedPing
#
#     Параметры: (которые должны быть переданы в том же порядке, как указано ниже)
#     название блога
#     Блог Домашний адрес
#     Новый адрес для волос статьи
#     Адрес блога RSS
#    """
#
#    result = 1
#    rpc_server = xmlrpclib.ServerProxy('http://ping.baidu.com/ping/RPC2')
#
#    try:
#        # Возвращает 0 успешно отправлен
#        current_app.logger.info('begin to ping baidu: <%s>' % url)
#        result = rpc_server.weblogUpdates.extendedPing(
#            current_app.config.get('SITE_NAME'),
#            url_for('main.index', _external=True),
#            url,
#            url_for('main.feed', _external=True)
#        )
#    except:
#        pass
#
#    if result != 0:
#        current_app.logger.warning('<%s> ping to baidu failed' % url)
#
#    return result == 0
