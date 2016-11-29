# -*- coding: utf-8 -*-

import os
import re
import json
import urllib
import datetime

from flask import request, url_for, redirect, current_app, make_response, abort
from werkzeug.contrib.atom import AtomFeed
from werkzeug._compat import to_bytes
from webhelpers.paginate import Page, PageURL
from flask_mobility.decorators import mobile_template

from flask_login import current_user

from ..decorators import permission_required
from ..utils.helpers import render_template, get_category_ids, page_url
from ..utils.upload import SaveUploadFile
from ..utils.metaweblog import blog_dispatcher
from ..ext import cache
from ..models import db, Article, Category, Tag, Flatpage, Topic, \
    Role, Permission
from . import main

IMAGE_TYPES = {
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'image/gif': '.gif',
}


@main.route('/deploy/')
def deploy():
    db.create_all()
    Role.insert_roles()
    return 'deployed'


@main.route('/')
@main.route('/page/<int:page>/')
@mobile_template('{mobile/}%s')
@cache.cached()
def index(template, page=1):
    _template = template % 'index.html'
    blog_mode = current_app.config.get("BLOG_MODE")
    if blog_mode:
        _url = page_url
        _query = Article.query.public()
        pagination = Page(_query, page=page, items_per_page=Article.PER_PAGE, url=_url)
        articles = pagination.items

        return render_template(_template,
                               articles=articles,
                               pagination=pagination)
    else:
        return render_template(_template)


@main.route('/article/<int:article_id>/')
@mobile_template('{mobile/}%s')
@cache.cached(86400)
def article(template, article_id):
    article = Article.query.get_or_404(article_id)

    if not article.published:
        abort(403)

    _template = template % (article.category.article_template or
                            article.template or 'article.html')
    return render_template(_template, article=article)


@main.route('/category/<path:longslug>/')
@main.route('/category/<path:longslug>/page/<int:page>/')
@mobile_template('{mobile/}%s')
@cache.cached(86400)
def category(template, longslug, page=1):
    category = Category.query.filter_by(longslug=longslug).first_or_404()
    cate_ids = get_category_ids(longslug)

    _url = page_url
    _query = Article.query.public().filter(Article.category_id.in_(cate_ids))
    pagination = Page(_query, page=page, items_per_page=Article.PER_PAGE, url=_url)

    articles = pagination.items

    _template = template % (category.template or 'category.html')
    return render_template(_template,
                           category=category,
                           pagination=pagination,
                           articles=articles)


@main.route('/archives/<int:year>/<int:month>/')
@main.route('/archives/<int:year>/<int:month>/page/<int:page>/')
@mobile_template('{mobile/}%s')
@cache.cached(86400)
def archives(template, year, month, page=1):
    _url = page_url
    _query = Article.query.archives(year, month)
    pagination = Page(_query, page=page, items_per_page=Article.PER_PAGE, url=_url)

    articles = pagination.items

    _template = template % 'archives.html'
    return render_template(_template,
                           pagination=pagination,
                           articles=articles,
                           year=year,
                           month=month)


@main.route('/tag/')
def tags_():
    return redirect(url_for('.tags'), code=301)


@main.route('/tags/')
@mobile_template('{mobile/}%s')
@cache.cached(86400)
def tags(template):
    _template = template % 'tags.html'
    return render_template(_template)


@main.route('/tag/<name>/')
@main.route('/tag/<name>/page/<int:page>/')
@mobile_template('{mobile/}%s')
@cache.cached(86400)
def tag(template, name, page=1):
    """
    :param template:
    Файл шаблона, этот параметр автоматически передается
    :param name:
        Имя тега, если не-ASCII символов, как правило, через URL закодированного
    """
    # Если name Не ASCII，Входящий в основном через URL закодированного
    # Если name URL Код, вам нужно будет декодировать Unicode
    # URL-код метода судить: Если такой URL-закодированы, кодирование будет появляться снова до 25 ``% каждого кода
    _name = to_bytes(name, 'utf-8')
    if urllib.quote(_name).count('%25') > 0:
        name = urllib.unquote(_name)

    tag = Tag.query.filter_by(name=name).first_or_404()

    _url = page_url
    _query = Article.query.public().filter(Article.tags.any(id=tag.id))
    pagination = Page(_query, page=page, items_per_page=Article.PER_PAGE, url=_url)

    articles = pagination.items

    _template = template % (tag.template or 'tag.html')
    return render_template(_template,
                           tag=tag,
                           pagination=pagination,
                           articles=articles)


