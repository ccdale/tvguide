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

import logging
import os
from pathlib import Path
import sys

from tvguide import makeApp, db, log, errorNotify, errorExit


app = makeApp()


def updateDB():
    try:
        with app.app_context():
            dbpath = Path(app.config["DATABASE"])
            log.debug(f"looking for database at: {dbpath}")
            if not dbpath.is_file():
                raise Exception(f"failed to find a database at: {dpbath}")
        log.info(f"I'm here so the dbpath must be correct {dbpath}")
    except Exception as e:
        errorExit(sys.exc_info()[2], e)


if __name__ == "__main__":
    os.environ["FLASK_ENV"] = "development"
    log.setLevel(logging.DEBUG)
    updateDB()
