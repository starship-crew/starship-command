from flask import Blueprint

admin_bp = Blueprint(
    "admin_bp",
    __name__,
    url_prefix="/dashboard",
    template_folder="templates",
    static_folder="static",
)
