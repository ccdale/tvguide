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

import logging
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

from tvguide import db, log, errorNotify
from tvguide.models import Station

bp = Blueprint("guide", __name__)

log.setLevel(logging.DEBUG)


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


@bp.route("/channels", methods=["GET"])
def channels():
    try:
        st = Station.query.all()
        return render_template("tvchannels.html", st=st)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


@bp.route("/channel", methods=["GET"])
def channel():
    try:
        chanid = "" if "chanid" not in request.args else request.args["chanid"]
        return render_template("tvchannel.html", chanid=chanid)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


@bp.route("/grid", methods=["GET"])
def grid():
    try:
        return render_template("tvhome.html")
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)
