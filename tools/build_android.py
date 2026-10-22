"""Select the existing host build route without changing Termux policy."""

import os
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
command = ([sys.executable, str(root / "tools/dev_env.py"), "android-build"]
           if os.name == "nt" else ["bash", str(root / "tools/build-android.sh")])
sys.exit(subprocess.run(command, cwd=root, check=False).returncode)
