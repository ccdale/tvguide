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
from tvguide.models import (
    Schedule,
    Schedulemd5,
    Station,
    Person,
    Program,
    Logo,
    CastMap,
)
from tvguide.sdapi import SDApi


app = makeApp()


def getRMap(xmap):
    try:
        rmap = {}
        for xm in xmap:
            rmap[int(xm["stationID"])] = int(xm["channel"])
        return rmap
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def updatePrograms(sd, plist):
    """Retrieves information for each program in the list"""
    try:
        if len(plist) == 0:
            raise Exception("updatePrograms: received empty list")
        progs = sd.getPrograms(plist)
        [addUpdateProgram(prog) for prog in progs]
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def extractString(xlist, key):
    try:
        for item in xlist:
            if key in item:
                return item[key]
        log.warning(f"{key} not found in {xlist}")
        return None
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def extractSeries(mdata):
    try:
        series = episode = 0
        for item in mdata:
            series = int(item["Gracenote"]["season"])
            episode = int(item["Gracenote"]["episode"])
        return (series, episode)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def setProgData(eprog, prog):
    try:
        eprog.md5 = prog["md5"]
        eprog.title = extractString(prog["titles"], "title120")
        eprog.episodetitle = prog["episodeTitle150"]
        eprog.shortdesc = extractString(prog["descriptions"], "description1000")
        eprog.originalairdate = prog["originalAirDate"]
        eprog.series, prog.episode = extractSeries(prog["metadata"])
        return eprog
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def addUpdatePersonMap(personid, programid, role, billingorder):
    try:
        cm = CastMap.query.filter_by(
            programid=programid, personid=personid, role=role, billingorder=billingorder
        ).first()
        if not cm:
            kwargs = {
                "programid": programid,
                "personid": personid,
                "role": role,
                "billingorder": billingorder,
            }
            cm = CastMap(**kwargs)
            db.session.add(cm)
            db.session.commit()
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def addUpdatePerson(person, programid):
    try:
        log.debug(f"addUpdatePerson: {person['name']}")
        per = Person.query.filter_by(personid=person["personId"]).first()
        if not per:
            log.debug(f"storing person: {person['name']}")
            kwargs = {
                "personid": person["personId"],
                name: person["name"],
                nameid: person["nameId"],
            }
            per = Person(**kwargs)
            db.session.add(per)
            db.session.commit()
        addUpdatePersonMap(
            per.personid, programid, person["role"], person["billingorder"]
        )
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def addUpdateProgram(prog):
    """Updates/Creates one program information

    see
    https://github.com/SchedulesDirect/JSON-Service/wiki/API-20141201#download-program-information

    """
    try:
        progid = prog["programID"]
        log.debug(f"addUpdateProg: {progid}")
        eprog = Program.query.filter_by(programid=progid).first()
        if eprog:
            log.debug(f"{progid} already exists")
            if eprog.md5 == prog["md5"]:
                log.debug("md5 match")
                return None
            else:
                log.debug(f"md5 mismatch: storing {progid}")
                eprog = setProgData(eprog, prog)
                db.session.commit()
        else:
            log.debug(f"new program: {progid}")
            kwargs = {"programid": progid}
            kwargs["title"] = extractString(prog["titles"], "title120")
            log.debug(f"title: {kwargs['title']}")
            kwargs["episodetitle"] = prog["episodeTitle150"]
            kwargs["shortdesc"] = extractString(prog["descriptions"], "description1000")
            kwargs["originalairdate"] = prog["originalAirDate"]
            kwargs["series"], kwargs["episode"] = extractSeries(prog["metadata"])
            eprog = Program(**kwargs)
            db.session.add(eprog)
            db.session.commit()
        [addUpdatePerson(item, programid) for item in prog["cast"]]
        [addUpdatePerson(item, programid) for item in prog["crew"]]
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def addUpdateSMD5(sd, smd5, chanid, xdate):
    try:
        md5 = Schedulemd5.query.filter_by(md5=smd5["md5"]).first()
        if md5:
            return False
        sdate = f"{xdate}T00:00:00Z"
        datets = sd.getTimeStamp(sdate)
        kwargs = {
            "md5": smd5["md5"],
            "stationid": chanid,
            "datets": datets,
            "modified": sd.getTimeStamp(smd5["lastModified"]),
        }
        md5 = Schedulemd5(**kwargs)
        db.session.add(md5)
        db.session.commit()
        return True
    except Exception as e:
        msg = f"{e}\n{smd5=}, {chanid=}, {xdate=}\n"
        msg += f"{kwargs=}"
        errorExit(sys.exc_info()[2], msg)


