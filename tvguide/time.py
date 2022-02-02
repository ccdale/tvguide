from datetime import date
from datetime import datetime
import sys
import time

from tvguide import log, errorNotify


def hms(dur):
    try:
        hours = int(dur / 3600)
        mins = int((dur % 3600) / 60)
        h = "" if hours == 0 else f"{hours}h"
        m = "" if mins == 0 else f"{mins}m"
        return f"{h} {m}".strip()
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


def timeLine(ndays=14):
    try:
        d = date.today()
        dts = datetime(d.year, d.month, d.day, 6)
        ts = dts.timestamp()
        oneday = 86400
        end = ndays * oneday
        days = [(i, dayOfWeek(ts, i)) for i in range(0, end, oneday)]
        return days
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def alignTime(offset, ts=None, alignment=3600):
    try:
        now = int(time.time()) if ts is None else ts
        then = now + offset
        align = then - (then % alignment)
        return align
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)
