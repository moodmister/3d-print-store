from flask import session
from wtforms import Form
from wtforms.csrf.session import SessionCSRF
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class CsrfBaseForm(Form):
    class Meta:
        csrf = True
        csrf_class = SessionCSRF
        csrf_secret = bytearray(os.getenv("SECRET_KEY"), "utf-8")
        csrf_time_limit = timedelta(minutes=20)

        @property
        def csrf_context(self):
            return session

