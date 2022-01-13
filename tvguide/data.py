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
