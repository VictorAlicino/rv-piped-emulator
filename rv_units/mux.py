"""This module contains the Multiplexers class"""
from rv_units.register_file import DataRegister

class MUX1:
    """This class represents a 1-bit Multiplexer"""
    def __init__(self, _0 = 0, _1 = 0, select: int = 0):
        self._input0: DataRegister | int = _0
        self._input1: DataRegister | int = _1
        self._select: int = select

    def write(self, value: DataRegister, select: int) -> None:
        """Write data to the multiplexer"""
        match select:
            case 1:
                self._input1 = value
            case _:
                self._input0 = value

    def read(self) -> DataRegister | int:
        """Read the selected input"""
        match self._select:
            case 1:
                return self._input1
            case _:
                return self._input0

    def set_select(self, select: int) -> None:
        """Set the select signal"""
        if select < 0 or select > 1:
            raise ValueError('Invalid select signal')
        self._select = select

    def __str__(self):
        return (f'Input0: {self._input0} |'
                f'Input1: {self._input1} |'
                f' Select: {self._select} = {self.read()}')

class MUX2:
    """This class represents a 2-bit Multiplexer"""
    def __init__(self, _0 = 0, _1 = 0, _2 = 0, select:int = 0):
        self._input0: DataRegister | int = _0
        self._input1: DataRegister | int = _1
        self._input2: DataRegister | int = _2
        self._select: int = select

    def write(self, value: DataRegister, select: int) -> None:
        """Write data to the multiplexer"""
        match select:
            case 1:
                self._input1 = value
            case 2:
                self._input2 = value
            case _:
                self._input0 = value

    def read(self) -> DataRegister | int:
        """Read the selected input"""
        match self._select:
            case 1:
                return self._input1
            case 2:
                return self._input2
            case _:
                return self._input0

    def set_select(self, select: int) -> None:
        """Set the select signal"""
        if select < 0 or select > 2:
            raise ValueError('Invalid select signal')
        self._select = select

    def __str__(self):
        return (f'Input0: {self._input0} |'
                f'Input1: {self._input1} |'
                f'Input2: {self._input2} |'
                f' Select: {self._select} = {self.read()}')
