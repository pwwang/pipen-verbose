# pipen-verbose

Add verbosal information in logs for [pipen][1].

## Usage
```python
from pipen import Proc, Pipen

class Process(Proc):
    input_keys = 'a'
    input = range(10)
    output = 'b:file:a.txt'
    script = 'echo {{in.a}} > {{out.b}}'

Pipen(starts=Process).run()
```

```
> python example.py
11-04 12:00:19 I /main                _____________________________________   __
               I /main                ___  __ \___  _/__  __ \__  ____/__  | / /
               I /main                __  /_/ /__  / __  /_/ /_  __/  __   |/ /
               I /main                _  ____/__/ /  _  ____/_  /___  _  /|  /
               I /main                 /_/     /___/  /_/     /_____/  /_/ |_/
               I /main
               I /main                             version: 0.0.1
               I /main
               I /main    ┏━━━━━━━━━━━━━━━━━━━━━━━━━ pipeline-0 ━━━━━━━━━━━━━━━━━━━━━━━━━━┓
               I /main    ┃ Undescribed.                                                  ┃
               I /main    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
               I /main    Enabled plugins: ['verbose', 'main-0.0.1']
               I /main    Loaded processes: 1
               I /main    Running pipeline using profile: 'default'
               I /main    Output will be saved to: './pipeline-0-output'
               I /main
               I /main    ╭─────────────────── default configurations ────────────────────╮
               I /main    │ cache            = True                                       │
               I /main    │ dirsig           = 1                                          │
               I /main    │ envs             = Config({})                                 │
               I /main    │ error_strategy   = 'ignore'                                   │
               I /main    │ forks            = 1                                          │
               I /main    │ lang             = 'bash'                                     │
               I /main    │ loglevel         = 'debug'                                    │
               I /main    │ num_retries      = 3                                          │
               I /main    │ plugin_opts      = Config({})                                 │
               I /main    │ plugins          = None                                       │
               I /main    │ scheduler        = 'local'                                    │
               I /main    │ scheduler_opts   = Config({})                                 │
               I /main    │ submission_batch = 8                                          │
               I /main    │ template         = 'liquid'                                   │
               I /main    │ workdir          = './.pipen'                                 │
               I /main    ╰───────────────────────────────────────────────────────────────╯
               I /main
               I /main    ╭═══════════════════════════ Process ═══════════════════════════╮
               I /main    ║ Undescribed.                                                  ║
               I /main    ╰═══════════════════════════════════════════════════════════════╯
               I /main    Process: Workdir: '.pipen/process'
               I /verbose Process: size: 10
               I /verbose Process: [0/9] in.a: 0
               I /verbose Process: [0/9] out.b: pipeline-0-output/Process/0/a.txt
               I /main    Process: Cached jobs: 0-1
               I /verbose Process: Time elapsed: 00:00:00.034s

pipeline-0: 100%|████████████████████████████████████████| 1/1 [00:00<00:00, 10.50 procs/s]
```

[1]: https://github.com/pwwang/pipen
