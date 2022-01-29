from datetime import date
from datetime import datetime
import sys
import time

from flask_sqlalchemy import get_debug_queries

from tvguide import log, errorNotify, db
from tvguide.models import Schedule, Program, Person, CastMap, Station


def hms(dur):
    try:
        hours = int(dur / 3600)
        mins = int((dur % 3600) / 60)
        return f"{hours:0>2}:{mins:0>2}"
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def timeFromTS(ts):
    try:
        d = datetime.fromtimestamp(ts)
        log.debug(f"timeFromTS: {ts=}, {d=}")
        return d.strftime("%H:%M")
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def dateFromTS(ts):
    try:
        d = date.fromtimestamp(ts)
        dord = {
            "01": "st",
            "02": "nd",
            "03": "rd",
            "21": "st",
            "22": "nd",
            "23": "rd",
            "31": "st",
        }
        sday = d.strftime("%d")
        xord = "th" if sday not in dord else dord[sday]
        smon = d.strftime("%b")
        sdow = d.strftime("%a")
        return f"{sdow} {int(sday)}{xord} {smon}, {d.strftime('%Y')}"
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def dayOfWeek(ts, offset=0):
    try:
        d = date.fromtimestamp(ts + offset)
        return d.strftime("%a")
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def timeLine():
    try:
        d = date.today()
        dts = datetime(d.year, d.month, d.day, 6)
        ts = dts.timestamp()
        oneday = 86400
        end = 7 * oneday
        days = [(i, dayOfWeek(ts, i)) for i in range(0, end, oneday)]
        return days
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
        }
        return op
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def channelSchedule(chanid, offset=0, duration=86400):
    try:
        xstart = int(time.time()) + offset
        scheds = (
            Schedule.query.filter(
                Schedule.stationid == chanid,
                Schedule.airdate > xstart,
                Schedule.airdate < xstart + duration,
            )
            .order_by(Schedule.airdate)
            .all()
        )
        progs = []
        gotdate = today = False
        for sched in scheds:
            if not gotdate:
                today = dateFromTS(sched.airdate)
                days = timeLine()
                gotdate = True
            p = Program.query.filter_by(programid=sched.programid).first()
            progs.append(copyProgSched(p, sched))
        return (progs, today, days)
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


def doSearch(search):
    try:
        pass
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)
