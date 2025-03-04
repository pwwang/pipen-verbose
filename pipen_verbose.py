"""pipen-verbose plugin: Logging some addtitional informtion for pipen"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, List, Mapping
from pprint import pformat
from functools import singledispatch
from time import time
from yunpath import CloudPath
from xqute import JobStatus
from xqute.path import MountedPath

from pipen import plugin
from pipen.utils import get_logger, brief_list

if TYPE_CHECKING:  # pragma: no cover
    from pipen import Proc

__version__ = "0.13.0"

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


@singledispatch
def _shorten_value(value, len_cutoff: int = 20) -> str:
    """Format the values in input dataframe for debug logging

    Args:
        value: The value to be formatted
        len_cutoff: The length cutoff for the value

    Returns:
        The formatted value
    """
    return _shorten_value.dispatch(str)(str(value), len_cutoff)


@_shorten_value.register(str)
def _(value: str, len_cutoff: int = 20) -> str:
    if len(value) < len_cutoff:
        return value

    if "/" not in value:
        return f"{value[:5]} ... {value[-5:]}"

    parts = value.split("/")
    if len(parts) >= 3:
        out = "/".join([parts[0], "..."] + parts[-2:])
        if len(out) < len_cutoff:
            return out
        out = "/".join([parts[0], "...", parts[-1]])
        return out

    if len(parts[0]) > 3:
        return "/".join(["...", parts[-1]])

    return "/".join([parts[0], f"...{parts[-1][-5:]}"])


@_shorten_value.register(MountedPath)
def _(value: MountedPath, len_cutoff: int = 20) -> str:
    """Format the value of MountedPath"""
    fmtfn = _shorten_value.dispatch(str)

    if value.spec and value.spec == value:
        return fmtfn(str(value), len_cutoff)

    part1 = fmtfn(str(value.spec), len_cutoff)
    part2 = fmtfn(str(value), len_cutoff)
    return f"{part1}:{part2}"


def _is_mounted_path(path: Any) -> bool:
    """Check if the path is a mounted path"""
    return isinstance(path, MountedPath) and path.spec and path.spec != path


@singledispatch
def _format_value(value, key: str, key_len: int) -> List[str]:
    """Format the value to a string or a list of strings to be logged

    Args:
        value: The value to be formatted
        key: The key of the value
        key_len: The length of the key

    Returns:
        The formatted value, which is a list of strings
    """
    return _format_value.dispatch(str)(pformat(value), key, key_len)


@_format_value.register(str)
def _(value: str, key: str, key_len: int) -> List[str]:
    """Format the value of str"""
    out = []

    if "\n" in value:
        for i, line in enumerate(value.splitlines()):
            line = line.replace("%", "%%").replace("[", "\\[")
            if i == 0:
                out.append(f"{key.ljust(key_len)}: {line}")
            else:
                out.append(f"{' ' * (key_len + 2)}{line}")
    else:
        value = value.replace("%", "%%").replace("[", "\\[")
        out.append(f"{key.ljust(key_len)}: {value}")

    return out


@_format_value.register(MountedPath)
@_format_value.register(CloudPath)
def _(value: MountedPath, key: str, key_len: int) -> List[str]:
    """Format the value of MountedPath"""
    strfmt = _format_value.dispatch(str)
    out = strfmt(str(value), key, key_len)

    if hasattr(value, "spec") and value.spec != value:
        out.extend(strfmt(str(value.spec), f"{key}.spec", key_len))

    return out


def _log_values(
    values: Mapping[str, Any] | None,
    log_fn: Callable,
    prefix: str = "",
    level: str = "info",
) -> None:
    """Log the values"""
    key_len = max(len(key) for key in values) if values else 0
    if any(_is_mounted_path(value) for value in values.values()):
        key_len += 5  # .spec
    key_len += len(prefix)

    for key, value in values.items():
        for formatted in _format_value(value, f"{prefix}{key}", key_len):
            log_fn(level, formatted, logger=logger)


class PipenVerbose:
    """pipen-verbose plugin: Logging some addtitional informtion for pipen"""

    __version__: str = __version__
    __slots__ = ("tic",)

    def __init__(self) -> None:
        """Constructor"""
        self.tic: float = 0.0  # pragma: no cover

    @plugin.impl
    def on_proc_input_computed(self, proc: Proc):
        """Print input data on debug"""
        if hasattr(proc.input.data, "map"):  # pragma: no cover
            # pandas 2.1
            data_to_show = proc.input.data.map(_shorten_value)
        else:  # pragma: no cover
            data_to_show = proc.input.data.applymap(_shorten_value)

        _log_values(
            {"indata": data_to_show.to_string(show_dimensions=True, index=False)},
            proc.log,
            level="debug",
        )

    @plugin.impl
    async def on_proc_start(self, proc: Proc):
        """Print some configuration items of the process"""
        # printing the process properties
        # ---------------------------------
        props = {}
        for prop, getter in VERBOSAL_CONFIGS.items():
            value = getter(proc) if getter else getattr(proc, prop)
            if value is not None and value != proc.pipeline.config.get(prop, None):
                props[prop] = value

        _log_values(props, proc.log, prefix="")

        # printing the process envs
        # ---------------------------------
        _log_values(proc.envs, proc.log, prefix="envs.")

        job = proc.jobs[0]
        # printing the process input
        # ---------------------------------
        _log_values(job.input, job.log, prefix="in.")

        # printing the process output
        # ---------------------------------
        output = job.output
        _log_values(output, job.log, prefix="out.")

        self.tic = time()

    @plugin.impl
    async def on_proc_done(self, proc: Proc, succeeded: bool) -> None:
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
        failed_jobs = [job.index for job in proc.jobs if job.status == JobStatus.FAILED]
        if not failed_jobs:  # pragma: no cover
            # could be triggered by Ctrl+C and all jobs are running
            return

        proc.log(
            "error",
            "[red]Failed jobs: %s[/red]",
            brief_list(failed_jobs),
            logger=logger,
        )

        job = proc.jobs[failed_jobs[0]]
        stderr = (
            job.stderr_file.read_text() if job.stderr_file.is_file() else ""
        )
        kwargs = {"limit": job.index + 1, "logger": logger}
        for line in stderr.splitlines():
            job.log("error", "[red]%s[/red]", line, **kwargs)

        job.log("error", "[red]-----------------------------------[/red]", **kwargs)
        if not _is_mounted_path(job.script_file.mounted):
            job.log("error", "script: %s", job.script_file, **kwargs)
            job.log("error", "stdout: %s", job.stdout_file, **kwargs)
            job.log("error", "stderr: %s", job.stderr_file, **kwargs)
        else:  # pragma: no cover
            job.log("error", "script: %s", job.script_file.mounted, **kwargs)
            job.log("error", "script (spec): %s", job.script_file, **kwargs)
            job.log("error", "stdout: %s", job.stdout_file.mounted, **kwargs)
            job.log("error", "stdout (spec): %s", job.stdout_file, **kwargs)
            job.log("error", "stderr: %s", job.stderr_file.mounted, **kwargs)
            job.log("error", "stderr (spec): %s", job.stderr_file, **kwargs)
