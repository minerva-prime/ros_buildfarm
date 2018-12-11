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

from colcon_core.package_identification.ignore import IGNORE_MARKER
from colcon_core.package_selection import add_arguments \
    as add_packages_arguments
from colcon_core.package_selection import get_packages
from colcon_core.plugin_system import satisfies_version
from colcon_core.verb import VerbExtensionPoint


class ScopeVerb(VerbExtensionPoint):
    """Scope workspace to a pool of packages by ignoring unrelated ones."""

    def __init__(self):
        super().__init__()
        satisfies_version(VerbExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')

    def add_arguments(self, *, parser):
        parser.add_argument(
            'depth_before', type=int, metavar='NUM_BEFORE',
            help='Number of forward-dependent packages upon which ' +
                 'the targeted package(s) depends.')
        parser.add_argument(
            'depth_after', type=int, metavar='NUM_AFTER',
            help='Number of reverse-dependent packages which ' +
                 'depend upon the targeted package(s).')
        parser.add_argument(
            '--testing', action='store_true',
            help='Include test dependencies of target(s).')
        add_packages_arguments(parser)

    def main(self, *, context):
        direct_categories = ('build', 'test') if context.args.testing else ('build', )
        recursive_categories = ('run', )

        # Decorators should be in topological order and selected based on args
        decorators = get_packages(
            context.args, additional_argument_names=['*'],
            direct_categories=direct_categories,
            recursive_categories=recursive_categories)

        # Key is package name. Value is depth to be processed after itself.
        # Presence in either dict indicates that the package is in scope.
        fwd_names = {}
        rev_names = {}

        # Sweep backward (for forward dependencies)
        if context.args.depth_before > 0:
            for pkg in reversed(decorators):
                if pkg.selected:
                    for dep in pkg.descriptor.get_dependencies(categories=direct_categories):
                        fwd_names[dep] = context.args.depth_before - 1
                elif fwd_names.get(pkg.descriptor.name, 0) > 0:
                    for dep in pkg.descriptor.get_dependencies(categories=recursive_categories):
                        if fwd_names.get(dep, -1) < fwd_names[pkg.descriptor.name] - 1:
                            fwd_names[dep] = fwd_names[pkg.descriptor.name] - 1

        # Sweep forward (for reverse dependencies)
        for pkg in decorators:
            if pkg.selected:
                rev_names[pkg.descriptor.name] = context.args.depth_after
            else:
                dep_depths = [rev_names.get(dep, -1) for dep in
                              pkg.descriptor.get_dependencies(categories=direct_categories)]
                if dep_depths:
                    dep_max = max(dep_depths)
                    if dep_max > 0:
                        rev_names[pkg.descriptor.name] = dep_max - 1

        # List of package names in scope
        in_scope_names = set(fwd_names.keys() | rev_names.keys())

        # Ignore out-of-scope packages
        for pkg in decorators:
            if pkg.descriptor.name not in in_scope_names:
                colcon_ignore = os.path.join(pkg.descriptor.path, IGNORE_MARKER)
                if not os.path.isfile(colcon_ignore):
                    print('Creating %s' % (colcon_ignore))
                    open(colcon_ignore, 'a').close()

        selected_len = len([pkg for pkg in decorators if pkg.selected])

        # Summarize
        print('-----------')
        print('Selected:%2d' % (selected_len, ))
        print('Before:%4d' % (len(fwd_names), ))
        print('After:%5d' % (len(rev_names) - selected_len, ))
        print('-----------')