@main.route('/topic/')
def topics_():
    return redirect(url_for('.topics'), code=301)


@main.route('/topics/')
@mobile_template('{mobile/}%s')
@cache.cached(86400)
def topics(template):
    _template = template % 'topics.html'
    return render_template(_template)


@main.route('/topic/<slug>/')
@main.route('/topic/<slug>/page/<int:page>/')
@mobile_template('{mobile/}%s')
@cache.cached(86400)
def topic(template, slug, page=1):
    topic = Topic.query.filter_by(slug=slug).first_or_404()

    _url = page_url
    _query = Article.query.public().filter(Article.topic_id == topic.id)
    pagination = Page(_query, page=page, items_per_page=Article.PER_PAGE, url=_url)

    articles = pagination.items

    _template = template % (topic.template or 'topic.html')
    return render_template(_template,
                           topic=topic,
                           pagination=pagination,
                           articles=articles)


@main.route('/flatpage/<slug>/')
@mobile_template('{mobile/}%s')
@cache.cached(86400)
def flatpage(template, slug):
    flatpage = Flatpage.query.filter_by(slug=slug).first_or_404()
    _template = template % (flatpage.template or 'flatpage.html')
    return render_template(_template, flatpage=flatpage)


@main.route('/search/')
@mobile_template('{mobile/}%s')
def search(template):
    page = int(request.args.get('page', 1))
    keyword = request.args.get('keyword', None)
    pagination = None
    articles = None
    if keyword:
        _url = PageURL(url_for('main.search'),
                       {"page": page, "keyword": keyword.encode('utf-8')})
        _query = Article.query.search(keyword)
        pagination = Page(_query, page=page, items_per_page=Article.PER_PAGE, url=_url)

        articles = pagination.items

    _template = template % 'search.html'
    return render_template(_template,
                           articles=articles,
                           keyword=keyword,
                           pagination=pagination)


@main.route('/sitemap.xsl')
def sitemap_xsl():
    response = make_response(render_template('sitemap.xsl'))
    response.mimetype = 'text/xsl'
    return response


@main.route('/sitemap.xml', methods=['GET'])
@cache.cached(86400)
def sitemap():
    """Generate sitemap.xml. Makes a list of urls and date modified."""
    urlset = []

    urlset.append(dict(
        loc=url_for('.index', _external=True),
        lastmod=datetime.date.today().isoformat(),
        changefreq='weekly',
        priority=1,
    ))

    # categories
    categories = Category.query.all()

    for category in categories:
        urlset.append(dict(
            loc=category.link,
            changefreq='weekly',
            priority=0.8,
        ))

    # tags
    tags = Tag.query.all()

    for tag in tags:
        urlset.append(dict(
            loc=tag.link,
            changefreq='weekly',
            priority=0.6,
        ))

    # articles model pages
    articles = Article.query.public().all()

    for article in articles:
        url = article.link
        modified_time = article.last_modified.date().isoformat()
        urlset.append(dict(
            loc=url,
            lastmod=modified_time,
            changefreq='monthly',
            priority=0.5,
        ))

    sitemap_xml = render_template('sitemap.xml', urlset=urlset)
    res = make_response(sitemap_xml)
    res.mimetype = 'application/xml'
    return res


@main.route('/feed/')
def feed():
    site_name = current_app.config.get('SITE_NAME')

    feed = AtomFeed(
        u"%s Recent Articles" % site_name,
        feed_url=request.url,
        url=request.url_root,
    )

    articles = Article.query.public().limit(10).all()

    for article in articles:
        feed.add(
            article.title,
            unicode(article.summary),
            content_type='html',
            author=article.author,
            url=article.link,
            updated=article.last_modified,
            published=article.created
        )

    res = make_response(feed.get_response())
    res.mimetype = 'application/xml'
    return res


