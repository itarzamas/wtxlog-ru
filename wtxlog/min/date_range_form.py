from flask import render_template
from flask_wtf import Form
from wtforms.fields import DateField, SubmitField
from wtforms.validators import DataRequired


class DateRangeForm(Form):
    """A form for entering a date range.

    Default values can be supplied for both the start and date of the range. These will be used if the field value
    isn't set from the GET or POST request parameters.

    CSRF is disabled for this form.

    Params:
    -------
    default_start_date: date
        Default to use as start date.
    default_end_date: date
        Default to use as end date.
    """

    start_date = DateField('Start', validators=[DataRequired()])
    end_date = DateField('End', validators=[DataRequired()])
    submit = SubmitField('Query')

    def __init__(self, default_start_date=None, default_end_date=None):
        Form.__init__(self, csrf_enabled=False)

        # change empty fields to default values
        if not self.start_date.data and default_start_date:
            self.start_date.data = default_start_date
        if not self.end_date.data and default_end_date:
            self.end_date.data = default_end_date

    def html(self):
        return render_template('data_quality/date_range_form.html', form=self)
