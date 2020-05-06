# ===========================================================================
#   run.py ------------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.__init__
import rsvis.config.settings
import rsvis.plugin
import rsvis.debug.exceptions

import click

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
@click.command(
    "run",
    help="RSCanvas",
    context_settings=dict(ignore_unknown_options=True)
)
@click.help_option(
    "-h",
    "--help" 
)
@click.argument(
    "file", 
    type=str, 
    nargs=1
)
@click.option(
    "--task_set",
    help="Execute a task from specified task set(default: {0})".format(rsvis.config.settings._TASK_SPEC_NAME),
    type=click.Choice([*rsvis.plugin.get_tasks()]),
    default=rsvis.config.settings._TASK_SPEC_NAME
)
@click.option(
    "-t",
    "--task",
    help="Execute the specified task (default: {0})".format(""),
    type=str,
    default= rsvis.config.settings._DEFAULT_TASK 
)
def cli(
        file,
        task_set,
        task,
    ):
    """Read general settings file and execute specified task."""

    # read general settings file and assign content to global settings object
    rsvis.config.settings.get_settings(file)

    # get the specified task and imort it as module
    task_module = rsvis.plugin.get_module_from_submodule("tasks", task_set)

    # call task's main routine
    if not task:
        rsvis.__init__._logger.debug("Call the default routine from task set '{0}'".format(task_module[0]))
        task_module[0].main()
    else:
        rsvis.__init__._logger.debug("Call task '{1}' from set '{0}'".format(task_module[1], task))

        task_funcs = rsvis.plugin.get_module_functions(task_module[0])
        if not task in task_funcs:
            raise rsvis.debug.exceptions.ArgumentError(task, task_funcs) 

        task_func = rsvis.plugin.get_module_task(
            task_module[0],
            "{}{}".format(rsvis.config.settings._TASK_PREFIX, task)
        )
        task_func()        