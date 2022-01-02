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

import json
import logging
import os
from pathlib import Path
from pprint import pprint
import sys

from tvguide import makeApp, db, log, errorNotify, errorExit
from tvguide.config import Configuration
from tvguide.credential import Credential
from tvguide.models import Schedule, Schedulemd5, Station, Person, Program, Logo
from tvguide.sdapi import SDApi


app = makeApp()


def writeChanMap():
    try:
        with open("/home/chris/tmp/lineups.json", "r") as ifn:
            xdict = json.load(ifn)
        xmap = xdict["map"]
        rmap = {}
        for xm in xmap:
            rmap[xm["stationID"]] = xm["channel"]
        pprint(rmap)
        with open("/home/chris/tmp/rmap.json", "w") as ofn:
            json.dump(rmap, ofn)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def getRMap(xmap):
    try:
        rmap = {}
        for xm in xmap:
            rmap[int(xm["stationID"])] = int(xm["channel"])
        return rmap
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def createChannels():
    try:
        with open("/home/chris/tmp/lineups.json", "r") as ifn:
            xdict = json.load(ifn)
        rmap = getRMap(xdict["map"])
        labels = ["name", "callsign"]
        llabs = ["height", "width", "category", "md5", "source"]
        for station in xdict["stations"]:
            stationid = int(station["stationID"])
            if not Station.query.filter_by(stationid=stationid).first():
                kwargs = {key: station[key] for key in labels}
                kwargs["stationid"] = stationid)
                kwargs["channelnumber"] = rmap[stationid]
                stat = Station(**kwargs)
                log.info(f"Inserting {stat=}")
                db.session.add(stat)
            for logo in xdict["stationLogo"]:
                if not Logo.query.filter_by(md5=logo["md5"]).first():
                    kwargs = {key: logo[key] for key in llabs}
                    kwargs["url"] = logo["URL"]
                    ologo = Logo(**kwargs)
                    log.info(f"Inserting {ologo}")
                    db.session.add(ologo)
        db.session.commit()
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def linupRefresh(sd):
    try:
        for lineup in sd.lineups:
            print(lineup)
            sd.getLineup(lineup["lineup"])
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def makeSD(cfg):
    try:
        keys = ["username", "token", "tokenexpires", "appname"]
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
        # linupRefresh(sd)
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
            createChannels()
        # log.debug(f"I'm here so the dbpath must be correct {dbpath}")
        # cfg = Configuration(appname="tvguide")
        # log.debug(cfg.config)
        # sd = makeSD(cfg)
        # log.debug("Alls good, sd is online")
        # # code goes here
        # cfg.update("token", sd.token)
        # cfg.update("tokenexpires", sd.tokenexpires)
        # log.debug("writing config")
        # cfg.writeConfig()
    except Exception as e:
        errorExit(sys.exc_info()[2], e)


if __name__ == "__main__":
    os.environ["FLASK_ENV"] = "development"
    log.setLevel(logging.DEBUG)
    # createChannels()
    # writeChanMap()
    updateDB()
