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

"""Database module for tvguide."""

# import os
# import sqlite3
# import sys
#
# import click
# from flask import current_app, g
# from flask_cli import with_appcontext

from tvguide import db


class Station(db.Model):
    stationid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    callsign = db.Column(db.String(64), nullable=True)
    broadcastlang = db.Column(db.String(4), nullable=True)
    descriptionlang = db.Column(db.String(4), nullable=True)
    logid = db.Column(db.Integer, nullable=True)
    source = db.Column(db.String(64), nullable=True)
    channelnumber = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"<Station {self.name}>"


class Person(db.Model):
    personid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    nameid = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"<Person {self.name}>"


class Program(db.Model):
    programid = db.Column(db.String(32), primary_key=True)
    md5 = db.Column(db.String(32), unique=True)
    title = db.Column(db.String(256), index=True)
    episodetitle = db.Column(db.String(256), nullable=True)
    shortdesc = db.Column(db.String(1024), nullable=True)
    longdesc = db.Column(db.String(4096), nullable=True)
    originalairdate = db.Column(db.String(32), nullable=True)
    series = db.Column(db.Integer, nullable=True)
    episode = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return (
            f"<Program {self.title}, {self.series}/{self.episode}, {self.episodetitle}>"
        )


class Schedule(db.Model):
    md5 = db.Column(db.String(32), primary_key=True)
    programid = db.Column(
        db.String(32), db.ForeignKey("program.programid"), nullable=False
    )
    stationid = db.Column(
        db.Integer, db.ForeignKey("station.stationid"), nullable=False
    )
    airdate = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Schedule {self.programid}/{self.stationid}/{self.airdate}/{self.duration}>"


class Schedulemd5(db.Model):
    md5 = db.Column(db.String(32), primary_key=True)
    stationid = db.Column(db.Integer)
    datestr = db.Column(db.String(64))
    datets = db.Column(db.Integer)
    modified = db.Column(db.Integer)

    def __repr__(self):
        return f"<Schedulemd5 {self.stationid}/{self.md5}/{self.modified}>"
