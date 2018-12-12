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

from colcon_core.package_selection import add_arguments \
    as add_packages_arguments
from colcon_core.package_selection import get_packages
from colcon_core.plugin_system import satisfies_version
from colcon_core.verb import VerbExtensionPoint

from colcon_core.shell import find_installed_packages_in_environment


class ListRosdepsVerb(VerbExtensionPoint):
    """List rosdep keys needed to process the workspace."""

    def __init__(self):
        super().__init__()
        satisfies_version(VerbExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')

    def add_arguments(self, *, parser):
        parser.add_argument(
            '--testing', action='store_true',
            help='Include keys necessary to test the selected packages')
        add_packages_arguments(parser)

    def main(self, *, context):
        direct_categories = ('build', 'test') if context.args.testing else ('build', )
        recursive_categories = ('run', )

        # Decorators should be in topological order and selected based on args
        decorators = get_packages(
            context.args, additional_argument_names=['*'],
            direct_categories=direct_categories,
            recursive_categories=recursive_categories)

        package_names = set([pkg.descriptor.name for pkg in decorators])

        rosdeps = set()

        for pkg in reversed(decorators):
            if pkg.descriptor.type.startswith('ros.'):
                if pkg.selected:
                    rosdeps.update(pkg.descriptor.get_dependencies(categories=direct_categories))
                elif pkg.descriptor.name in rosdeps:
                    rosdeps.update(pkg.descriptor.get_dependencies(categories=recursive_categories))

        rosdeps -= package_names

        for dep in sorted(rosdeps - package_names):
            print(dep)
