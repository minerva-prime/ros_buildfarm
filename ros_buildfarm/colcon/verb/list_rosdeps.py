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

from colcon_core.package_decorator import add_recursive_dependencies
from colcon_core.package_decorator import get_decorators
from colcon_core.package_selection import add_arguments \
    as add_packages_arguments
from colcon_core.package_selection import get_package_descriptors
from colcon_core.package_selection import select_package_decorators
from colcon_core.plugin_system import satisfies_version
from colcon_core.verb import VerbExtensionPoint


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
        descriptors = get_package_descriptors(
            context.args, additional_argument_names=['*'])
        decorators = get_decorators(descriptors)
        package_names = set([desc.name for desc in descriptors])
        add_recursive_dependencies(
            decorators,
            direct_categories=('build', 'test') if context.args.testing else ('build', ),
            recursive_categories=('run', ))
        select_package_decorators(context.args, decorators)

        decorators = [dec for dec in decorators if dec.selected]
        decorators = [dec for dec in decorators if dec.descriptor.type.startswith('ros.')]

        rosdeps = set()
        recursive_deps = set()
        for dec in decorators:
            recursive_deps.update(dec.recursive_dependencies)
            if 'build' in dec.descriptor.dependencies:
                rosdeps.update(dec.descriptor.dependencies['build'])
            if context.args.testing:
                if 'run' in dec.descriptor.dependencies:
                    rosdeps.update(dec.descriptor.dependencies['run'])
                if 'test' in dec.descriptor.dependencies:
                    rosdeps.update(dec.descriptor.dependencies['test'])

        for desc in descriptors:
            if not desc.name in recursive_deps:
                continue
            if 'run' in desc.dependencies:
                rosdeps.update(desc.dependencies['run'])

        for dep in sorted(rosdeps - package_names):
            print(dep)
