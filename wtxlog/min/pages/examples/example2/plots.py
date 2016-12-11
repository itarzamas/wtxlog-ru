import pandas as pd

from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.plotting import figure, ColumnDataSource

from app import db
from app.decorators import data_quality


@data_quality(name='weather_downtime', caption='Weather downtime.')
def weather_downtime_plot(start_date, end_date):
    """Return a <div> element with a weather downtime plot.

    The plot shows the downtime for the period between start_date (inclusive) and end_date (exclusive).

    Params:
    -------
    start_date: str
        Earliest date to include in the plot.
    end_date: str
        Earliest date not to include in the plot.

    Return:
    -------
    str:
        A <div> element with the weather downtime plot.
    """

    return _downtime_plot('TimeLostToWeather', 'Weather Downtime', start_date, end_date)


@data_quality(name='technical_downtime', caption='Downtime due to technical problems.')
def technical_downtime_plot(start_date, end_date):
    """Return a <div> element with a plot displaying the downtime due to technical problems.

    The plot shows the downtime for the period between start_date (inclusive) and end_date (exclusive).

    Params:
    -------
    start_date: str
        Earliest date to include in the plot.
    end_date: str
        Earliest date not to include in the plot.

    Return:
    -------
    str:
        A <div> element with the weather downtime plot.
    """

    return _downtime_plot('TimeLostToProblems', 'Downtime due to Technical Problems', start_date, end_date)


def _downtime_plot(downtime_column, title, start_date, end_date):
    """Return a <div> element with a downtime plot.

    The plot shows the downtime for the period between start_date (inclusive) and end_date (exclusive).

    Params:
    -------
    downtime_column: str
        Name of the column in the NightInfo table whose data shall be used.
    title: str
        Plot title.
    start_date: str
        Earliest date to include in the plot.
    end_date: str
        Earliest date not to include in the plot.

    Return:
    -------
    bokeh.model.Model:
        The downtime plot.
    """

    sql = 'SELECT Date, {downtime_column} FROM NightInfo' \
          '       WHERE Date >= \'{start_date}\' AND Date < \'{end_date}\' AND {downtime_column} IS NOT NULL' \
        .format(start_date=start_date, end_date=end_date, downtime_column=downtime_column)
    df = pd.read_sql(sql, db.engine)
    source = ColumnDataSource(df)

    date_formatter = DatetimeTickFormatter(formats=dict(hours=['%e %b %Y'],
                                                        days=['%e %b %Y'],
                                                        months=['%e %b %Y'],
                                                        years=['%e %b %Y']))

    p = figure(title=title,
               x_axis_label='Date',
               y_axis_label='Downtime (seconds)',
               x_axis_type='datetime')
    p.scatter(source=source, x='Date', y='{downtime_column}'.format(downtime_column=downtime_column))

    p.xaxis[0].formatter = date_formatter

    return p
