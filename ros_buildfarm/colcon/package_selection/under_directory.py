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

from pathlib import Path

from colcon_core.package_selection import PackageSelectionExtensionPoint
from colcon_core.plugin_system import satisfies_version


class UnderDirectoryPackageSelection(PackageSelectionExtensionPoint):
    """Select packages which share a given parent directory."""

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(
            PackageSelectionExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')

    def add_arguments(self, *, parser):
        parser.add_argument(
            '--packages-under-directory', nargs='*', metavar='PATH',
            help='Process packages which share the parent directory')

    def select_packages(self, args, decorators):
        if args.packages_under_directory:
            parents = set([Path(path) for path in args.packages_under_directory])

            for decorator in decorators:
                pkg_path = Path(decorator.descriptor.path)
                if not len(parents.intersection(pkg_path.parents)):
                    decorator.selected = False
