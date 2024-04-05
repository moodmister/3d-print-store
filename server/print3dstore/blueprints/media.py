import os
from flask import Blueprint

bp = Blueprint("media", __name__, static_url_path="/media", static_folder="../media")

