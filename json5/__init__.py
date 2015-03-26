# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""json5 - a pure Python implementation of the JSON5 configuration language."""

from json5.arg_parser import ArgumentParser
from json5.main import main
from json5.lib import load, loads, dump, dumps
from json5.version import VERSION


__all__ = [
    'ArgumentParser',
    'VERSION',
    'dump',
    'dumps',
    'load',
    'loads',
    'main',
]
