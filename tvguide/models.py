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
    getdata = db.Column(db.Integer, nullable=True, default=1)
    favourite = db.Column(db.Integer, nullable=True, default=0)

    def __repr__(self):
        return f"Station(name='{self.name}')"


class Person(db.Model):
    personid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    nameid = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"Person(name='{self.name}')"


class Genre(db.Model):
    name = db.Column(db.String(64), primary_key=True)

    def __repr__(self):
        return f"Genre(name='{self.name}')"


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
        return f"Program(title='{self.title}', series={self.series}, episode={self.episode}, episodetitle='{self.episodetitle}')"


class GenreMap(db.Model):
    programid = db.Column(
        db.String(32),
        db.ForeignKey("program.programid"),
        nullable=False,
        primary_key=True,
    )
    genre = db.Column(
        db.String(64), db.ForeignKey("genre.name"), nullable=False, primary_key=True
    )

    def __repr__(self):
        return f"GenreMap(programid={self.programid}, genre={self.genre}"


class CastMap(db.Model):
    programid = db.Column(
        db.String(32),
        db.ForeignKey("program.programid"),
        nullable=False,
        primary_key=True,
    )
    personid = db.Column(
        db.Integer, db.ForeignKey("person.personid"), nullable=False, primary_key=True
    )
    role = db.Column(db.String(64), nullable=False)
    billingorder = db.Column(db.String(10), nullable=True)

    def __repr__(self):
        return f"CastMap(programid={self.programid}, personid={self.personid}, role={self.role}, billingorder={self.billingorder})"


class Schedule(db.Model):
    md5 = db.Column(db.String(32), nullable=False)
    programid = db.Column(
        db.String(32), db.ForeignKey("program.programid"), primary_key=True
    )
    stationid = db.Column(
        db.Integer, db.ForeignKey("station.stationid"), primary_key=True
    )
    airdate = db.Column(db.Integer, primary_key=True)
    duration = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Schedule(programid='{self.programid}', stationid={self.stationid}, md5='{self.md5}', airdate={self.airdate}, duration={self.duration})"


class Schedulemd5(db.Model):
    md5 = db.Column(db.String(32), primary_key=True)
    stationid = db.ForeignKey("station.stationid", nullable=False)
    datets = db.Column(db.Integer, nullable=False)
    modified = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Schedulemd5(stationid={self.stationid}, md5='{self.md5}', modified={self.modified})"


class User(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        return f"User(uid={self.uid}, name='{self.name}')"


class Logo(db.Model):
    lid = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(256), nullable=False)
    height = db.Column(db.Integer, nullable=True)
    width = db.Column(db.Integer, nullable=True)
    md5 = db.Column(db.String(32), nullable=False)
    source = db.Column(db.String(64), nullable=True)
    category = db.Column(db.String(10), nullable=True)

    def __repr__(self):
        return f"Logo(url={self.url})"
