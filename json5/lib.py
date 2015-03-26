# Copyright 2015 Google Inc. All rights reserved.
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

import json

def load(fp, **kwargs):
    return json.load(fp, **kwargs)


def loads(s, **kwargs):
    return json.loads(s, **kwargs)


def dump(obj, fp, **kwargs):
    return json.dump(obj, fp, **kwargs)


def dumps(obj, **kwargs):
    return json.dumps(obj, **kwargs)
