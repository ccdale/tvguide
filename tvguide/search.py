from operator import itemgetter
import sys

from tvguide import log, errorNotify, db
from tvguide.data import channelsById, timeFromTS, hms
from tvguide.models import Schedule, Program, Person, CastMap, Station


def findScheduleForProgram(prog):
    try:
        scheds = Schedule.query.filter(Schedule.programid == prog.programid).all()
        return scheds
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def searchTitle(search):
    try:
        st = Station.query.order_by(Station.channelnumber.asc()).all()
        chans = channelsById(st)
        progs = Program.query.filter(Program.title.like(f"%{search}%")).all()
        log.info(f"search title for {search}")
        oprogs = []
        cn = len(progs)
        if cn > 0:
            log.debug(f"{cn} programs found")
            for prog in progs:
                scheds = findScheduleForProgram(prog)
                cn = len(scheds)
                if cn > 0:
                    log.debug(f"{cn} schedules found for {prog.title}")
                    for sched in scheds:
                        chan = chans[sched.stationid]
                        opd = {"channel": chan.name, "cnum": chan.channelnumber}
                        opd["duration"] = hms(sched.duration)
                        opd["end"] = timeFromTS(sched.airdate + sched.duration)
                        opd["start"] = timeFromTS(sched.airdate)
                        opd["ts"] = sched.airdate  # needed for sorting later on
                        opd["title"] = prog.title
                        opd["shortdesc"] = prog.shortdesc
                        opd["longdesc"] = prog.longdesc
                        oprogs.append(opd)
                    else:
                        log.debug(f"no schedules found for {prog.title}")
        else:
            log.info("no program titles found for {search}")
        f = itemgetter("ts")
        return oprogs.sort(key=f)
        # using itemgetter is cleaner than
        # oprogs.sort(key=lambda item: item.get("ts"))
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)
