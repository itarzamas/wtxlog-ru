from bokeh.resources import CDN
from flask import Blueprint

min = Blueprint('min', __name__)


#@min.context_processor
#def bokeh_resources():
#    return dict(bokeh_resources=CDN)


from . import views, errors
