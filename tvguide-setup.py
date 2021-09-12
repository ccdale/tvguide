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

import hashlib
import sys
from tvguide import errorExit
from tvguide.config import Configuration
from tvguide.credential import Credential

cfg = Configuration(appname="tvguide")

host = cfg.get("host", "schedulesdirect.net")
username = cfg.get("username")
if username is None:
    un = input(f"User Name for {host}: ")
    print(f"username for {host} is now {un}")
    yn = input("Is that correct (y/N): ")
    if yn.lower() == "y":
        cfg.update("username", un)
        username = un

cred = Credential(username, host)
pw = cred.getPassword()
if pw is None:
    print(f"Do you want to set/change your password for {host}")
    yn = input(f"Do you want to set/change your password for {host} (y/N):")
    if yn.lower() == "y":
        pw = input(f"{un} / {host} password: ")
        pw2 = input("again, please: ")
        if pw2 == pw:
            print("passwords match ok.")
            hpw = hashlib.sha1(pw.encode()).hexdigest()
            cred.setPassword(password=hpw)

print(f"{host} / {username} / {pw}")

cfg.writeConfig()
