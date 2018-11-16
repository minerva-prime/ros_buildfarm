# generated from @template_name

@(TEMPLATE(
    'snippet/from_base_image.Dockerfile.em',
    os_name=os_name,
    os_code_name=os_code_name,
    arch=arch,
))@

VOLUME ["/var/cache/apt/archives"]

ENV DEBIAN_FRONTEND noninteractive

@(TEMPLATE(
    'snippet/old_release_set.Dockerfile.em',
    os_name=os_name,
    os_code_name=os_code_name,
))@

@(TEMPLATE(
    'snippet/setup_locale.Dockerfile.em',
    timezone=timezone,
))@

RUN useradd -u @uid -m buildfarm

@(TEMPLATE(
    'snippet/add_distribution_repositories.Dockerfile.em',
    distribution_repository_keys=distribution_repository_keys,
    distribution_repository_urls=distribution_repository_urls,
    os_name=os_name,
    os_code_name=os_code_name,
    add_source=False,
))@

@(TEMPLATE(
    'snippet/add_additional_repositories.Dockerfile.em',
    os_name=os_name,
    os_code_name=os_code_name,
    arch=arch,
))@

@(TEMPLATE(
    'snippet/add_wrapper_scripts.Dockerfile.em',
    wrapper_scripts=wrapper_scripts,
))@

# automatic invalidation once every day
RUN echo "@today_str"

@(TEMPLATE(
    'snippet/install_python3.Dockerfile.em',
    os_name=os_name,
    os_code_name=os_code_name,
))@

@(TEMPLATE(
    'snippet/install_dependencies.Dockerfile.em',
    dependencies=dependencies,
    dependency_versions=dependency_versions,
))@

@(TEMPLATE(
    'snippet/rosdep_init.Dockerfile.em',
    custom_rosdep_urls=custom_rosdep_urls,
))@

USER buildfarm
ENTRYPOINT ["sh", "-c"]
@{
cmds = [
    'rosdep update',

    'PYTHONPATH=/tmp/ros_buildfarm:$PYTHONPATH python3 -u' + \
    ' /tmp/ros_buildfarm/scripts/ci/create_workspace.py' + \
    ' --workspace-root /tmp/ws' + \
    ' --repos-file-urls ' + ' '.join(repos_file_urls),

    'PYTHONPATH=/tmp/ros_buildfarm:$PYTHONPATH python3 -u' + \
    ' /tmp/ros_buildfarm/scripts/ci/get_rosdep_dependencies.py' + \
    ' --package-root /tmp/ws/src' + \
    ' --os-name ' + os_name + \
    ' --os-code-name ' + os_code_name + \
    ' --rosdistro-name ' + rosdistro_name + \
    ' --output-file /tmp/ws/install_list.txt' + \
    ' --skip-rosdep-keys ' + ' '.join(skip_rosdep_keys) + \
    ' --parent-package-root /tmp/parent_ws/share',
]
}@
CMD ["@(' && '.join(cmds))"]
