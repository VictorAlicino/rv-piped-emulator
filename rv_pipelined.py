"""Implementation of a Risc-V Pipelined CPU simulator"""

import logging
from rv_units.register_file import DataRegister, RegisterFile
from rv_units.data_memory import DataMemory
from rv_units.control_unit import ControlUnit
from rv_units.alu import ALU
from rv_units.mux import MUX1

class RiscV:
    """This class simulates a Risc-V Pipelined CPU"""
    def __init__(self):
        self._cycle_counter: int = 1 # For debugging purposes

        # Cache Memory on binary file
        self._data_mem = DataMemory()

        # Pipeline busES
        self._bus_if_id: dict = {}
        self._bus_id_ex: dict = {}
        self._bus_ex_mem: dict = {}
        self._bus_mem_wb: dict = {}

        # Stages variables
        #   IF
        self._pc_src_mux: MUX1 = MUX1() # PC Multiplexer
        self.pc: DataRegister = DataRegister(0)  # Program Counter
        self._imem: dict = {} # Instruction memory

        #  ID
        self._registers: RegisterFile = RegisterFile() # Register File

        # EX
        self._ex_mux: MUX1 = MUX1() # MUX for the ALU
        self._alu: ALU = ALU()

        # MEM
        self._pc_src: bool = False # Conditional branch AND gate
        self._offset: DataRegister = DataRegister(0) # Branch offset

        # WB
        self._wb_mux: MUX1 = MUX1() # MUX for the Write Back stage
        self._wb_rd: DataRegister = DataRegister(0) # Write Back destination register

        self._init_rv()

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

    def _init_rv(self) -> None:
        """Initialize the RISC-V CPU"""
        logging.debug('[Emulator] Initializing RISC-V CPU')
        self._bus_if_id = {
            'pc': DataRegister(0),
            'instruction': '00000000000000000000000000000000'
        }
        self._bus_id_ex = {
            'control': ControlUnit(),
            'pc': DataRegister(0),
            'rr_1': DataRegister(0),
            'rr_2': DataRegister(0),
            'imm': DataRegister(0),
            'instruction': '00000000000000000000000000000000',
            'rd': 0
        }
        self._bus_ex_mem = {
            'control': ControlUnit(),
            'offset': DataRegister(0),
            'ZERO': False,
            'alu_result': DataRegister(0),
            'rr_2': DataRegister(0),
            'rd': 0,
            'instruction': '00000000000000000000000000000000'
        }
        self._bus_mem_wb = {
            'control': ControlUnit(),
            'dmem_read_data': DataRegister(0),
            'alu_result': DataRegister(0),
            'rd': 0,
            'instruction': '00000000000000000000000000000000'
        }
        self._pc_src_mux.write(DataRegister(0), 0)
        self._pc_src_mux.write(DataRegister(0), 1)
        self._ex_mux.write(DataRegister(0), 0)
        self._ex_mux.write(DataRegister(0), 1)
        self._wb_mux.write(DataRegister(0), 0)
        self._wb_mux.write(DataRegister(0), 1)
        logging.debug('[Emulator] RISC-V CPU initialized')

    def _instruction_fetch(self) -> dict:
        """This is the IF stage of the pipeline"""
        logging.debug('-' * 50)
        logging.info('[Emulator] Instruction Fetch')

        self.pc = self._pc_src_mux.read() # Load the PC value from the MUX
        self._pc_src_mux.write(int(self.pc) + 4, 0) # Write the PC+4 value to the MUX on input 0

        # Get the instruction from the memory
        curr_addr = int(self.pc)
        try:
            instruction: str = self._imem[format(curr_addr, '02x')]
        except KeyError:
            logging.debug('[IF] Instruction not found at address %s', hex(curr_addr))
            logging.debug('[IF] Halting...')
            return {}

        # Update the IF/ID bus
        new_bus_if_id = {}
        new_bus_if_id.update({'pc': self.pc}) # Update the IF/ID bus with the PC value
        new_bus_if_id.update({'instruction': instruction})
        logging.debug('[IF] PC at %s', hex(curr_addr))
        logging.debug('[IF] Instruction at %s: %s', hex(curr_addr), instruction)
        return new_bus_if_id

    def _instruction_decode(self, bus_if_id: dict, bus_mem_wb: dict) -> dict:
        """This is the ID stage of the pipeline"""
        if bus_if_id == {}:
            logging.debug('[ID] Halting...')
            return {}
        logging.debug('-' * 50)
        logging.info('[Emulator] Instruction Decode')

        # Get the instruction from the IF/ID bus
        pc = bus_if_id['pc']
        instruction: str = bus_if_id['instruction']
        logging.info('[ID] Instruction: %s', instruction)

        # Control Unit
        control_unit: ControlUnit = ControlUnit()

        # Decoding the Opcode
        opcode: int = int(instruction[25:32], 2)
        logging.debug('[ID] Opcode: %s', bin(opcode))
        control_unit.set_opcode(opcode)
        if opcode == 0b1100011:
            if int(instruction[17:20], 2) == 0b000:
                logging.debug('[ID] BRANCH EQUAL instruction detected')
            if int(instruction[17:20], 2) == 0b001:
                logging.debug('[ID] BRANCH NOT EQUAL instruction detected')

        # Immediate value (Checking if it's I-type or S-type)
        if instruction[25:32] == '0000011' or instruction[25:32] == '0010011': # I-type
            logging.debug('[ID] Immediate value: %s', instruction[0:12])
            imm: DataRegister = self.imm_gen(instruction[0:12])
        elif instruction[25:32] == '0100011': # S-type
            logging.debug('[ID] Immediate value: %s', instruction[0:7] + instruction[20:25])
            imm: DataRegister = self.imm_gen(instruction[0:7] + instruction[20:25])
        elif instruction[25:32] == '1100011': # B-type
            logging.debug('[ID] Immediate value: %s',
                          instruction[0] + instruction[24] +
                          instruction[1:7] + instruction[20:24] + '0')
            imm: DataRegister = self.imm_gen(
                instruction[0] + instruction[24] +
                instruction[1:7] + instruction[20:24] + '0')
        else:
            logging.debug('[ID] Immediate value: %s', instruction[0:8])
            imm: DataRegister = self.imm_gen(instruction[0:8])

        # The next 5 bits are the source register 1
        rr_1: int = int(instruction[12:17], 2)
        # The next 5 bits are the source register 2
        rr_2: int = int(instruction[7:12], 2)
        # The next 5 bits are the destination register
        rd: int = int(instruction[20:25], 2)

        # Operations with the Register File
        # Writing the result to the destination register
        if bus_mem_wb['control'].reg_write: # If the MEM/WB stage is writing to the register
            logging.debug('[ID] Writing %s to register x%s',
                          int(self._wb_mux.read()),
                          bus_mem_wb['rd']) # Write the result to the destination register
            self._registers.write_data(
                bus_mem_wb['rd'],
                self._wb_mux.read()
            )

        # Reading the source registers
        self._registers.select_register(read_register=rr_1, to_read_data=1)
        self._registers.select_register(read_register=rr_2, to_read_data=2)
        logging.debug('[ID] Read Register 1: x%s | Read Register 2: x%s | Write Register: x%s',
                       rr_1, rr_2, rd)

        # Update the ID/EX bus
        new_bus_id_ex = {}
        new_bus_id_ex.update({'control': control_unit})
        new_bus_id_ex.update({'pc': pc})
        new_bus_id_ex.update({'rr_1': self._registers.read_data(1)})
        new_bus_id_ex.update({'rr_2': self._registers.read_data(2)})
        new_bus_id_ex.update({'imm': imm})
        new_bus_id_ex.update({'instruction': instruction})
        new_bus_id_ex.update({'rd': rd})
        return new_bus_id_ex

    def _execute(self, bus_id_ex: dict) -> dict:
        """This is the EX stage of the pipeline"""
        if bus_id_ex == {}:
            logging.debug('[EX] Halting...')
            return {}
        logging.debug('-' * 50)
        logging.info('[Emulator] Execute')

        # Get the values from the ID/EX bus
        control_unit = bus_id_ex['control']
        pc: DataRegister = bus_id_ex['pc']
        imm: DataRegister = bus_id_ex['imm']
        rr_1: DataRegister = bus_id_ex['rr_1']
        rr_2: DataRegister = bus_id_ex['rr_2']
        rd: int = bus_id_ex['rd']
        instruction: str = bus_id_ex['instruction']

        logging.info('[EX] Instruction: %s', instruction)

        # The ALU receives the source registers, the immediate value and the function code
        # and the control signals to perform the operation.
        logging.debug('[EX] ALUOp: %s | Funct: %s', control_unit.alu_op, instruction[0:7][::-1])
        self._alu.alu_control(
            control_signal=control_unit,
            funct3=int(instruction[17:20], 2),
            funct7=int(instruction[0:7], 2)
        )
        # Set the operands:

        # First ALU Operand
        logging.debug('[EX] ALU Operand A: %s | %s',
                      int(rr_1),
                      str(rr_1))
        self._alu.set_op_a(rr_1)
        # Configuring the ALU 2nd input MUX
        self._ex_mux.write(rr_2, 0)
        self._ex_mux.write(imm, 1)
        self._ex_mux.set_select(int(control_unit.alu_src))
        # Second ALU Operand
        logging.debug('[EX] ALU Operand B: %s | %s',
                      int(self._ex_mux.read()),
                      self._ex_mux.read())
        self._alu.set_op_b(self._ex_mux.read())

        # Perform the operation
        self._alu.do_op()
        logging.debug('[EX] ALU Result: %s | %s', self._alu.result(), bin(self._alu.result()))

        # Immediate + PC
        pc_offset = int(pc) + int(imm)
        logging.debug('[EX] PC: %s | Immediate: %s | PC+Immediate: %s', pc, imm, pc_offset)

        # Update the EX/MEM bus
        new_bus_ex_mem = {}
        new_bus_ex_mem.update({'control': control_unit})
        new_bus_ex_mem.update({'offset': pc_offset})
        new_bus_ex_mem.update({'ZERO': self._alu.zero()})
        new_bus_ex_mem.update({'alu_result': self._alu.result()})
        new_bus_ex_mem.update({'rr_2': rr_2})
        new_bus_ex_mem.update({'rd': rd})
        new_bus_ex_mem.update({'instruction': instruction})
        return new_bus_ex_mem

    def _memory_access(self, bus_ex_mem: dict) -> dict:
        """This is the MEM stage of the pipeline"""
        if bus_ex_mem == {}:
            logging.debug('[MEM] Halting...')
            return {}
        logging.debug('-' * 50)
        logging.info('[Emulator] Memory Access')

        # Get the values from the EX/MEM bus
        control_unit: ControlUnit = bus_ex_mem['control']
        offset: DataRegister = bus_ex_mem['offset']
        zero: bool = bus_ex_mem['ZERO']
        alu_result: DataRegister = bus_ex_mem['alu_result']
        rr_2: DataRegister = bus_ex_mem['rr_2']
        rd: int = bus_ex_mem['rd']
        instruction: str = bus_ex_mem['instruction']

        logging.info('[MEM] Instruction: %s', instruction)

        # Conditional Branch
        self._pc_src_mux.write(offset, 1)
        logging.debug('[MEM] Writing %s to PC Multiplexer at input 1', offset)
        self._pc_src = (zero and control_unit.branch)
        self._pc_src_mux.set_select(int(self._pc_src))
        logging.debug('[MEM] Selecting input %s for the PC Multiplexer', int(self._pc_src))

        # Memmory Access
        dmem_read_data: DataRegister = DataRegister(0)

        if control_unit.mem_write:
            # Write the data memory using the ALU result as the address
            # Dev Note: DataRegister should just return bytes if asked so
            logging.debug('[MEM] Writing %s to data memory at address: %s',
                          int(rr_2), hex(alu_result))
            self._data_mem.write(
                address= self._alu.result(),
                data= rr_2)
        if control_unit.mem_read:
            # Read the data memory using the ALU result as the address
            logging.debug('[MEM] Reading data memory at address: %s', hex(alu_result))
            dmem_read_data = self._data_mem.read(address= alu_result)
            logging.debug('[MEM] Data Memory read: %s', dmem_read_data)
        else:
            pass # Logical "Don't Care"

        # Update the MEM/WB bus
        new_bus_mem_wb = {}
        new_bus_mem_wb.update({'control': control_unit})
        new_bus_mem_wb.update({'dmem_read_data': dmem_read_data})
        new_bus_mem_wb.update({'alu_result': alu_result})
        new_bus_mem_wb.update({'rd': rd})
        new_bus_mem_wb.update({'instruction': instruction})
        logging.warning('[MEM] Data Memory dump below:')
        self._data_mem.dump()
        return new_bus_mem_wb

    def _write_back(self, bus_mem_wb) -> None:
        """This is the WB stage of the pipeline"""
        if bus_mem_wb == {}:
            logging.debug('[WB] Halting...')
            raise ValueError('Instruction not found')
        logging.debug('-' * 50)
        logging.info('[Emulator] Write Back')

        # Get the values from the MEM/WB bus
        control_unit: ControlUnit = bus_mem_wb['control']
        dmem_read_data: DataRegister = bus_mem_wb['dmem_read_data']
        alu_result: int = bus_mem_wb['alu_result']
        rd: DataRegister = bus_mem_wb['rd']
        instruction: str = bus_mem_wb['instruction']

        logging.info('[WB] Instruction: %s', instruction)

        # Write Back
        self._wb_mux.write(dmem_read_data, 1)
        self._wb_mux.write(alu_result, 0)
        self._wb_mux.set_select(int(control_unit.mem_to_reg))
        logging.debug('[WB] Write Back MUX at %s: %s',
                        int(control_unit.mem_to_reg),
                        self._wb_mux.read())
        self._wb_rd = DataRegister(rd)
        logging.debug('[WB] Write Back destination register: x%s', rd)

    def cycle(self) -> bool:
        """This is the main loop of the CPU"""
        logging.debug('[Emulator] Starting cycle %d', self._cycle_counter)

        # Getting the last clock bus values
        bus_if_id = self._bus_if_id
        bus_id_ex = self._bus_id_ex
        bus_ex_mem = self._bus_ex_mem
        bus_mem_wb = self._bus_mem_wb

        # IF - Instruction Fetch
        new_bus_if_id = self._instruction_fetch()

        #logging.debug(self._bus_if_id)

        # ID - Instruction Decode
        new_bus_id_ex = self._instruction_decode(bus_if_id, bus_mem_wb)

        #logging.debug(self._bus_id_ex)

        # EX - Execute
        new_bus_ex_mem = self._execute(bus_id_ex)

        #logging.debug(self._bus_ex_mem)

        # MEM - Memory Access
        new_bus_mem_wb = self._memory_access(bus_ex_mem)

        #logging.debug(self._bus_mem_wb)

        # WB - Write Back
        try:
            self._write_back(bus_mem_wb)
        except ValueError:
            logging.debug('[Emulator] Halting...')
            return False

        # Writing the next cycle bus values
        self._bus_if_id = new_bus_if_id
        self._bus_id_ex = new_bus_id_ex
        self._bus_ex_mem = new_bus_ex_mem
        self._bus_mem_wb = new_bus_mem_wb

        logging.debug('[Emulator] Cycle %d finished\n', self._cycle_counter)
        self._cycle_counter += 1
        return True
