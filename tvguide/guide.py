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
from tvguide.data import channelSchedule, timeLine, generateEdits
from tvguide.search import searchTitle, searchPerson, searchPeopleProgs

bp = Blueprint("guide", __name__)

log.setLevel(logging.DEBUG)


@bp.route("/", methods=["GET"])
def home():
    try:
        kwargs = {
            "oprogs": [],
            "lenprogs": 0,
            "people": [],
            "lenpeople": 0,
            "personprogs": [],
            "lenpersonprogs": 0,
        }
        return render_template("tvhome.html", **kwargs)
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
        st = (
            Station.query.filter_by(getdata=1)
            .order_by(Station.channelnumber.asc())
            .all()
        )
        return render_template("tvchannels.html", chans=st)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


@bp.route("/channel", methods=["GET"])
def channel():
    try:
        chanid = "0" if "chanid" not in request.args else request.args["chanid"]
        offset = 0 if "offset" not in request.args else int(request.args["offset"])
        p, today, days = channelSchedule(chanid, offset=offset)
        xchan = Station.query.filter_by(stationid=request.args["chanid"]).first()
        return render_template(
            "channel.html", progs=p, chan=xchan, today=today, days=days
        )
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


@bp.route("/channeledit", methods=["GET", "POST"])
def channeledit():
    try:
        st = Station.query.order_by(Station.channelnumber.asc()).all()
        if request.method == "POST":
            generateEdits(request.form, st)
            st = Station.query.order_by(Station.channelnumber.asc()).all()
        return render_template("channelform.html", chans=st)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


@bp.route("/searchtitle", methods=["POST"])
def searchtitle():
    try:
        oprogs = people = pprogs = []
        if "searchtitleinput" in request.form:
            oprogs = searchTitle(request.form["searchtitleinput"])
        if "searchpeopleinput" in request.form:
            people = searchPerson(request.form["searchpeopleinput"])
        if "searchprogspeopleinput" in request.form:
            pprogs = searchPeopleProgs(request.form["searchprogspeopleinput"])
        kwargs = {
            "oprogs": oprogs,
            "lenprogs": len(oprogs),
            "people": people,
            "lenpeople": len(people),
            "personprogs": pprogs,
            "lenpersonprogs": len(pprogs),
        }
        return render_template("tvhome.html", **kwargs)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


@bp.route("/searchperson", methods=["GET"])
def searchperson():
    try:
        personid = request.args.get("personid", None)
        kwargs = {"pprogs": [], "lenpprogs": 0}
        kwargs = {
            "oprogs": [],
            "lenprogs": 0,
            "people": [],
            "lenpeople": 0,
            "personprogs": [],
            "lenpersonprogs": 0,
        }
        return render_template("tvhome.html", **kwargs)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


@bp.route("/grid", methods=["GET"])
def grid():
    try:
        return render_template("tvhome.html")
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)
