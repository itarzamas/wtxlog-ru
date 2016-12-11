import pandas as pd

from bokeh.models.formatters import DatetimeTickFormatter, DEFAULT_DATETIME_FORMATS
from bokeh.plotting import figure, ColumnDataSource

from app import db


def data_quality_date_plot(start_date, end_date, title, column, table, logic='', y_axis_label=''):
    """Create a plot using a data quality table and the FileData table

    The plot shows the column from table for the period between start_date
    (inclusive) and end_date (exclusive).  In addition to the date logic, it will
    append what is given in logic

    Params:
    -------
    start_date: date
        Earliest date to include in the plot.
    end_date: date
        Earliest date not to include in the plot.
    title: string
        Title for the plot
    column: string
        Column to plot along the y-axis
    table: string
        Table to join with FileData.  The table should have a FileData_Id
        column
    logic: string
        Any other logic to append to the query
    y_axis_label: string
        Y-axis label

    Return:
    -------
    str:
        A <div> element with the weather downtime plot.
    """
    sql = "select UTStart, {column} from {table} join FileData using (FileData_Id) " \
          "       where UTStart > '{start_date}' and UTStart <'{end_date}' {logic}"\
        .format(column=column, start_date=start_date, end_date=end_date,
                table=table, logic=logic)
    df = pd.read_sql(sql, db.engine)
    source = ColumnDataSource(df)

    date_formats = DEFAULT_DATETIME_FORMATS()
    date_formats['hours'] = ['%e %b %Y']
    date_formats['days'] = ['%e %b %Y']
    date_formats['months'] = ['%e %b %Y']
    date_formats['years'] = ['%e %b %Y']
    date_formatter = DatetimeTickFormatter(formats=date_formats)

    p = figure(title=title,
               x_axis_label='Date',
               y_axis_label=y_axis_label,
               x_axis_type='datetime')
    p.scatter(source=source, x='UTStart', y=column)

    p.xaxis[0].formatter = date_formatter

    return p
