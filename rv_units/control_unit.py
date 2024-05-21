"""This module contains the Control Unit"""
import logging

class ControlUnit:
    """This class represents the Control Unit of the CPU"""
    def __init__(self):
        self.alu_src: bool = False
        self.mem_to_reg: bool = False
        self.reg_write: bool = False
        self.mem_read: bool = False
        self.mem_write: bool = False
        self.branch: bool = False
        self.alu_op: tuple[bool, bool] = (False, False)

    def _set_control_signals(self, signals: dict):
        """Set the control signals from a dictionary of values"""
        for signal, value in signals.items():
            setattr(self, signal, value)

    def set_opcode(self, opcode: int):
        """Receive the opcode and set the control signals accordingly"""
        logging.debug('[Control Unit] Received opcode: %s | %s', opcode, bin(opcode))

        match opcode:
            case 0b0110011: # R-type
                self._set_control_signals({
                'alu_src': False,
                'mem_to_reg': False,
                'reg_write': True,
                'mem_read': False,
                'mem_write': False,
                'branch': False,
                'alu_op': (False, True)
                })
                logging.debug('[Control Unit] R-type instruction detected')
            case 0b0000011: # LW
                self._set_control_signals({
                'alu_src': True,
                'mem_to_reg': True,
                'reg_write': True,
                'mem_read': True,
                'mem_write': False,
                'branch': False,
                'alu_op': (False, False)
                })
                logging.debug('[Control Unit] LOAD WORD instruction detected')
            case 0b0100011: #SW
                self._set_control_signals({
                'alu_src': True,
                'reg_write': False,
                'mem_read': False,
                'mem_write': True,
                'branch': False,
                'alu_op': (False, False)
                })
                logging.debug('[Control Unit] STORE WORD instruction detected')
            case 0b1100011: # BEQ
                self._set_control_signals({
                'alu_src': False,
                'reg_write': False,
                'mem_read': False,
                'mem_write': False,
                'branch': True,
                'alu_op': (True, False)
                })
                logging.debug('[Control Unit] BRANCH instruction detected')
            case 0b1100011: # BNE
                self._set_control_signals({
                'alu_src': False,
                'reg_write': False,
                'mem_read': False,
                'mem_write': False,
                'branch': True,
                'alu_op': (False, True)
                })
                logging.debug('[Control Unit] BRANCH NOT EQUAL instruction detected')
            case 0b0010011: # ADDI
                self._set_control_signals({
                'alu_src': True,
                'mem_to_reg': False,
                'reg_write': True,
                'mem_read': False,
                'mem_write': False,
                'branch': False,
                'alu_op': (False, False)
                })
                logging.debug('[Control Unit] ADD IMMEDIATE instruction detected')
            case _ : logging.error('[Control Unit] Opcode not recognized')

    def __str__(self):
        return (
            f'           |Branch-------{self.branch}\n'
            f'           |Mem Read-----{self.mem_read}\n'
            f'           |Mem to Reg---{self.mem_to_reg}\n'
            f'Control--->|ALU Op-------{self.alu_op}\n'
            f'           |Mem Write----{self.mem_write}\n'
            f'           |ALU Src------{self.alu_src}\n'
            f'           |Reg Write----{self.reg_write}\n'
        )
