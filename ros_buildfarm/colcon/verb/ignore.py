# Copyright 2018 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from colcon_core.package_decorator import get_decorators
from colcon_core.package_identification.ignore import IGNORE_MARKER
from colcon_core.package_selection import add_arguments \
    as add_packages_arguments
from colcon_core.package_selection import get_package_descriptors
from colcon_core.package_selection import select_package_decorators
from colcon_core.plugin_system import satisfies_version
from colcon_core.verb import VerbExtensionPoint


class IgnoreVerb(VerbExtensionPoint):
    """Create package ignore marker files."""

    def __init__(self):
        super().__init__()
        satisfies_version(VerbExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')

    def add_arguments(self, *, parser):  # noqa: D102
        add_packages_arguments(parser)

    def main(self, *, context):
        descriptors = get_package_descriptors(
            context.args, additional_argument_names=['*'])
        decorators = get_decorators(descriptors)
        select_package_decorators(context.args, decorators)

        for descriptor in [dec.descriptor for dec in decorators if dec.selected]:
            colcon_ignore = os.path.join(descriptor.path, IGNORE_MARKER)
            if not os.path.isfile(colcon_ignore):
                print('Creating %s' % (colcon_ignore))
                open(colcon_ignore, 'a').close()
