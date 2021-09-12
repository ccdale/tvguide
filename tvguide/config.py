# Copyright (c) 2021, Christopher Allison
#
#     This file is part of ptvg.
#
#     ptvg is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     ptvg is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with ptvg.  If not, see <http://www.gnu.org/licenses/>.
"""Configuration routines for the ptvg application."""

from pathlib import Path
import sys
import yaml

from tvguide import errorRaise, errorNotify


class Configuration:
    def __init__(self, appname="ptvg"):
        try:
            self.appname = appname
            self.config = {}
            yamlfn = f"{self.appname}.yaml"
            home = Path.home()
            self.configfn = home.joinpath(".config", yamlfn)
            self.readConfig()
        except Exception as e:
            errorRaise(sys.exc_info()[2], e)

    def readConfig(self):
        try:
            if self.configfn.exists():
                with open(str(self.configfn), "r") as cfn:
                    self.config = yaml.safe_load(cfn)
        except Exception as e:
            errorRaise(sys.exc_info()[2], e)

    def writeConfig(self):
        try:
            if self.config.get("amdirty", True):
                self.config.pop("amdirty", None)
                with open(str(self.configfn), "w") as cfn:
                    yaml.dump(self.config, cfn, default_flow_style=False)
        except Exception as e:
            errorRaise(sys.exc_info()[2], e)

    def update(self, key, value):
        try:
            self.config[key] = value
            self.config["amdirty"] = True
        except Exception as e:
            errorRaise(sys.exc_info()[2], e)
