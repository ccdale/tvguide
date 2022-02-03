from datetime import date
from datetime import datetime
import sys
import time

from flask_sqlalchemy import get_debug_queries

from tvguide import log, errorNotify, db
from tvguide.models import Schedule, Program, Person, CastMap, Station
from tvguide.time import hms, timeFromTS, dateFromTS, timeLine, alignTime, dayOfWeek


def displayIfNotZero(v, label):
    try:
        ret = "" if v == 0 else f"{v}{label}"
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def seriesString(series, episode):
    try:
        if series is None and episode is None:
            return ""
        if series is None:
            return episode
        return f"{series} / {episode}"
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def copyProgSched(prog, sched):
    try:
        op = {
            "programid": prog.programid,
            "title": prog.title,
            "episodetitle": prog.episodetitle,
            "shortdesc": prog.shortdesc,
            "longdesc": prog.longdesc,
            "seriesstr": seriesString(prog.series, prog.episode),
            "series": "" if prog.series is None else prog.series,
            "episode": "" if prog.episode is None else prog.episode,
            "airdate": timeFromTS(sched.airdate),
            "duration": hms(sched.duration),
            "iduration": sched.duration,
            "endtime": timeFromTS(sched.airdate + sched.duration),
        }
        return op
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def channelSchedule(chanid, offset=0, duration=86400):
    try:
        xmin = 86400
        # xstart = int(time.time()) + offset
        xstart = alignTime(offset)
        # find programmes that end after the start point
        # and begin before the end point
        scheds = (
            Schedule.query.filter(
                Schedule.stationid == chanid,
                Schedule.airdate + Schedule.duration > xstart,
                Schedule.airdate < xstart + duration,
            )
            .order_by(Schedule.airdate)
            .all()
        )
        progs = []
        gotdate = today = dow = False
        for sched in scheds:
            if not gotdate:
                today = dateFromTS(sched.airdate)
                days = timeLine(7)
                dow = dayOfWeek(sched.airdate)
                gotdate = True
            p = Program.query.filter_by(programid=sched.programid).first()
            if sched.duration < xmin:
                xmin = sched.duration
            progs.append(copyProgSched(p, sched))
        return (progs, today, days, dow, xmin)
    except Exception as e:
        log.debug(get_debug_queries())
        errorNotify(sys.exc_info()[2], e)


def getNumeric(txt, findfrom="_"):
    try:
        return int(txt[txt.index(findfrom) + 1 :])
    except ValueError as e:
        log.error(f"input has no numeric component: {txt=}, {findfrom=}")
        return 0
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def channelsById(stations):
    try:
        op = {}
        for chan in stations:
            op[chan.stationid] = chan
        return op
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def checkFavourite(frmel, chan):
    try:
        # we only get form elements when the box is checked
        # log.debug(f"testing for 'fav' in element {frmel}")
        if frmel.startswith("fav"):
            log.debug(f"favourite set on channel {chan.name}")
            if chan.favourite != 1:
                log.debug(f"adding favourite {chan.name}")
                chan.favourite = 1
                # automatically turn on getdata for a favourite channel
                chan.getdata = 1
                db.session.commit()
            else:
                log.debug(f"favourite already set for {chan.name} in db.")
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def checkGetData(frmel, chan):
    try:
        if frmel.startswith("gd"):
            if chan.getdata != 1:
                log.debug(f"adding getdata {chan.name}")
                chan.getdata = 1
                db.session.commit()
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def setZero(xchans):
    try:
        for chan in xchans:
            changed = False
            if chan.favourite != 0:
                chan.favourite = 0
                changed = True
                log.debug(f"unsetting favourite for {chan.name}")
            elif chan.getdata != 0:
                chan.getdata = 0
                changed = True
                log.debug(f"unsetting getdata for {chan.name}")
            if changed:
                db.session.commit()
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def generateEdits(form, stations):
    try:
        updated = []
        chans = channelsById(stations)
        for key in form:
            sid = getNumeric(key)
            checkGetData(key, chans[sid])
            checkFavourite(key, chans[sid])
            updated.append(sid)
        log.debug(f"{len(updated)} channels changed")
        xchans = [chans[x] for x in chans if chans[x].stationid not in updated]
        log.debug(f"checking {len(xchans)} channels for zero (of {len(chans)}")
        setZero(xchans)
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def gridProgs(offset=0, width=7200):
    try:
        grid = []
        xmin = 86400
        kwargs = {"offset": offset, "duration": width}
        stations = (
            Station.query.filter_by(favourite=1)
            .order_by(Station.channelnumber.asc())
            .all()
        )
        for station in stations:
            progs, today, days, cmin = channelSchedule(station.stationid, **kwargs)
            if cmin < xmin:
                xmin = cmin
            gridline = {
                "channel": station,
                "programmes": progs,
                "today": today,
                "days": days,
            }
            grid.append(gridline)
        return grid, xmin
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)
