from pipen import Pipen, Proc


class AProc(Proc):
    input = "a,b:file"
    output = "b:file:{{in.a}}.txt"
    input_data = [(1, __file__), (2, __file__)]
    envs = {
        "x": "[a]\nb=1\n",
        "xyz": "[a]\nb=1\n",
        "cases": {
            "some_key": "some_value",
            "another_key": {
                "nested_key": "nested_value",
                "list_key": [1, 2, 3],
                "nested_list_key": [
                    {"key1": "value1", "key2": "value2"},
                    {"key3": "value3", "key4": "value4", "key5": "value5"},
                ],
                "nested_dict_key": {
                    "sub_key1": "sub_value1",
                    "sub_key2": {
                        "sub_sub_key1": "sub_sub_value1",
                        "sub_sub_key2": [4, 5, 6],
                    },
                },
            },
            "venn": {
                "enabled": "auto",
                "more_formats": [],
                "save_code": False,
                "devpars": {"res": 100},
            },
        },
    }
    script = "echo 123 > {{out.b}}"


pipen = Pipen(loglevel="debug", plugin_opts={"verbose_loglevel": "debug"}).set_start(
    AProc
)

if __name__ == "__main__":
    pipen.run()
