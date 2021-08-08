from datetime import datetime

from tvguide.models import Station, Program, Schedule, Schedulemd5, User


def test_station():
    c = Station(stationid=1, name="station 1")
    assert c.name == "station 1"
    assert c.stationid == 1
    assert f"{c}" == "Station(name='station 1')"


def test_program():
    p = Program(programid=1, title="a program", md5="deadbeef")
    assert (
        f"{p}"
        == "Program(title='a program', series=None, episode=None, episodetitle='None')"
    )


def test_schedule():
    now = datetime.utcnow()
    s = Schedule(programid=1, stationid=1, md5="deadbeef", airdate=now, duration=1)
    assert (
        f"{s}"
        == f"Schedule(programid='1', stationid=1, md5='deadbeef', airdate={now}, duration=1)"
    )


def test_schedulemd5():
    now = datetime.utcnow()
    s = Schedulemd5(md5="deadbeef", stationid=12, datestr=now, datets=1, modified=now)
    assert f"{s}" == f"Schedulemd5(stationid=12, md5='deadbeef', modified={now})"


def test_user():
    u = User(name="chris", password="wibble")
    assert f"{u}" == f"User(uid=None, name='chris')"
