from flask import current_app, render_template

from . import min


@min.errorhandler(500)
def internal_server_error(e):
    current_app.logger.error(str(e), exc_info=1)
    return render_template('500.html'), 500

@min.errorhandler(404)

def file_not_found_error(e):
      return render_template('errors/404.html'), 404
  


@min.errorhandler(Exception)
def exception_raised(e):
    current_app.logger.error(str(e), exc_info=1)
    return render_template('500.html'), 500
