"""This is a simple RISC-V Pipelined CPU simulator."""

import sys
import logging
import time
import tkinter as tk
from tkinter import filedialog
from rv_pipelined import RiscV


def _main() -> int:
    """Main function"""
    root = tk.Tk()
    root.withdraw()
    if len(sys.argv) > 1:
        if sys.argv[1] == '--debug':
            logging.basicConfig(encoding='utf-8', level=logging.DEBUG,
                                #format='[%(asctime)s|%(funcName)s @ '
                                #  '%(filename)s:%(lineno)s] %(message)s',
                                format='%(asctime)s | %(message)s',
                                handlers=[
                                    logging.FileHandler("debug.log"),
                                    logging.StreamHandler()
                                ]
                                )
        else:
            print('Invalid arguments')
            return 1
    else:
        logging.basicConfig(encoding='utf-8', level=logging.DEBUG,
                            format='%(asctime)s %(message)s',
                            handlers=[logging.FileHandler("debug.log")]
                            )

    logging.debug('[Emulator] Starting RISC-V Pipelined CPU simulator')
    risc_v = RiscV()
    file_path = filedialog.askopenfilename() # Won't work with TUI

    try:
        risc_v.load_program(file_path)
    except ValueError as e:
        print(f'Failed to load program: {e}')
        sys.exit(1)

    start_time = time.time()
    while risc_v.cycle():
        pass
    end_time = time.time()
    execution_time = end_time - start_time
    logging.debug(f'Execution time: {execution_time/1000} s')

    return 0

if __name__ == "__main__":
    sys.exit(_main())
