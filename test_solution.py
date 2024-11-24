from dataclasses import dataclass
import pytest
import pathlib
import subprocess

project_dir = pathlib.Path(__file__).parent

@dataclass
class BasicOpsCase:
    name: str
    input: str
    expected_output: bytes

BASIC_OPS_CASES = [
    BasicOpsCase("load",
                 "LOAD 714 0\n",
                 bytes([0xa2, 0x2c, 0x00, 0x00, 0x00])
    ),
    BasicOpsCase("read",
                 "READ 9 187 11\n",
                 bytes([0x90, 0xbb, 0x0b])
    ),
    BasicOpsCase("write",
                 "WRITE 4 342\n",
                 bytes([0x45, 0x56, 0x01, 0x00])
    ),
    BasicOpsCase("shift",
                 "SHIFT 13 434\n",
                 bytes([0xd6, 0xb2, 0x01, 0x00])
    )
]

@pytest.mark.parametrize("op", BASIC_OPS_CASES)
def test_load(tmp_path, op):
    input_file = tmp_path / f"input_{op.name}"
    log_file = tmp_path / f"log_{op.name}.yaml"
    output_file = tmp_path / f"output_{op.name}"
    with open(input_file, "w") as f:
        f.write(op.input)

    res = subprocess.run(["python3", "assembler.py",\
                    str(input_file), str(output_file),
                    str(log_file)])
    assert res.returncode == 0
    with open(output_file, "rb") as f:
        got = f.read(len(op.expected_output))
        assert got == op.expected_output


def test_program(tmp_path):
    input_file = tmp_path / "input.asm"
    log_file = tmp_path / "log_file.yaml"
    assembler_file = tmp_path / "assembler.bin"
    interpreter_file = tmp_path / "result.yaml"

    with open(input_file, "w") as f:
        f.write(
    """LOAD 32 0
        LOAD 64 1
        LOAD 128 2
        LOAD 256 3
        LOAD 512 4
        WRITE 0 100
        WRITE 1 101
        WRITE 2 102
        WRITE 3 103
        WRITE 4 104
        LOAD 1 0
        LOAD 2 1
        LOAD 3 2
        LOAD 4 3
        LOAD 5 4
        WRITE 0 105
        WRITE 1 106
        WRITE 2 107
        WRITE 3 108
        WRITE 4 109
        SHIFT 0 100
        SHIFT 1 101
        SHIFT 2 102
        SHIFT 3 103
        SHIFT 4 104
        """)
    
    assembler_res = subprocess.run(["python3", "assembler.py",\
                    str(input_file), str(assembler_file),
                    str(log_file)])
    assert assembler_res.returncode == 0

    interpreter_res = subprocess.run(["python3", "interpreter.py",\
                    str(assembler_file), str(interpreter_file),\
                        "100", "110"], capture_output=True)
    assert interpreter_res.returncode == 0

    with open(interpreter_file, "r") as f:
        got = f.read()
        excepted = \
"""100: 16
101: 16
102: 16
103: 16
104: 16
105: 1
106: 2
107: 3
108: 4
109: 5
"""
        assert got == excepted
