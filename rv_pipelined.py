"""Implementation of a Risc-V Pipelined CPU simulator"""

import logging
from rv_units.register_file import DataRegister, RegisterFile
from rv_units.data_memmory import DataMemory
from rv_units.control_unit import ControlUnit
from rv_units.mux import MUX1

class RiscV:
    """This class simulates a Risc-V Pipelined CPU"""
    def __init__(self):
        self._cycle_counter: int = 1 # For debugging purposes

        # Cache Memory on binary file
        self._data_mem = DataMemory()

        # Pipeline BUSES
        self._bus_if_id: dict = {}
        self._bus_id_ex: dict = {}
        self._bus_ex_mem: dict = {}
        self._bus_mem_wb: dict = {}

        # Stages variables
        #   IF
        self._if_mux: MUX1 = MUX1() # PC Multiplexer
        self.pc: DataRegister = DataRegister(0)  # Program Counter
        self._imem: dict = {} # Instruction memory

        #  ID
        self._registers: RegisterFile = RegisterFile() # Register File
        self._control: ControlUnit = ControlUnit() # Control Unit


    def __del__(self):
        logging.debug('[Emulator] Closing data memory file')
        self._data_mem.__del__()

    def pc_value(self) -> int:
        """Returns the current value of the program counter register"""
        return int(self.pc)

    def dump_memory(self):
        """Dump the memory to the console"""
        logging.debug('[Emulator] Dumping loaded memory to STDIN...')
        for addr, instruction in self._imem.items():
            print(f'0x{addr} {instruction}')

    def load_program(self, file_name):
        """Load the program from a file"""
        # Test if the file is empty
        if file_name == '':
            raise ValueError('Program path was not provided')
        logging.debug('[Emulator] Loading memory from %s', file_name)
        with open(file_name, encoding='utf-8') as f:
            temp_last_addr = 0
            for i, line in enumerate(f):
                if line == "\n":
                    continue
                if i == 0:
                    addr = format(i, '02x')
                else:
                    temp_last_addr = temp_last_addr + 4
                    addr = format(temp_last_addr, '02x')
                self._imem.update({addr: line.rstrip()})
        logging.debug('[Emulator] Loaded %d instructions', len(self._imem))

    def instruction_at_address(self, address: int):
        """Returns the instruction at the given address"""
        hex_addr = format(address, '02x')
        try:
            return self._imem[hex_addr]
        except KeyError:
            return None

    @staticmethod
    def imm_gen(imm: str) -> DataRegister:
        """This function receives a 12-bit immediate value and sign extends it to 32 bits"""
        temp = int(imm, 2).to_bytes(4, byteorder='big', signed=True)
        imm32: DataRegister = DataRegister(bytearray.fromhex(temp.hex()))
        logging.debug('[ImmGen] Immediate-32 value: %s | %s', int(imm32), imm32)
        return imm32

    def _instruction_fetch(self) -> None:
        """This is the IF stage of the pipeline"""
        logging.info('[Emulator] Instruction Fetch')

        self.pc = self._if_mux.read() # Load the PC value from the MUX
        self._if_mux.write(self.pc, 0) # Write the PC+4 value to the MUX on input 0

        # Get the instruction from the memory
        curr_addr = int(self.pc)
        try:
            instruction: str = self._imem[format(curr_addr, '02x')]
        except KeyError as exc:
            logging.debug('[CPU] Instruction not found at address %s', hex(curr_addr))
            logging.debug('[CPU] Halting...\n')
            self._cycle_counter = 0
            raise exc.add_note('Instruction not found')

        # Update the IF/ID bus
        self._bus_if_id.update({'pc': self.pc}) # Update the IF/ID bus with the PC value
        self._bus_if_id.update({'instruction': instruction})
        logging.debug('[IF] PC at %s', hex(curr_addr))
        logging.debug('[IF] Instruction at %s: %s', hex(curr_addr), instruction)

    def _instruction_decode(self) -> None:
        """This is the ID stage of the pipeline"""
        logging.info('[Emulator] Instruction Decode')

        # Get the instruction from the IF/ID bus
        instruction: str = self._bus_if_id['instruction']

        # Decoding the Opcode
        opcode: int = int(instruction[25:32], 2)
        logging.debug('[CPU] Opcode: %s', bin(opcode))
        if opcode == 0b1100011:
            if int(instruction[17:20], 2) == 0b000:
                logging.debug('[CPU] BRANCH EQUAL instruction detected')
            if int(instruction[17:20], 2) == 0b001:
                logging.debug('[CPU] BRANCH NOT EQUAL instruction detected')

        # Immediate value (Checking if it's I-type or S-type)
        if instruction[25:32] == '0000011' or instruction[25:32] == '0010011': # I-type
            logging.debug('[CPU] Immediate value: %s', instruction[0:12])
            imm: DataRegister = self.imm_gen(instruction[0:12])
        elif instruction[25:32] == '0100011': # S-type
            logging.debug('[CPU] Immediate value: %s', instruction[0:7] + instruction[20:25])
            imm: DataRegister = self.imm_gen(instruction[0:7] + instruction[20:25])
        elif instruction[25:32] == '1100011': # B-type
            logging.debug('[CPU] Immediate value: %s',
                          instruction[0] + instruction[24] +
                          instruction[1:7] + instruction[20:24] + '0')
            imm: DataRegister = self.imm_gen(
                instruction[0] + instruction[24] + 
                instruction[1:7] + instruction[20:24] + '0')
        else:
            logging.debug('[CPU] Immediate value: %s', instruction[0:8])
            imm: DataRegister = self.imm_gen(instruction[0:8])

        # The next 5 bits are the source register 1
        rr_1: int = int(instruction[12:17], 2)
        # The next 5 bits are the source register 2
        rr_2: int = int(instruction[7:12], 2)
        # The next 5 bits are the destination register
        rd: int = int(instruction[20:25], 2)

        logging.debug('[CPU] Read Register 1: x%s | Read Register 2: x%s | Write Register: x%s',
                       rr_1, rr_2, rd)

        # Decode the instruction
        self._control.set_opcode(opcode)

        # Update the ID/EX bus
        self._bus_id_ex.update({'imm': imm})
        self._bus_id_ex.update({'rr_1': rr_1})
        self._bus_id_ex.update({'rr_2': rr_2})


    def cycle(self) -> bool:
        """This is the main loop of the CPU"""
        logging.debug('[Emulator] Starting cycle %d', self._cycle_counter)

        # TODO: IF - Instruction Fetch
        try:
            self._instruction_fetch()
        except KeyError:
            return False
        # TODO: ID - Instruction Decode
        self._instruction_decode()
        # TODO: EX - Execute
        #self._execute()
        # TODO: MEM - Memory Access
        #self._memory_access()
        # TODO: WB - Write Back
        #self._write_back()

        self._cycle_counter += 1
        return False
