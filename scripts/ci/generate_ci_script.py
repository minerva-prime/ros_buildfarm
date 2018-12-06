#!/usr/bin/env python3

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

import argparse
import sys

from em import BANGPATH_OPT
from em import Hook

from ros_buildfarm.argument import add_argument_arch
from ros_buildfarm.argument import add_argument_build_name
from ros_buildfarm.argument import add_argument_build_tool
from ros_buildfarm.argument import add_argument_config_url
from ros_buildfarm.argument import add_argument_os_code_name
from ros_buildfarm.argument import add_argument_os_name
from ros_buildfarm.argument import add_argument_rosdistro_name
from ros_buildfarm.ci_job import configure_ci_job
from ros_buildfarm.common import get_ci_job_name
from ros_buildfarm.config import get_ci_build_files
from ros_buildfarm.config import get_index as get_config_index
from ros_buildfarm.templates import expand_template


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description="Generate a 'CI' script")
    add_argument_config_url(parser)
    add_argument_rosdistro_name(parser)
    add_argument_build_name(parser, 'ci')
    add_argument_os_name(parser)
    add_argument_os_code_name(parser)
    add_argument_arch(parser)
    add_argument_build_tool(parser)
    parser.add_argument(
        '--skip-cleanup', action='store_true',
        help="Do not clean up the workspace after the job completes.")
    args = parser.parse_args(argv)

    # collect all template snippets of specific types
    class IncludeHook(Hook):

        def __init__(self):
            Hook.__init__(self)
            self.scms = []
            self.scripts = []
            self.parameters = {}

        def beforeInclude(self, *_, **kwargs):
            template_path = kwargs['file'].name
            if template_path.endswith('/snippet/scm.xml.em'):
                self.scms.append(
                    (kwargs['locals']['repo_spec'], kwargs['locals']['path']))
            if template_path.endswith('/snippet/builder_shell.xml.em'):
                script = kwargs['locals']['script']
                # reuse existing ros_buildfarm folder if it exists
                if 'Clone ros_buildfarm' in script:
                    lines = script.splitlines()
                    lines.insert(0, 'if [ ! -d "ros_buildfarm" ]; then')
                    lines += [
                        'else',
                        'echo "Using existing ros_buildfarm folder"',
                        'fi',
                    ]
                    script = '\n'.join(lines)
                if args.build_tool and ' --build-tool ' in script:
                    script = script.replace(
                        ' --build-tool catkin_make_isolated',
                        ' --build-tool ' + args.build_tool)
                self.scripts.append(script)
            if template_path.endswith('/snippet/property_parameters-definition.xml.em'):
                for parameter in reversed(kwargs['locals']['parameters']):
                    name = parameter['name']
                    value_type = parameter['type']
                    if value_type in ['string', 'text']:
                        default_value = parameter['default_value']
                    elif value_type is 'boolean':
                        if name == 'skip_cleanup':
                            default_value = 'true' if args.skip_cleanup else 'false'
                        else:
                            default_value = 'true' if parameter.get('default_value', False) else 'false'
                    else:
                        continue

                    self.parameters.setdefault(name, default_value)

    hook = IncludeHook()
    from ros_buildfarm import templates
    templates.template_hooks = [hook]

    config = get_config_index(args.config_url)
    build_files = get_ci_build_files(config, args.rosdistro_name)
    build_file = build_files[args.ci_build_name]

    configure_ci_job(
        args.config_url, args.rosdistro_name, args.ci_build_name,
        args.os_name, args.os_code_name, args.arch,
        config=config, build_file=build_file, jenkins=False, views=False,
        job_type='script')

    templates.template_hooks = None

    ci_job_name = get_ci_job_name(
        args.rosdistro_name, args.os_name,
        args.os_code_name, args.arch, 'script')

    value = expand_template(
        'ci/ci_script.sh.em', {
            'ci_job_name': ci_job_name,
            'scms': hook.scms,
            'scripts': hook.scripts,
            'build_tool': args.build_tool or build_file.build_tool,
            'parameters': hook.parameters},
        options={BANGPATH_OPT: False})
    value = value.replace('python3 ', sys.executable + ' ')
    print(value)


if __name__ == '__main__':
    sys.exit(main())
