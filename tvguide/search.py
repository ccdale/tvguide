from operator import itemgetter
import sys

from tvguide import log, errorNotify, db
from tvguide.data import channelsById, timeFromTS, hms, dateFromTS
from tvguide.models import Schedule, Program, Person, CastMap, Station


def findScheduleForProgram(prog):
    try:
        scheds = Schedule.query.filter(Schedule.programid == prog.programid).all()
        return scheds
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def schedulesForProgList(progs):
    try:
        st = Station.query.order_by(Station.channelnumber.asc()).all()
        chans = channelsById(st)
        oprogs = []
        cn = 0 if progs is None else len(progs)
        if cn > 0:
            log.debug(f"{cn} programs found")
            for prog in progs:
                scheds = findScheduleForProgram(prog)
                cn = 0 if scheds is None else len(scheds)
                if cn > 0:
                    log.debug(f"{cn} schedules found for {prog.title}")
                    for sched in scheds:
                        chan = chans[sched.stationid]
                        opd = {"channel": chan.name, "cnum": chan.channelnumber}
                        opd["duration"] = hms(sched.duration)
                        opd["end"] = timeFromTS(sched.airdate + sched.duration)
                        opd["date"] = dateFromTS(sched.airdate)
                        opd["start"] = timeFromTS(sched.airdate)
                        opd["ts"] = sched.airdate  # needed for sorting later on
                        opd["title"] = prog.title
                        opd["shortdesc"] = prog.shortdesc
                        opd["longdesc"] = prog.longdesc
                        oprogs.append(opd)
                    else:
                        log.debug(f"no schedules found for {prog.title}")
        if len(oprogs):
            f = itemgetter("ts")
            oprogs.sort(key=f)
            log.debug(f"after sorting: {type(oprogs)}")
        return oprogs
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def searchTitle(search):
    try:
        if search is not None and len(search) > 3:
            progs = Program.query.filter(Program.title.like(f"%{search}%")).all()
            oprogs = schedulesForProgList(progs)
        else:
            oprogs = []
        return oprogs
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def searchPerson(search):
    try:
        if search is not None and len(search) > 3:
            persons = Person.query.filter(Person.name.like(f"%{search}%")).all()
            op = [
                {"personid": x.personid, "name": x.name, "nameid": x.nameid}
                for x in persons
            ]
        else:
            op = []
        return op
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def searchPeopleProgs(search):
    try:
        if search is not None and len(search) > 3:
            pass
        else:
            op = []
        return op
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)
