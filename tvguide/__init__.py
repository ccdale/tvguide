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

"""TVGuide flask application."""

from datetime import datetime
import logging
import logging.handlers
import os
import sys
from systemd.journal import JournalHandler

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


log = logging.getLogger(__name__)
jlog = JournalHandler()
# syslog = logging.handlers.SysLogHandler(address="/dev/log")
formatter = logging.Formatter("%(levelname)s - %(message)s")
# syslog.setFormatter(formatter)
jlog.setFormatter(formatter)
# log.addHandler(syslog)
log.addHandler(jlog)
log.propagate = False
log.setLevel(logging.INFO)

__version__ = "0.3.40"

db = SQLAlchemy()


def errorRaise(exci, e, omsg=""):
    lineno = exci.tb_lineno
    fname = exci.tb_frame.f_code.co_name
    ename = type(e).__name__
    xmsg = "" if len(omsg) == 0 else f" - {omsg}"
    msg = f"{ename} Exception at line {lineno} in function {fname}: {e}{xmsg}"
    log.error(msg)
    raise


def errorNotify(exci, e, omsg=""):
    lineno = exci.tb_lineno
    fname = exci.tb_frame.f_code.co_name
    ename = type(e).__name__
    xmsg = "" if len(omsg) == 0 else f" - {omsg}"
    msg = f"{ename} Exception at line {lineno} in function {fname}: {e}{xmsg}"
    log.error(msg)
    return msg


def errorExit(exci, e, omsg=""):
    lineno = exci.tb_lineno
    fname = exci.tb_frame.f_code.co_name
    ename = type(e).__name__
    xmsg = "" if len(omsg) == 0 else f" - {omsg}"
    msg = f"{ename} Exception at line {lineno} in function {fname}: {e}{xmsg}"
    log.error(msg)
    sys.exit(1)


def convertTimeString(timestring, dtformat="%Y-%m-%dT%H:%M:%SZ", asts=False):
    try:
        dt = datetime.strptime(timestring, dtformat)
        if asts:
            dt = int(dt.timestamp())
        return dt
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def makeApp(testconfig=None):
    global db
    try:
        log.info(f"creating application version {__version__}")
        # set log level if we are in development
        env = os.environ.get("FLASK_ENV", "production")
        if env == "development":
            log.setLevel(logging.DEBUG)
            log.debug("Debug level logging enabled (development instance).")
        elif env == "production":
            log.setLevel(logging.WARNING)
            log.warning("Warning level logging enabled (production instance).")
        # create and configure the app
        app = Flask("tvguide", instance_relative_config=True)
        app.config.from_mapping(
            SECRET_KEY="dev",
            DATABASE=os.path.join(app.instance_path, "tvguide.db"),
        )
        if testconfig is None:
            # load the instance config, if it exists, when not testing
            app.config.from_pyfile("config.py", silent=True)
        else:
            # load the test config if passed in
            app.config.from_mapping(testconfig)
        # ensure the instance folder exists
        try:
            os.makedirs(app.instance_path)
        except OSError:
            pass

        # initialise the db class
        db.init_app(app)

        with app.app_context():
            from . import auth
            from . import guide

            app.register_blueprint(auth.bp)
            app.register_blueprint(guide.bp)

            # a simple page that says the app is healthy
            @app.route("/health")
            def hello():
                return "OK"

            return app
    except Exception as e:
        errorExit(sys.exc_info()[2], e)
