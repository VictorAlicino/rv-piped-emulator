"""This module contains the Multiplexers class"""
from rv_units.register_file import DataRegister

class MUX1:
    """This class represents a Multiplexer"""
    def __init__(self, _0 = 0, _1 = 0, select = False):
        self._input0: DataRegister | int = _0
        self._input1: DataRegister | int = _1
        self._select: bool = select

    def write(self, value: DataRegister, select: bool) -> None:
        """Write data to the multiplexer"""
        if select:
            self._input1 = value
        else:
            self._input0 = value

    def read(self) -> DataRegister | int:
        """Read the selected input"""
        if self._select:
            return self._input1
        return self._input0

    def set_select(self, select: bool) -> None:
        """Set the select signal"""
        self._select = select

    def __str__(self):
        return f'Input0: {self._input0} | Input1: {self._input1} | Select: {self._select}'

    def __repr__(self):
        return f'Input0: {self._input0} | Input1: {self._input1} | Select: {self._select}'
