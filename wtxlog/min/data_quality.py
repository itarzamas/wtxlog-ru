import importlib
import json
import os

from bokeh.embed import components
from bokeh.model import Model
from dateutil import parser
from flask import g, render_template

from app.decorators import store_query_parameters, data_quality_items
from app.min.date_range_form import DateRangeForm


def data_quality_item_html(item, caption=None, export_name='item'):
    """Create the HTML for a data quality item.

    The generated html looks as follows.

    <figure class="data-quality-item" data-export-name="... your export name here ...">
        {... your data item content here ...}
        <figcaption>
            {caption}
        </figcaption>
    </figure>

    By default, the string representation of the item is used as data item content. However, if the item is a Bokeh
    model, Bokeh's components function is used to generate the necessary html.

    The figure caption is included only if the corresponding argument has a truthy value.

    The export name is intended to be used as filename when the item is exported to file. It thus should be unique
    weithin a page, but this isn't enforced.

    Params:
    -------
    item: object
        Data quality item.
    caption: str
        Figure caption.
    export_name: str
        Filename for exporting the data quality item.

    Return:
    -------
    str:
        HTML representing the data quality item.
    """

    if isinstance(item, Model):
        script, div = components(item)
        content = '<div>{script}{div}</div>'.format(script=script, div=div)
    else:
        content = str(item)

    figcaption = ''
    if caption:
        figcaption = '    <figcaption>\n' \
                     '        {caption}\n' \
                     '    </figcaption>'.format(caption=caption)
    return '<figure class="data-quality-item" data-export-name="{export_name}">' \
           '    {content}\n' \
           '    {figcaption}\n' \
           '</figure>'.format(content=content,
                              figcaption=figcaption,
                              export_name=export_name)


def data_quality_item(package, name):
    """Return the data quality item details for a package and name.

    The name must be the one used in the data_quality decorator of the function.

    Params:
    -------
    package: str
        Package containing the function.
    name: str
        Name used when registering the function.

    Return:
    -------
    tuple:
        The function and the dictionary of additional details, as passed to the function's decorator.

    """

    return data_quality_items[package][name]


@store_query_parameters(names=('start_date', 'end_date'))
def default_data_quality_content_for_date_range(package, default_start_date=None, default_end_date=None):
    """Create default data quality content for a date range query.

    The default data quality content (as created by _default_data_quality_content) is obtained for a date range, which
    the user can select in an input form.

    The start date for the range is inclusive, the end date exclusive.

    Defaults can be supplied for the start and end date.

    The content is created if the form is valid, irrespective of whether a GET or POST request is made. Otherwise only
    the form is included.

    Params:
    -------
    default_start_date: date
        Default start date for the query.
    default_end_date: date
        Default end date for the query.
    """

    form = DateRangeForm(default_start_date, default_end_date)

    # update form data from stored parameters
    stored_params = g.stored_query_parameters
    if 'start_date' in stored_params:
        form.start_date.data = parser.parse(stored_params['start_date'])
    if 'end_date' in stored_params:
        form.end_date.data = parser.parse(stored_params['end_date'])

    if form.validate():
        start_date = form.start_date.data
        end_date = form.end_date.data
        query_results = _default_data_quality_content(package, start_date=start_date, end_date=end_date)
    else:
        query_results = ''
    return render_template('data_quality/data_quality_query_page.html', form=form.html(), query_results=query_results)


def _default_data_quality_content(package, *args, **kwargs):
    """Content for a default data quality page.

    All the modules of the given package are imported and all data quality item functions (i.e. functions with a
    data_quality decorator) are registered. Then the functions named in the content.txt file within the package
    directory are called, and their output is joined together.

    All functions named in the context.txt file must actually exist in one of the package's modules.

    For example, assume that the content.txt file has the following content,

    rss_throughput
    RSS temperature

    Then these functions must be declared somewhere in the package's modules:

    @decorate(name='rss_throughput', caption='RSS throughput over time')
    def some_func_1():
        ...

    @decorate(name='RSS temperature', caption='Temperature over time')
    def some_func_2():
        ...

    You can choose any function names, as long as the name argument of the decorator has the correct value.

    Positional and keyword arguments (other than the first one, which gives the package) are passed on to the functions.
    This implies that all the functions should have the same signature.

    For example, if you call default_data_quality_content as

    default_data_quality_content('app.main.pages.example', from_date, to_date, include_errors=True)

    then all the functions named in the content.txt file must conform to the signature

    def func(from_date, to_date, include_errors)

    Params:
    -------
    package: str
        Fully qualified name of the package to use. If you are calling this function from the packages __init__.py file,
        the variable __package__ contains this name.
    *args: positional arguments
        Positional arguments to pass to the data quality functions named in the context.txt file.
    **kwargs: keyword arguments
        Keyword arguments to pass to the data quality functions named in the context.txt file.

    Return:
    -------
    str:
        <div> element with the HTML elements returned by the functions named in the content.txt file.

    """

    # find package directory
    spec = importlib.util.find_spec(package)
    package_init = spec.origin
    if not _is_package_init(package_init):
        raise ValueError('{package_name} is not a package'.format(package_name=package))
    package_dir = os.path.dirname(package_init)

    # find all the modules
    # use a set because some may be both source and compiled
    module_extensions = ('.py', '.pyc', '.pyo')
    modules = set([package + '.' + os.path.splitext(module)[0]
                   for module in os.listdir(package_dir)
                   if module.endswith(module_extensions) and os.path.splitext(module)[0].lower() != '__init__'])

    # import everything from the modules
    for module in modules:
        importlib.import_module(module)

    # add content for each function named in context.txt
    content_file = os.path.join(package_dir, 'content.txt')
    if not os.path.isfile(content_file):
        raise IOError('The file {path} does not exist')
    html = '<div>\n'
    with open(content_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                dqi = data_quality_item(package, line)
                item = dqi[0](*args, **kwargs)
                caption = dqi[1].get('caption')
                export_name = dqi[1].get('export_name')
                html += data_quality_item_html(item, caption=caption, export_name=export_name) + '\n'
    html += '</div>'

    return html


def _is_package_init(path):
    """Check whether a file path refers to a __init__.py or __init__.pyc file.

    Params:
    -------
    path: str
        File path.

    Return:
    -------
    bool:
        Whether the file path refers to a pacvkage init file.
    """

    return path.lower().endswith('__init__.py') or path.lower().endswith('__init__.pyc')
