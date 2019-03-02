from flask import Blueprint

blueprint = Blueprint('core', __name__)

from .controller import routes