@main.route('/upload/', methods=['POST', 'OPTIONS'])
@permission_required(Permission.UPLOAD_FILES)
def upload():
    ''' Функция загрузки файла '''

    result = {"err": "", "msg": {"url": "", "localfile": ""}}
    fname = ''
    fext = ''
    data = None

    if request.method == 'POST' and 'filedata' in request.files:
        # традиционный режим, IE браузер использeт этот режим
        fileobj = request.files['filedata']
        result["msg"]["localfile"] = fileobj.filename
        fname, fext = os.path.splitext(fileobj.filename)
        data = fileobj.read()
    elif 'CONTENT_DISPOSITION' in request.headers:
        # HTML5 Режим загрузки, FireFox по умолчанию в этом режиме, и т.д.
        pattern = re.compile(r"""\s.*?\s?filename\s*=\s*['|"]?([^\s'"]+).*?""", re.I)
        _d = request.headers.get('CONTENT_DISPOSITION').encode('utf-8')
        if urllib.quote(_d).count('%25') > 0:
            _d = urllib.unquote(_d)
        filenames = pattern.findall(_d)
        if len(filenames) == 1:
            result["msg"]["localfile"] = urllib.unquote(filenames[0])
            fname, fext = os.path.splitext(filenames[0])
        data = request.data

    ONLINE = False
    if ONLINE:
        obj = SaveUploadFile(fext, data)
        url = obj.save()
        result["msg"]["url"] = '!%s' % url
    else:
        obj = SaveUploadFile(fext, data)
        url = obj.save()
        result["msg"]["url"] = '!%s' % url
        pass

    return json.dumps(result)


@main.route('/uploadremote/', methods=['POST', 'OPTIONS'])
@permission_required(Permission.UPLOAD_FILES)
def uploadremote():
    """
    xheditorСохранить простую реализацию удаленного изображения
     URL с "|" разграничены строка возвращается с "|" разделены
     Возвращает строку формат не формат JSON
    """
    localdomain_re = re.compile("""https?:\/\/[^\/]*?(bcs\.duapp\.com)\/""", re.I)
    imageTypes = {'gif': '.gif', 'jpeg': '.jpg', 'jpg': '.jpg', 'png': '.png'}
    urlout = []
    result = ''
    srcUrl = request.form.get('urls', None)
    if srcUrl:
        urls = srcUrl.split('|')
        for url in urls:
            if not localdomain_re.search(url.strip()):
                downfile = urllib.urlopen(url)
                fext = imageTypes[downfile.headers.getsubtype().lower()]

                urlreturn = ''

                ONLINE = False
                if ONLINE:
                    obj = SaveUploadFile(fext, downfile.read())
                    urlreturn = obj.save()
                else:
                    obj = SaveUploadFile(fext, downfile.read())
                    urlreturn = obj.save()
                    pass

                urlout.append(urlreturn)
            else:
                urlout.append(url)
    result = '|'.join(urlout)
    return result


@main.route('/xmlrpc/', methods=['POST', 'OPTIONS'])
def xmlrpc():
    """
    author: digwtx <wtx358@qq.com>

    firefox-scribefire and Blogilo passed.

    Reference:

    * <http://codex.wordpress.org.cn/XML-RPC_MetaWeblog_API>
    * <http://blog.csdn.net/priderock/article/details/1754503>
    """

    # return blog_dispatcher._marshaled_dispatch(request.data)
    response_data = blog_dispatcher._marshaled_dispatch(request.data)
    return current_app.response_class(response_data, mimetype='text/xml')


@main.route('/ckupload/', methods=['POST', 'OPTIONS'])
@permission_required(Permission.UPLOAD_FILES)
def ckupload():
    """CKEditor file upload"""
    data = None
    error = ''
    url = ''
    callback = request.args.get("CKEditorFuncNum")

    if request.method == 'POST' and 'upload' in request.files:
        # Для IE и прочих устаревших браузеров
        fileobj = request.files['upload']
        data = fileobj.read()
        fname, fext = os.path.splitext(fileobj.filename)
        if fext.lower() in ('.gif', '.jpg', '.jpeg', '.png'):
            _fext = fext
        else:
            _fext = fileobj.filename
        try:
            obj = SaveUploadFile(_fext, data)
            url = obj.save()
        except:
            error = 'upload error'
    else:
        error = 'post error'

    res = """<script type="text/javascript">
  window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
</script>""" % (callback, url, error)

    response = make_response(res)
    response.headers["Content-Type"] = "text/html"
    return response
