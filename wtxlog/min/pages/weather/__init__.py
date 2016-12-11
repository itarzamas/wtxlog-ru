import datetime

from app.main.data_quality import default_data_quality_content_for_date_range


def title():
    return 'Example 2'


def content():
    return default_data_quality_content_for_date_range(__package__,
                                                       datetime.date.today() - datetime.timedelta(days=180),
                                                       datetime.date.today())
