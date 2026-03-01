"""
Starts main.py as a fully detached Windows process.
This script exits immediately after spawning; child survives SSH disconnect.
"""
import subprocess
import os
import sys

PYTHON = r"C:\FreedomWalletBot\.venv\Scripts\python.exe"
MAIN   = r"C:\FreedomWalletBot\main.py"
CWD    = r"C:\FreedomWalletBot"
LOG    = r"C:\FreedomWalletBot\startup_log.txt"

DETACHED_PROCESS       = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

with open(LOG, "w") as logf:
    proc = subprocess.Popen(
        [PYTHON, MAIN],
        cwd=CWD,
        stdout=logf,
        stderr=logf,
        close_fds=True,
        creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
    )
    print(f"Bot started with PID: {proc.pid}")
    sys.exit(0)
