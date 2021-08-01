from datetime import datetime

from tvguide.models import Station, Program, Schedule, Schedulemd5, User


def test_station():
    c = Station(stationid=1, name="station 1")
    assert c.name == "station 1"
    assert c.stationid == 1
    assert f"{c}" == "<Station station 1>"


def test_program():
    p = Program(programid=1, title="a program", md5="deadbeef")
    assert f"{p}" == "<Program a program, None/None, None>"


def test_schedule():
    now = datetime.utcnow()
    s = Schedule(programid=1, stationid=1, md5="deadbeef", airdate=now, duration=1)
    assert f"{s}" == f"<Schedule 1/1/{now}/1>"


def test_user():
    u = User(name="chris", password="wibble")
    assert f"{u}" == f"<User None, chris>"
