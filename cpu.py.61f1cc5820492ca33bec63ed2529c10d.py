"""CPU functionality."""

import sys
HLT = 0b00000001
PRN = 0b01000111
LDI = 0b10000010
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110
ADD = 0b10100000


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.pc = 0
        self.reg = [0] * 8
        self.op_hlt = False
        self.SP = 0x73  # stack pointer
        self.reg[7] = self.ram[self.SP]
        self.fl = 0b00000000
        self.previous = None

        # operation dictionary
        self.ins = {
            HLT: self.op_halt,
            LDI: self.op_ldi,
            MUL: self.op_mul,
            CMP: self.op_cmp,
            PUSH: self.op_push,
            POP: self.op_pop,
            CALL: self.op_call,
            RET: self.op_ret,
            JMP: self.op_jmp,
            JEQ: self.op_jeq,
            ADD: self.op_add,
            PRN: self.op_prn,
        }

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def op_mul(self, operand_a, operand_b):
        self.alu('MUL', operand_a, operand_b)

    def op_add(self, operand_a, operand_b):
        self.alu('ADD', operand_a, operand_b)

    def op_cmp(self, reg_a, reg_b):
        a = self.reg[reg_a]
        b = self.reg[reg_b]

        if a == b:
            self.fl = 0b00000001
        elif a < b:
            self.fl = 0b00000100
        elif a > b:
            self.fl = 0b00000010
        else:
            self.fl = 0b00000000

    def op_halt(self, address, value):
        self.op_hlt = True

    def op_ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b

    def op_push(self,  operand_a, operand_b):
        self.SP -= 1
        value = self.reg[operand_a]
        self.ram[self.SP] = value

    def op_pop(self, operand_a, operand_b):
        val = self.ram[self.SP]
        self.reg[operand_a] = val
        self.SP += 1

    def op_call(self, operand_a, operand_b):
        self.previous = self.pc + 2
        self.pc = self.reg[operand_a]

    def op_ret(self, operand_a, operand_b):
        self.pc = self.previous
        self.previous = None

    def op_jmp(self, operand_a, operand_b):
        self.pc = self.reg[operand_a]

    def op_jeq(self, operand_a, operand_b):
        if self.fl == 0b1:
            self.op_jmp(operand_a, operand_b)

    def op_jne(self, operand_a, operand_b):
        if self.fl != 0b1:
            self.op_jmp(operand_a, operand_b)

    def op_prn(self, address, operand_b):
        print(self.reg[address])

    def load(self, filename):
        """Load a program into memory."""

        address = 0

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,10
        #     0b00000000,
        #     0b00001010,
        #     0b10000010,  # LDI R1,20
        #     0b00000001,
        #     0b00010100,
        #     0b10000010,  # LDI R2,TEST1
        #     0b00000010,
        #     0b00010011,
        #     0b10100111,  # CMP R0,R1
        #     0b00000000,
        #     0b00000001,
        #     0b01010101,  # JEQ R2
        #     0b00000010,
        #     0b10000010,  # LDI R3,1
        #     0b00000011,
        #     0b00000001,
        #     0b01000111,  # PRN R3
        #     0b00000011,
        #     0b00000001,  # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1
        with open(filename) as file:

            for line in file:
                comment_split = line.split('#')
                instruction = comment_split[0]

                if instruction == '':
                    continue

                first_bit = instruction[0]

                if first_bit == "0" or first_bit == "1":

                    self.ram[address] = int(instruction[:8], 2)
                    address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while not self.op_hlt:
            # self.trace()
            ir = self.ram[self.pc]

            print(ir)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            op_size = ir >> 6
            ins_set = ((ir >> 4) & 0b1) == 1

            if ir in self.ins:
                self.ins[ir](operand_a, operand_b)
            else:
                print(f"Error: Instruction {ir} not found")
                exit()

            if not ins_set:
                self.pc += op_size + 1
