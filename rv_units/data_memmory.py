"""Data Memory for the RV32 Pipelined Emulator"""
import logging
from rv_units.register_file import DataRegister


class DataMemory():
    """Data Memory class"""
    def __init__(self):
        try:
            self._data_mem = open('data_memory.bin', 'r+b') #type: ignore
            logging.debug('[Emulator] Data Memory file found')
        except FileNotFoundError:
            self._data_mem = open('data_memory.bin', 'w+b')
            logging.debug('[Emulator] Data Memory file not found, creating a new one')

    def __del__(self):
        self._data_mem.close()

    def write(self, address: int, data: DataRegister) -> None:
        """Write data to the cache memory"""
        logging.debug('[Data Memory] Writing data to address %s (%s)', hex(address), address)
        with open('data_memory.bin', 'r+b') as f:
            f.seek(address*4)
            f.write(int(data).to_bytes(4, 'little', signed=True))

    def read(self, address: int) -> DataRegister:
        """Read data from the cache memory"""
        logging.debug('[Data Memory] Reading data from address %s (%s)', hex(address), address)
        with open('data_memory.bin', 'r+b') as f:
            f.seek(address*4)
            retrieved = f.read(4)
        logging.debug('[Data Memory] Retrieved data: %s | %s',
                      int.from_bytes(retrieved, 'little', signed=True),
                      retrieved.hex())
        data = int.from_bytes(retrieved, 'little', signed=True)
        return DataRegister(data)

    def dump(self) -> None:
        """Dump the data memory to the console"""
        self._data_mem.seek(0)
        while True:
            retrieved = self._data_mem.read(4)
            if not retrieved:
                break
            data = int.from_bytes(retrieved, 'big')
            print(data)

    def seek(self, address) -> None:
        """Seek to a specific address"""
        self._data_mem.seek(address)
