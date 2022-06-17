from pipen import Pipen, Proc

class AProc(Proc):
    input = "a"
    output = "b:file:{{in.a}}.txt"
    input_data = [1]
    envs = {
        "x": "[a]\nb=1\n",
        "xyz": "[a]\nb=1\n",
    }
    script = "echo 123 > {{out.b}}"

pipen = Pipen(loglevel="debug").set_start(AProc)

if __name__ == "__main__":
    pipen.run()
