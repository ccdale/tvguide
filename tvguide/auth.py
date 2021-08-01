import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from tvguide import db
from tvguide.models import User

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=("GET", "POST"))
def register():
    try:
        if request.method == "POST":
            u = User()
            u.name = request.form["username"]
            u.password = generate_password_hash(request.form["password"])
            # need to work out what to do here
            # to commit the user to the db
            db.add(u)
            db.commit()
        return render_template("auth/register.html")
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)
