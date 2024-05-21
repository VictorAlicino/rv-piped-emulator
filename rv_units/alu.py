"""This module contains the ALU class and the ALUOp enumeration"""
from dataclasses import dataclass
import logging
from rv_units.control_unit import ControlUnit
from rv_units.register_file import DataRegister

@dataclass
class ALUmux:
    """This is the second operator MUX of the ALU"""
    a: DataRegister
    b: int

class ADDER:
    """Adder generic class"""
    def __init__(self):
        pass

    @classmethod
    def do(cls, op_a: int | DataRegister, op_b: int | DataRegister) -> int:
        """Perform the addition"""
        a: int = int(op_a)
        b: int = int(op_b)
        return a + b

class ALU:
    """This is the ALU of the CPU"""
    def __init__(self):
        self._a: int = 0
        self._b: int = 0
        self._result: int = 0
        self._zero: bool = False
        self._control: int = 0b0000

    def set_op_a(self, operand: DataRegister) -> None:
        """Set the first operand"""
        self._a = int(operand)

    def set_op_b(self, operand: int | DataRegister) -> None:
        """Set the second operand"""
        self._b = int(operand)

    def result(self) -> int:
        """Return the result of the operation"""
        return self._result

    def zero(self) -> bool:
        """Return the zero flag"""
        return self._zero

    def alu_control(self, control_signal: ControlUnit, funct3: int, funct7: int) -> None:
        """Set the ALU control signal"""
        logging.debug('[ALU Control] Setting ALU control signal')
        logging.debug('[ALU Control] ALUOp: %s', control_signal.alu_op)
        logging.debug('[ALU Control] Funct3: %s Funct7: %s', bin(funct3), bin(funct7))
        if control_signal.alu_op[0] is True:
            # Branch Equal (BEQ)
            self._control = 0b0110
        else:
            if control_signal.alu_op[1] is True:
                if funct7 == 0b0100000:
                    # SUB operation
                    self._control = 0b0110
                else:
                    match funct3:
                        case 0b0000: # ADD
                            self._control = 0b0010
                        case 0b0111: # AND
                            self._control = 0b0000
                        case 0b0110: # OR
                            self._control = 0b0001
                        case _: # Default
                            raise ValueError('Invalid function code')
            else:
                # Load or Store Word (LW | SW)
                self._control = 0b0010
        self._zero = False

    def do_op(self) -> None:
        """Perform the operation"""
        if self._control is None:
            raise ValueError('Operation not set')

        match self._control:
            case 0b0010:
                # ADD operation
                self._result = self._a + self._b
                logging.debug('[ALU] ADD operation performed: %s + %s = %s',
                              self._a,
                              self._b,
                              self._result)
            case 0b0110:
                # SUB operation
                self._result = self._a - self._b
                logging.debug('[ALU] SUB operation performed: %s - %s = %s',
                              self._a,
                              self._b,
                              self._result)
            case 0b0000:
                # AND operation
                self._result = self._a & self._b
                logging.debug('[ALU] AND operation performed: %s & %s = %s',
                              self._a,
                              self._b,
                              self._result)
            case 0b0001:
                # OR operation
                self._result = self._a | self._b
                logging.debug('[ALU] OR operation performed: %s | %s = %s',
                              self._a,
                              self._b,
                              self._result)
            case 0b0111:
                # SLT operation
                self._result = int(self._a < self._b)
                logging.debug('[ALU] SLT operation performed: %s < %s = %s',
                              self._a,
                              self._b,
                              self._result)
            case _:
                print('ALUControl:', bin(self._control))
                raise ValueError('Invalid operation')

        if self._result == 0:
            logging.debug('[ALU] Zero flag set')
            self._zero = True
