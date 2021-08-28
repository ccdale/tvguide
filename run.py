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

from pathlib import Path
import sys

from tvguide import makeApp, db, log, errorNotify


app = makeApp()


def letsGo():
    try:
        with app.app_context():
            dbpath = Path(app.config["DATABASE"])
            log.warning(f"looking for database at: {dbpath}")
            if not dbpath.is_file():
                log.warning(f"Creating db at {dbpath}")
                db.create_all()
            log.info("running application")
            app.run(host="0.0.0.0")
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


if __name__ == "__main__":
    letsGo()
