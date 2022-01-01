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
import os
from pathlib import Path
import sys

from tvguide import makeApp, db, log, errorNotify, errorExit
from tvguide.config import Configuration
from tvguide.credential import Credential
from tvguide.sdapi import SDApi


app = makeApp()


def makeSD(cfg):
    try:
        keys = ["username", "token", "tokenexpires"]
        kwargs = {}
        for key in keys:
            kwargs[key] = cfg.get(key)
        cred = Credential(kwargs["username"], cfg.get("host"))
        kwargs["password"] = cred.getPassword()
        kwargs["debug"] = True
        sd = SDApi(**kwargs)
        sd.apiOnline()
        if not sd.online:
            raise Exception("Schedules Direct does not appear to be online.")
        return sd
    except Exception as e:
        errorExit(sys.exc_info()[2], e)


def updateDB():
    try:
        with app.app_context():
            dbpath = Path(app.config["DATABASE"])
            log.debug(f"looking for database at: {dbpath}")
            if not dbpath.is_file():
                raise Exception(f"failed to find a database at: {dpbath}")
        log.debug(f"I'm here so the dbpath must be correct {dbpath}")
        cfg = Configuration(appname="tvguide")
        log.debug(cfg.config)
        sd = makeSD(cfg)
        log.debug("Alls good, sd is online")
        # code goes here
        cfg.update("token", sd.token)
        cfg.update("tokenexpires", sd.tokenexpires)
        log.debug("writing config")
        cfg.writeConfig()
    except Exception as e:
        errorExit(sys.exc_info()[2], e)


if __name__ == "__main__":
    os.environ["FLASK_ENV"] = "development"
    log.setLevel(logging.DEBUG)
    updateDB()
