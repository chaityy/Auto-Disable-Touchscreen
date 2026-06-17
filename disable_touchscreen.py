"""
disable_touchscreen.py

Finds your touchscreen device automatically and disables it.
Must be run as Administrator (the .bat launcher handles this).

No external dependencies — uses only Python standard library + PowerShell.
"""

from __future__ import annotations

import ctypes
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
LOG_PATH = SCRIPT_DIR / "touchscreen_toggle.log"


# ── Logging ──────────────────────────────────────────────────────────────────

def log(message: str) -> None:
    from datetime import datetime
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    existing = LOG_PATH.read_text(encoding="utf-8") if LOG_PATH.exists() else ""
    LOG_PATH.write_text(existing + f"[{stamp}] {message}\n", encoding="utf-8")


# ── Admin elevation ───────────────────────────────────────────────────────────

def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def relaunch_as_admin() -> None:
    params = " ".join(f'"{arg}"' for arg in sys.argv)
    result = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, params, str(SCRIPT_DIR), 1
    )
    if result <= 32:
        print("ERROR: Could not open an admin prompt. Right-click the .bat and choose 'Run as administrator'.")
        input("Press Enter to exit...")
    sys.exit(0)


# ── PowerShell helper ─────────────────────────────────────────────────────────

def powershell(script: str) -> str:
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout).strip())
    return result.stdout.strip()


# ── Touchscreen detection ─────────────────────────────────────────────────────

def find_touchscreen_ids() -> list[str]:
    """
    Look for HID-compliant touch screen devices.
    Deliberately strict: only matches the standard Windows name so we don't
    accidentally disable a pen, trackpad, or other HID device.
    """
    script = r"""
Get-PnpDevice -Class HIDClass -ErrorAction SilentlyContinue |
Where-Object {
    $_.FriendlyName -eq 'HID-compliant touch screen' -and
    $_.InstanceId -notmatch '^ROOT\\'
} |
Select-Object -ExpandProperty InstanceId -Unique
"""
    output = powershell(script)
    ids = [line.strip() for line in output.splitlines() if line.strip()]

    # Fallback: broader search if the strict one found nothing
    if not ids:
        fallback_script = r"""
Get-PnpDevice -ErrorAction SilentlyContinue |
Where-Object {
    ($_.FriendlyName -match 'touch screen|touchscreen|digitizer') -and
    $_.InstanceId -notmatch '^ROOT\\'
} |
Select-Object -ExpandProperty InstanceId -Unique
"""
        output = powershell(fallback_script)
        ids = [line.strip() for line in output.splitlines() if line.strip()]

    return ids


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    if sys.platform != "win32":
        print("This script only works on Windows.")
        return 1

    if not is_admin():
        relaunch_as_admin()

    print("Searching for touchscreen device...")
    log("disable_touchscreen.py started.")

    try:
        ids = find_touchscreen_ids()
    except Exception as exc:
        print(f"ERROR while searching for devices: {exc}")
        log(f"ERROR during detection: {exc}")
        input("Press Enter to exit...")
        return 1

    if not ids:
        msg = (
            "No touchscreen device was found.\n\n"
            "If your touchscreen is listed under a different name in Device Manager,\n"
            "you can disable it manually there.\n\n"
            "Device Manager path: Human Interface Devices > your touchscreen"
        )
        print(msg)
        log("No touchscreen device found.")
        input("Press Enter to exit...")
        return 1

    print(f"Found {len(ids)} touchscreen device(s):")
    for device_id in ids:
        print(f"  {device_id}")

    errors = 0
    for device_id in ids:
        escaped = device_id.replace("'", "''")
        try:
            powershell(f"Disable-PnpDevice -InstanceId '{escaped}' -Confirm:$false")
            print(f"DISABLED: {device_id}")
            log(f"Disabled: {device_id}")
        except Exception as exc:
            print(f"ERROR disabling {device_id}: {exc}")
            log(f"ERROR disabling {device_id}: {exc}")
            errors += 1

    if errors == 0:
        print("\nTouchscreen successfully disabled.")
        print("Run enable_touchscreen.bat to turn it back on.")
    else:
        print(f"\nFinished with {errors} error(s). Check touchscreen_toggle.log for details.")

    log("disable_touchscreen.py finished.")
    input("\nPress Enter to exit...")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
