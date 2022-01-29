import logging
from pathlib import Path
import sys

from tvguide import makeApp, db, log, errorNotify, errorExit
from tvguide.config import Configuration
from tvguide.data import hms, dateFromTS, timeFromTS
from tvguide.models import Schedule, Station, Program

app = makeApp()


def scheduleTest():
    try:
        chanid = 17154  # bbc two
        startdate = "2022-01-29"
        # prog on at 13:30 for 2 hours
        prog = {
            "airdate": 1643463000,
            "duration": 7200,
            "stationid": chanid,
        }
        c = Station.query.filter_by(stationid=chanid).first()
        log.info(f"testing for channel {c.name} on {startdate}")
        duration = 7200
        start = 1643463000
        end = start + duration
        xs = Schedule.query.filter(
            Schedule.stationid == chanid,
            (Schedule.airdate + Schedule.duration) > start,
            Schedule.airdate < end,
        ).all()
        log.info(f"found {len(xs)} progs to replace")
        for s in xs:
            p = Program.query.filter_by(programid=s.programid).first()
            log.info(
                f"{p.title}: {dateFromTS(s.airdate)} {timeFromTS(s.airdate)}: duration: {hms(s.duration)}"
            )
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def dotest():
    try:
        with app.app_context():
            dbpath = Path(app.config["DATABASE"])
            db.create_all()
            scheduleTest()
    except Exception as e:
        errorExit(sys.exc_info()[2], e)


if __name__ == "__main__":
    log.setLevel(logging.DEBUG)
    dotest()
