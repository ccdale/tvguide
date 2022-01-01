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

bp = Blueprint("guide", __name__)


@bp.route("/", methods=["GET"])
def home():
    try:
        return render_template("tvhome.html")
    except Exception as e:
        return errorNotify(sys.exc_info()[2], e)


@bp.route("/about", methods=["GET"])
def about():
    try:
        return render_template("tvabout.html")
    except Exception as e:
        return errorNotify(sys.exc_info()[2], e)
