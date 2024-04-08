import functools

from flask import make_response, render_template
from print3dstore.errors import RequestException

def error_handler(view):
    @functools.wraps(view)
    def error_handler(**kwargs):
        try:
            return view(**kwargs)
        except RequestException as e:
            return make_response(render_template('error.html', error=e), e.http_code)
        except Exception as unexpected_error:
            return make_response(render_template('error.html', error=unexpected_error), 500)

    return error_handler
