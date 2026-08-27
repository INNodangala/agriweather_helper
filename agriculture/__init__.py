"""
Agriculture Blueprint for AgriWeather Helper.
"""

from flask import Blueprint

agriculture_bp = Blueprint('agriculture', __name__,
                           url_prefix='/agriculture',
                           template_folder='templates')

from agriculture.routes import dashboard, farm, scan, marketplace, finance  # noqa
