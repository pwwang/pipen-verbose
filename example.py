from pipen import Proc, Pipen

class Process(Proc):
    input_keys = 'a'
    input = range(10)
    output = 'b:file:a.txt'
    script = 'echo {{in.a}} > {{out.b}}'

Pipen(starts=Process).run()
