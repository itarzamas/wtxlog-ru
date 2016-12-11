from urllib.parse import urlparse

from bokeh.embed import autoload_server
from flask import request


def title():
    return 'Interactive Plot'


def content():
    up = urlparse(request.url)
    scheme = up.scheme
    host = up.netloc
    port = up.port
    if port:
        host = host[:-(len(str(port)) + 1)]
    bokeh_server_url = '{scheme}://{host}:5100'.format(scheme=scheme, host=host)
    script1 = autoload_server(model=None, app_path='/sine', url=bokeh_server_url)
    script2 = autoload_server(model=None, app_path='/cosine', url=bokeh_server_url)
    return '<div>' + script1 + '</div>\n<div>' + script2 + '</div>'
