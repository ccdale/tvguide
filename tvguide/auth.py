# Copyright (c) 2021, Christopher Allison
#
#     This file is part of tvguide.
#
#     tvguide is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     tvguide is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with tvguide.  If not, see <http://www.gnu.org/licenses/>.

import sys
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

from tvguide import db, errorNotify
from tvguide.models import User
from tvguide.forms import RegistrationForm, LoginForm

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=("GET", "POST"))
def register():
    try:
        form = RegistrationForm()
        if form.validate_on_submit():
            flash(f"Registered new user: {form.username.data}", "success")
            return redirect(url_for("guide.home"))
        # if request.method == "POST":
        #    u = User()
        #    u.name = request.form["username"]
        #    u.password = generate_password_hash(request.form["password"])
        #    # need to work out what to do here
        #    # to commit the user to the db
        #    # db.add(u)
        #    # db.commit()
        return render_template("auth/register.html", title="Register", form=form)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


@bp.route("/login", methods=("GET", "POST"))
def login():
    try:
        form = LoginForm()
        # if request.method == "POST":
        #     u = User()
        #     u.name = request.form["username"]
        #     u.password = generate_password_hash(request.form["password"])
        #     # need to work out what to do here
        #     # to commit the user to the db
        #     # db.add(u)
        #     # db.commit()
        return render_template("auth/login.html", title="Login", form=form)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)
