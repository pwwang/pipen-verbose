
from pathlib import Path
from shutil import rmtree
from tempfile import gettempdir
import pytest
from pipen import Pipen, Proc
from pipen_verbose import PipenVerbose

TEST_TMPDIR = Path(gettempdir()) / "pipen_verbose_tests"
rmtree(TEST_TMPDIR, ignore_errors=True)
TEST_TMPDIR.mkdir(parents=True, exist_ok=True)

@pytest.fixture
def pipen():
    index = Pipen.PIPELINE_COUNT + 1
    return Pipen(
        name=f"pipeline_{index}",
        desc="Verbose test",
        loglevel="debug",
        cache=False,
        plugins=[PipenVerbose],
        outdir=TEST_TMPDIR / f"pipen_{index}",
    )

class NormalProc(Proc):
    input = "a"
    output = "b:{{in.a}}"
    input_data = [1]
    envs = {"x": 1}

class MultiJobProc(Proc):
    input = "a"
    output = "b:{{in.a}}"
    script = "echo 123 >&2; exit {{in.a}}"
    input_data = [0, 1]

def test_normal(pipen, caplog):
    pipen.set_starts(NormalProc).run()
    assert "Time elapsed" in caplog.text

def test_multijob(pipen, caplog):
    pipen.set_starts(MultiJobProc).run()
    assert "Failed jobs" in caplog.text
    assert "123" in caplog.text
