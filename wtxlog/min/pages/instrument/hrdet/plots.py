import pandas as pd

from bokeh.embed import components
from bokeh.models.formatters import DatetimeTickFormatter, DEFAULT_DATETIME_FORMATS
from bokeh.plotting import figure, ColumnDataSource

from app import db
from app.decorators import data_quality
from app.main.data_quality_plots import data_quality_date_plot


@data_quality(name='hrdet_bias', caption='Mean  HRDET Bias Background levels')
def hrdet_bias_plot(start_date, end_date):
    """Return a <div> element with a weather downtime plot.

    The plot shows the downtime for the period between start_date (inclusive) and end_date (exclusive).

    Params:
    -------
    start_date: date
        Earliest date to include in the plot.
    end_date: date
        Earliest date not to include in the plot.

    Return:
    -------
    str:
        A <div> element with the weather downtime plot.
    """
    title = "HRDET Bias Levels"
    column = 'BkgdMean'
    table = 'PipelineDataQuality_CCD'
    logic = " and FileName like 'R%%' and Target_Name='BIAS'"
    y_axis_label = 'Bias Background Mean (e)'
    return data_quality_date_plot(start_date, end_date, title, column, table, logic=logic, y_axis_label=y_axis_label)


@data_quality(name='hrdet_vacuum_temp', caption='HRS HRDET Vacuum Temperature')
def hrdet_vacuum_temp_plot(start_date, end_date):
    """Return a <div> element with a HRS vacuum temperature plot.

    The plot shows the HRS vacuum temperature for the period between start_date (inclusive) and end_date (exclusive).

    Params:
    -------
    start_date: date
        Earliest date to include in the plot.
    end_date: date
        Earliest date not to include in the plot.

    Return:
    -------
    str:
        A <div> element with the weather downtime plot.
    """
    title = "HRDET Vacuum Temp"
    y_axis_label = 'Vacuum Temp'

    # creates your query
    table = 'FitsHeaderHrs'
    column = 'TEM_VAC'
    logic = " and FileName like 'R%%'"
    sql = "select UTStart, {column} from {table} join FileData using (FileData_Id) " \
          "       where UTStart > '{start_date}' and UTStart <'{end_date}' {logic}"\
        .format(column=column, start_date=start_date, end_date=end_date,
                table=table, logic=logic)
    df = pd.read_sql(sql, db.engine)
    source = ColumnDataSource(df)

    # creates your plot
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


@data_quality(name='hrdet_arc_wave', caption='HRS Arc stability')
def hrdet_arc_wave_plot(start_date, end_date):
    """Return a <div> element with a HRS arc stability plot.

    The plot shows the HRS wavelenght as a function of pixel position for a set of time

    Params:
    -------
    start_date: date
        Earliest date to include in the plot.
    end_date: date
        Earliest date not to include in the plot.

    Return:
    -------
    str:
        A <div> element with the weather downtime plot.
    """
    title = "HRDET Arc Stability"
    y_axis_label = 'Pixel Position'

    # creates your query
    table = 'DQ_HrsArc'
    column = 'x'
    obsmode = 'LOW RESOLUTION'
    wavelength = 6483.08
    logic = " and FileName like 'R%%' and OBSMODE like '{obsmode}' and wavelength={wavelength}"\
        .format(obsmode=obsmode, wavelength=wavelength)
    sql = "select UTStart, {column} from {table} join FileData using (FileData_Id) " \
          "       where UTStart > '{start_date}' and UTStart <'{end_date}' {logic}"\
        .format(column=column, start_date=start_date, end_date=end_date,
                table=table, logic=logic)
    print(sql)
    df = pd.read_sql(sql, db.engine)
    source = ColumnDataSource(df)

    # creates your plot
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
    print(df['UTStart'], df['x'])
    p.scatter(source=source, x='UTStart', y=column)

    p.xaxis[0].formatter = date_formatter

    return p