def schedulesMd5(sd):
    try:
        retrieve = {}
        clist = Station.query.all()
        slist = [x.stationid for x in clist]

        # testing
        slist = [87840, 50716]
        # testing

        smd5 = sd.getScheduleMd5(slist)
        for chan in smd5:
            log.debug(f"scheduleMd5: {chan=}")
            for xdate in smd5[chan]:
                log.debug(f"scheduleMd5: {xdate=}")
                if addUpdateSMD5(sd, smd5[chan][xdate], chan, xdate):
                    if chan not in retrieve:
                        retrieve[chan] = []
                    retrieve[chan].append(xdate)
        log.debug(f"sheduleMd5 returns: {retrieve=}")
        return retrieve
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def addSchedule(sd, sched):
    try:
        plist = []
        chanid = sched["stationID"]
        c = Station.query.filter_by(stationid=chanid).first()
        log.info(
            f"Updating schedule for channel {c.name} with {len(sched['programs'])} programs"
        )
        for prog in sched["programs"]:
            p = Program.query.filter_by(
                programid=prog["programID"], md5=prog["md5"]
            ).first()
            if not p:
                plist.append(prog["programID"])
            kwargs = {"md5": prog["md5"]}
            kwargs["programid"] = prog["programID"]
            kwargs["stationid"] = chanid
            kwargs["airdate"] = sd.getTimeStamp(prog["airDateTime"])
            kwargs["duration"] = int(prog["duration"])
            s = Schedule(**kwargs)
            db.session.add(s)
        db.session.commit()
        log.info(f"require downloading of {len(plist)} programs for {c.name}")
        updatePrograms(sd, plist)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def schedules(sd):
    try:
        log.info("Retrieving schedule hashes")
        xdat = schedulesMd5(sd)
        log.info(f"require schedules for {len(xdat)} channels")
        if len(xdat) > 0:
            chans = [
                {"stationID": str(chanid), "date": xdat[chanid]} for chanid in xdat
            ]
            scheds = sd.getSchedules(chans)
            log.info("Updating new schedules")
            for sched in scheds:
                addSchedule(sd, sched)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def updateChannels(linupdata):
    try:
        # with open("/home/chris/tmp/lineups.json", "r") as ifn:
        #     xdict = json.load(ifn)
        # xdict = json.loads(linupdata)
        xdict = linupdata
        rmap = getRMap(xdict["map"])
        labels = ["name", "callsign"]
        llabs = ["height", "width", "category", "md5", "source"]
        existstation = createdstation = 0
        existlogo = createdlogo = 0
        for station in xdict["stations"]:
            stationid = int(station["stationID"])
            if not Station.query.filter_by(stationid=stationid).first():
                kwargs = {key: station[key] for key in labels}
                kwargs["stationid"] = stationid
                kwargs["channelnumber"] = rmap[stationid]
                stat = Station(**kwargs)
                # log.info(f"Inserting {stat=}")
                db.session.add(stat)
                createdstation += 1
            else:
                existstation += 1
            if "stationLogo" in station:
                for logo in station["stationLogo"]:
                    if not Logo.query.filter_by(md5=logo["md5"]).first():
                        kwargs = {key: logo[key] for key in llabs}
                        kwargs["url"] = logo["URL"]
                        ologo = Logo(**kwargs)
                        # log.info(f"Inserting {ologo}")
                        db.session.add(ologo)
                        createdlogo += 1
                    else:
                        existlogo += 1
        db.session.commit()
        log.info(
            f"Channels inserted: {createdstation}, Existing Channels: {existstation}"
        )
        log.info(f"Logos inserted: {createdlogo}, Existing Logos: {existlogo}")
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def linupRefresh(sd, cfg):
    try:
        for lineup in sd.lineups:
            if sd.getTimeStamp(lineup["modified"]) > cfg.get("lineupdate", 0):
                log.info(f"Lineup changes detected: refreshing lineup {lineup}")
                lineupdata = sd.getLineup(lineup["lineup"])
                updateChannels(lineupdata)
                cfg.update("lineupdate", sd.getTimeStamp(lineup["modified"]))
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
            # if we've changed the models then (re)create the tables
            db.create_all()
            if not dbpath.is_file():
                raise Exception(f"failed to find a database at: {dbpath}")
            log.debug(f"I'm here so the dbpath must be correct {dbpath}")
            cfg = Configuration(appname="tvguide")
            log.debug(cfg.config)
            sd = makeSD(cfg)
            log.debug("Alls good, sd is online")

            linupRefresh(sd, cfg)

            schedules(sd)

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
