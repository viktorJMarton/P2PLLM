"""Select the existing host build route without changing Termux policy."""

import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

root = Path(__file__).resolve().parents[1]
# The offline AI APK must contain the verified runtime and public model. Missing
# local prerequisites are a build blocker, never an apparently usable empty APK.
run_id = datetime.now(timezone.utc).strftime("android-inference-%Y%m%dT%H%M%S%fZ")
prepared = subprocess.run(
    [sys.executable, str(root / "tools/prepare_android_inference.py"),
     "--output", str(root / ".artifacts/checks" / run_id)],
    cwd=root, check=False,
)
if prepared.returncode:
    sys.exit(prepared.returncode)
command = ([sys.executable, str(root / "tools/dev_env.py"), "android-build"]
           if os.name == "nt" else ["bash", str(root / "tools/build-android.sh")])
sys.exit(subprocess.run(command, cwd=root, check=False).returncode)
