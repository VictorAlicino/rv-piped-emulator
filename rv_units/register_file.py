"""Registers Bank"""

import logging
from typing import Final

class DataRegister():
    """Structure to represent a Register"""

    def __init__(self, data: bytearray | int) -> None:
        if isinstance(data, bytearray):
            self.data: bytearray = data# 32 bits
            return
        self.data = data.to_bytes(4, byteorder='big', signed=True) # type: ignore

    def __str__(self):
        # Printing all the bits
        return ''.join(format(x, '08b') for x in self.data)

    def __int__(self):
        return int.from_bytes(self.data, byteorder='big', signed=True)

    def __bytes__(self):
        return self.data

    def write(self, value: bytearray) -> None:
        """Write data to a byte"""
        self.data = value

    def write_int(self, value: int) -> None:
        """Write an integer to the register"""
        self.data = value.to_bytes(4, byteorder='big', signed=True) # type: ignore

    def wipe(self) -> None:
        """Set all bits to 0"""
        self.data = (0 for _ in range(4)) # type: ignore


class RegisterFile():
    """Structure to represent the Register Bank"""
    def __init__(self):
        self.x0: Final[DataRegister] = DataRegister(0) # Zero Register (Always 0) # type: ignore
        self.x1: DataRegister = DataRegister(0)  # Return Address
        self.x2: DataRegister = DataRegister(0)  # Stack Pointer
        self.x3: DataRegister = DataRegister(0)  # Global Pointer
        self.x4: DataRegister = DataRegister(0)  # Thread Pointer
        self.x5: DataRegister = DataRegister(0)  # Temporary 0
        self.x6: DataRegister = DataRegister(0)  # Temporary 1
        self.x7: DataRegister = DataRegister(0)  # Temporary 2
        self.x8: DataRegister = DataRegister(0)  # Frame Pointer
        self.x9: DataRegister = DataRegister(0)  # Saved Register 1
        self.x10: DataRegister = DataRegister(0) # Function Argument 0 / Return Value 0
        self.x11: DataRegister = DataRegister(0) # Function Argument 1 / Return Value 1
        self.x12: DataRegister = DataRegister(0) # Function Argument 2
        self.x13: DataRegister = DataRegister(0) # Function Argument 3
        self.x14: DataRegister = DataRegister(0) # Function Argument 4
        self.x15: DataRegister = DataRegister(0) # Function Argument 5
        self.x16: DataRegister = DataRegister(0) # Function Argument 6
        self.x17: DataRegister = DataRegister(0) # Function Argument 7
        self.x18: DataRegister = DataRegister(0) # Saved Register 2
        self.x19: DataRegister = DataRegister(0) # Saved Register 3
        self.x20: DataRegister = DataRegister(0) # Saved Register 4
        self.x21: DataRegister = DataRegister(0) # Saved Register 5
        self.x22: DataRegister = DataRegister(0) # Saved Register 6
        self.x23: DataRegister = DataRegister(0) # Saved Register 7
        self.x24: DataRegister = DataRegister(0) # Saved Register 8
        self.x25: DataRegister = DataRegister(0) # Saved Register 9
        self.x26: DataRegister = DataRegister(0) # Saved Register 10
        self.x27: DataRegister = DataRegister(0) # Saved Register 11
        self.x28: DataRegister = DataRegister(0) # Temporary 3
        self.x29: DataRegister = DataRegister(0) # Temporary 4
        self.x30: DataRegister = DataRegister(0) # Temporary 5
        self.x31: DataRegister = DataRegister(0) # Temporary 6

        self._read_data_1: int = 0
        self._read_data_2: int = 0

    def zero(self) -> DataRegister:
        """Return the zero register"""
        return self.x0

    def get_reg(self, reg_name: int) -> DataRegister:
        """Get the register by its name"""
        return getattr(self, f'x{reg_name}')

    def select_register(self,
                        read_register: int,
                        to_read_data: int) -> None:
        """Set the value on Read Data 1 or Read Data 2"""
        if to_read_data < 1 or to_read_data > 2:
            raise ValueError('Invalid Read ouput')

        setattr(self, f'read_data_{to_read_data}', read_register)

    def read_data(self, read_data: int) -> DataRegister:
        """Return the selected register"""
        if read_data < 1 or read_data > 2:
            raise ValueError('Invalid Read ouput')
        return getattr(self, f'x{getattr(self, f"read_data_{read_data}")}')

    def write_data(self, write_register: int, value: DataRegister) -> None:
        """Write data to a register"""
        logging.debug('[Register File] Writing at register --> x%s = %s',
                      write_register,
                      value)
        if write_register == 0:
            raise ValueError('Cannot write to x0')
        getattr(self, f'x{write_register}').write(value.data)

    def dump(self, see_bits: bool = False) -> None:
        """Print all the registers"""
        logging.debug('[Register File] Dumping all registers on STDIN')
        if see_bits:
            for i in range(32):
                logging.debug('[Register File] x%s = %s | %s',
                              i,
                              int(getattr(self, f"x{i}")),
                              getattr(self, f"x{i}") )
        else:
            for i in range(32):
                logging.debug('[Register File] x%s = %s',
                              i,
                              int(getattr(self, f"x{i}")))
