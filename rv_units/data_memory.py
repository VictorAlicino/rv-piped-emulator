"""Data Memory for the RV32 Single Cycle Emulator"""
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
            f.seek(address)
            f.write(int(data).to_bytes(4, 'little', signed=True))

    def read(self, address: int) -> DataRegister:
        """Read data from the cache memory"""
        logging.debug('[Data Memory] Reading data from address %s (%s)', hex(address), address)
        with open('data_memory.bin', 'r+b') as f:
            f.seek(address)
            retrieved = f.read(4)
        logging.debug('[Data Memory] Retrieved data: %s | %s',
                      int.from_bytes(retrieved, 'little', signed=True),
                      retrieved.hex())
        data = int.from_bytes(retrieved, 'little', signed=True)
        return DataRegister(data)

    def dump(self) -> None:
        """Dump the data memory"""
        logging.debug('[Data Memory] Dumping data memory')
        with open('data_memory.bin', 'r+b') as f:
            f.seek(0)
            data = f.read()

        # Print the header
        header = "       " + " ".join(f"{i:02X}" for i in range(16))
        separator = "   " + "-" * (3 * 16 + 1) + " " + "-" * 16
        print(header)
        print(separator)

        # Print the data in the desired format
        for offset in range(0, len(data), 16):
            chunk = data[offset:offset + 16]
            hex_values = " ".join(f"{byte:02X}" for byte in chunk)
            ascii_values = "".join(chr(byte) if 32 <= byte < 127 else '.' for byte in chunk)
            print(f"{offset:04X} │ {hex_values:<47} │ {ascii_values}")

        #logging.debug('[Data Memory] Data: %s', data.hex())

    def seek(self, address) -> None:
        """Seek to a specific address"""
        self._data_mem.seek(address)
