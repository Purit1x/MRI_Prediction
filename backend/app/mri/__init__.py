from flask import Blueprint

bp = Blueprint('mri', __name__)

from app.mri import routes 