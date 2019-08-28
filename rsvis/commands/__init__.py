import rsvis.config.utils
import rsvis.plugin

import glob
import logging
import os
import re

import stevedore

commands_mgr = None

def _create_commands_mgr():
    global commands_mgr

    if commands_mgr is not None:
        return

    commands_mgr = stevedore.extension.ExtensionManager(
        namespace='rsvis.command',
        invoke_on_load=False,
        verify_requirements=True,
        propagate_map_exceptions=True,
        on_load_failure_callback=rsvis.plugin.stevedore_error_handler
    )


def get_external_scripts():
    regex = re.compile('.*rsvis-([^ .]+)$')
    paths = []
    scripts = {}
    paths.append(rsvis.config.utils.get_scripts_folder())
    paths += os.environ["PATH"].split(":")
    for path in paths:
        for script in glob.glob(os.path.join(path, "rsvis-*")):
            m = regex.match(script)
            if m is not None:
                name = m.group(1)
                scripts[name] = dict(
                    command_name=name,
                    path=script,
                    plugin=None
                )
    return scripts


def get_scripts():
    global commands_mgr
    _create_commands_mgr()
    scripts_dict = dict()
    for command_name in commands_mgr.names():
        scripts_dict[command_name] = dict(
            command_name=command_name,
            path=None,
            plugin=commands_mgr[command_name].plugin
        )
    return scripts_dict
