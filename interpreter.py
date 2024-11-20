import yaml
import sys
from dataclasses import dataclass

MEMORY_SIZE = 1024
REG_COUNT = 32

@dataclass
class BinaryBuffer:
    binary_data: bytearray = bytearray()
    bit_it = 0
    
    def read(self, bit_width):
        res = 0
        for i in range(bit_width):
            res ^= (((self.binary_data[self.bit_it // 8] >> (self.bit_it % 8)) & 1) << i)
            self.bit_it += 1
        return res

def interpret(binary_path, result_path, memory_range):
    memory = [0] * MEMORY_SIZE
    registers = [0] * REG_COUNT
    result = {}

    with open(binary_path, "rb") as f:
        binary_data = f.read()

    buffer = BinaryBuffer(binary_data)
    i = 0
    while i * 8 < len(binary_data):
        opcode = buffer.read(4)
        if opcode == 2:  # LOAD
            b = buffer.read(27)
            c = buffer.read(4)
            assert buffer.read(5) == 0
            registers[c] = b
            i += 5
        elif opcode == 0:  # READ
            b = buffer.read(4)
            c = buffer.read(8)
            d = buffer.read(4)
            assert buffer.read(4) == 0
            address = registers[d] + c
            registers[b] = memory[address]
            i += 3
        elif opcode == 5:  # WRITE
            b = buffer.read(4)
            c = buffer.read(21)
            assert buffer.read(3) == 0
            memory[c] = registers[b]
            i += 4
        elif opcode == 6:  # SHIFT
            b = buffer.read(4)
            c = buffer.read(21)
            assert buffer.read(3) == 0
            memory[c] >>= registers[b]
            i += 4
        else:
            raise ValueError(f"Unknown opcode: {opcode}")
    
    result = {addr: memory[addr] for addr in range(*memory_range)}

    with open(result_path, "w") as f:
        yaml.dump(result, f)

if __name__ == "__main__":
    binary_file = sys.argv[1]
    result_file = sys.argv[2]
    memory_range = tuple(map(int, sys.argv[3:5]))
    interpret(binary_file, result_file, memory_range)
