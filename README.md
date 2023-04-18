# pipen-verbose

Add verbosal information in logs for [pipen][1].

## Additional information

- Following process properties if not `None` and different from pipeline-level configurations: `scheduler`, `lang`, `forks`, `cache`, `dirsig`, `size`, `template`
- Ellapsed time for a process. Note that this is time ellapsed from process initialization to completion, no matter the jobs are cached or not, so this is not the real running time for the jobs.
- Process `envs` if set.
- Computed input data for processes.
- The indices of failed jobs if any.
- The stderr, paths to script, stdout file, stderr file, of the first failed jobs if any.
- The input/output data of the first job.

## Installation

```
pip install -U pipen-verbose
```

## Enabling/Disabling the plugin

The plugin is registered via entrypoints. It's by default enabled. To disable it:
`plugins=[..., "no:verbose"]`, or uninstall this plugin.

## Usage

`example.py`
```python
from pipen import Proc, Pipen

class Process(Proc):
    input = 'a'
    input_data = range(10)
    output = 'b:file:a.txt'
    cache = False
    script = 'echo {{in.a}} > {{out.b}}'

Pipen().run(Process)
```

```
> python example.py
[09/12/21 22:57:01] I main                   _____________________________________   __
[09/12/21 22:57:01] I main                   ___  __ \___  _/__  __ \__  ____/__  | / /
[09/12/21 22:57:01] I main                   __  /_/ /__  / __  /_/ /_  __/  __   |/ /
[09/12/21 22:57:01] I main                   _  ____/__/ /  _  ____/_  /___  _  /|  /
[09/12/21 22:57:01] I main                   /_/     /___/  /_/     /_____/  /_/ |_/
[09/12/21 22:57:01] I main
[09/12/21 22:57:01] I main                                version: 0.1.0
[09/12/21 22:57:01] I main
[09/12/21 22:57:01] I main    ╭═════════════════════════════ PIPEN-0 ══════════════════════════════╮
[09/12/21 22:57:01] I main    ║  # procs          = 1                                              ║
[09/12/21 22:57:01] I main    ║  plugins          = ['main', 'verbose-0.0.1']                      ║
[09/12/21 22:57:01] I main    ║  profile          = default                                        ║
[09/12/21 22:57:01] I main    ║  outdir           = ./Pipen-output                                 ║
[09/12/21 22:57:01] I main    ║  cache            = True                                           ║
[09/12/21 22:57:01] I main    ║  dirsig           = 1                                              ║
[09/12/21 22:57:01] I main    ║  error_strategy   = ignore                                         ║
[09/12/21 22:57:01] I main    ║  forks            = 1                                              ║
[09/12/21 22:57:01] I main    ║  lang             = bash                                           ║
[09/12/21 22:57:01] I main    ║  loglevel         = info                                           ║
[09/12/21 22:57:01] I main    ║  num_retries      = 3                                              ║
[09/12/21 22:57:01] I main    ║  plugin_opts      = {}                                             ║
[09/12/21 22:57:01] I main    ║  plugins          = None                                           ║
[09/12/21 22:57:01] I main    ║  scheduler        = local                                          ║
[09/12/21 22:57:01] I main    ║  scheduler_opts   = {}                                             ║
[09/12/21 22:57:01] I main    ║  submission_batch = 8                                              ║
[09/12/21 22:57:01] I main    ║  template         = liquid                                         ║
[09/12/21 22:57:01] I main    ║  template_opts    = {}                                             ║
[09/12/21 22:57:01] I main    ║  workdir          = ./.pipen                                       ║
[09/12/21 22:57:01] I main    ╰════════════════════════════════════════════════════════════════════╯
[09/12/21 22:57:02] I main
[09/12/21 22:57:02] I main    ╭═════════════════════════════ Process ══════════════════════════════╮
[09/12/21 22:57:02] I main    ║ Undescribed                                                        ║
[09/12/21 22:57:02] I main    ╰════════════════════════════════════════════════════════════════════╯
[09/12/21 22:57:02] I main    Process: Workdir: '.pipen/pipen-0/process'
[09/12/21 22:57:02] I main    Process: <<< [START]
[09/12/21 22:57:02] I main    Process: >>> [END]
[09/12/21 22:57:02] I verbose Process: cache: False
[09/12/21 22:57:02] I verbose Process: size : 10
[09/12/21 22:57:02] I verbose Process: [0/9] in.a: 0
[09/12/21 22:57:02] I verbose Process: [0/9] out.b:
                      /home/pwwang/github/pipen-verbose/Pipen-output/Process/0/a.txt
[09/12/21 22:57:04] I verbose Process: Time elapsed: 00:00:02.043s
[09/12/21 22:57:04] I main
```

[1]: https://github.com/pwwang/pipen
