"""pipen-verbose plugin: Logging some addtitional informtion for pipen"""

import os
from typing import TYPE_CHECKING, Any
from time import time
from xqute import JobStatus
from xqute.utils import a_read_text

from pipen import plugin
from pipen.utils import get_logger, brief_list

if TYPE_CHECKING:  # pragma: no cover
    from pipen import Proc

__version__ = "0.11.0"

logger = get_logger("verbose", "info")

VERBOSAL_CONFIGS = {
    # name: getter
    "scheduler": lambda proc: proc.scheduler.name,
    "lang": None,
    "forks": None,
    "cache": None,
    "dirsig": None,
    "size": None,
    "template": lambda proc: proc.template.name,
}


def _format_secs(seconds: float) -> str:
    """Format a time duration

    Args:
        seconds: the time duration in seconds

    Returns
        The formated string.
        For example: "01:01:01.001" stands for 1 hour 1 min 1 sec and 1 minisec.
    """
    minute, sec = divmod(seconds, 60)
    hour, minute = divmod(minute, 60)
    return "%02d:%02d:%02d.%03.0f" % (
        hour,
        minute,
        sec,
        1000 * (sec - int(sec)),
    )


def _shorten_path(path: Any, cutoff: int = 20) -> Any:
    """Shorten the path in input data"""
    if not isinstance(path, str):
        return path
    if len(path) < cutoff:
        return path
    if os.path.sep not in path:
        return f"{path[:5]} ... {path[-5:]}"

    parts = path.split(os.path.sep)
    if len(parts) >= 3:
        out = os.path.sep.join([parts[0], "..."] + parts[-2:])
        if len(out) < cutoff:
            return out
        out = os.path.sep.join([parts[0], "...", parts[-1]])
        return out

    if len(parts[0]) > 3:
        return os.path.sep.join(["...", parts[-1]])

    return os.path.sep.join([parts[0], f"...{parts[-1][-5:]}"])


class PipenVerbose:

    """pipen-verbose plugin: Logging some addtitional informtion for pipen"""

    __version__: str = __version__

    def __init__(self) -> None:
        """Constructor"""
        self.tic: float = 0.0  # pragma: no cover

    @plugin.impl
    def on_proc_input_computed(self, proc: "Proc"):
        """Print input data on debug"""
        data_to_show = proc.input.data.copy()
        if hasattr(data_to_show, "map"):  # pragma: no cover
            # pandas 2.1
            data_to_show = data_to_show.map(_shorten_path)
        else:
            data_to_show = data_to_show.applymap(_shorten_path)

        for line in data_to_show.to_string(
            show_dimensions=True, index=False
        ).splitlines():
            line = line.replace('%', '%%').replace('[', '\\[')
            proc.log("debug", f"indata | {line}")

    @plugin.impl
    async def on_proc_start(self, proc: "Proc"):
        """Print some configuration items of the process"""
        props = {}
        for prop, getter in VERBOSAL_CONFIGS.items():
            value = getter(proc) if getter else getattr(proc, prop)
            if value is not None and value != proc.pipeline.config.get(
                prop, None
            ):
                props[prop] = value

        key_len = max(len(prop) for prop in props) if props else 0
        for prop, value in props.items():
            proc.log(
                "info", "%s: %s", prop.ljust(key_len), value, logger=logger
            )
        # args
        if proc.envs:
            key_len = max(len(key) for key in proc.envs) if proc.envs else 0
            for key, value in proc.envs.items():
                value = [
                    line
                    if i == 0
                    else f"{' ' * (len(proc.name) + key_len + 17)}{line}"
                    for i, line in enumerate(
                        str(value)
                        .replace('%', '%%')
                        .replace('[', '\\[')
                        .splitlines()
                    )
                ]

                proc.log(
                    "info",
                    "envs.%s: %s",
                    key.ljust(key_len),
                    "\n".join(value),
                    logger=logger,
                )

        job = proc.jobs[0]
        # input
        input = job.input
        key_len = max(len(inp) for inp in input) if input else 0
        for inkey, inval in input.items():
            job.log(
                "info", "in.%s: %s", inkey.ljust(key_len), inval, logger=logger
            )

        # output
        output = job.output
        key_len = max(len(outp) for outp in output) if output else 0
        for inkey, inval in output.items():
            job.log(
                "info",
                "out.%s: %s",
                inkey.ljust(key_len),
                inval,
                logger=logger,
            )

        self.tic = time()

    @plugin.impl
    async def on_proc_done(self, proc: "Proc", succeeded: bool) -> None:
        """Log the ellapsed time for the process.
        If the process fails, log some error messages.
        """
        proc.log(
            "info",
            "Time elapsed: %ss",
            _format_secs(time() - self.tic),
            logger=logger,
        )

        if succeeded:
            return

        # print error info if any job failed
        failed_jobs = [
            job.index for job in proc.jobs if job.status == JobStatus.FAILED
        ]
        if not failed_jobs:  # pragma: no cover
            # could be triggered by Ctrl+C and all jobs are running
            return

        job = proc.jobs[failed_jobs[0]]

        proc.log(
            "error",
            "[red]Failed jobs: %s[/red]",
            brief_list(failed_jobs),
            logger=logger,
        )
        for job in proc.jobs:
            if job.status == JobStatus.FAILED:
                stderr = (
                    await a_read_text(job.stderr_file)
                    if job.stderr_file.is_file()
                    else ""
                )
                for line in stderr.splitlines():
                    job.log("error", "[red]%s[/red]", line, logger=logger)

                job.log(
                    "error",
                    "[red]-----------------------------------[/red]",
                    logger=logger,
                )
                job.log("error", "Script: %s", job.script_file, logger=logger)
                job.log("error", "Stdout: %s", job.stdout_file, logger=logger)
                job.log("error", "Stderr: %s", job.stderr_file, logger=logger)
                break
