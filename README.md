# Touchscreen Toggle

Simple Windows 10/11 scripts to disable or enable your touchscreen with one double-click.

Automatically detects your touchscreen hardware ID — no manual configuration needed.

---

## Requirements

- Windows 10 or Windows 11
- Python 3.8 or newer — [download here](https://www.python.org/downloads/)  
  *(check **"Add python.exe to PATH"** during installation)*
- No extra Python packages needed

---

## Usage

### Disable touchscreen
Double-click `disable_touchscreen.bat`

### Enable touchscreen
Double-click `enable_touchscreen.bat`

Both scripts will ask Windows for administrator permission automatically. This is required because enabling and disabling hardware devices is a protected action in Windows.

---

## Files

| File | Description |
|---|---|
| `disable_touchscreen.bat` | Run this to disable the touchscreen |
| `enable_touchscreen.bat` | Run this to re-enable the touchscreen |
| `disable_touchscreen.py` | Python script called by the disable bat |
| `enable_touchscreen.py` | Python script called by the enable bat |
| `touchscreen_toggle.log` | Created automatically; logs what happened |

---

## How it works

1. Uses Windows PowerShell's `Get-PnpDevice` to find your touchscreen by its friendly name (`HID-compliant touch screen`).
2. Calls `Disable-PnpDevice` or `Enable-PnpDevice` — the same thing Device Manager does internally.
3. Falls back to a broader search (matching "touchscreen", "touch screen", or "digitizer") if the strict name isn't found.

No registry edits, no driver changes, no third-party tools.

---

## Troubleshooting

**"No touchscreen device was found"**  
Your touchscreen might show under a different name in Device Manager. Open Device Manager → Human Interface Devices and look for your touchscreen. If you find it, note its exact name and open an issue or manually edit the script's search string.

**Script doesn't seem to do anything**  
Make sure you accepted the administrator prompt. Without it, PowerShell can't change device states.

**Touchscreen is stuck disabled**  
Run `enable_touchscreen.bat`. If that doesn't work, open Device Manager → Human Interface Devices, find your touchscreen (it will have a small down-arrow icon), right-click it, and choose Enable device.

---

## Notes

- A log file `touchscreen_toggle.log` is created next to the scripts so you can see what happened if something goes wrong.
- Both scripts only touch devices identified as touchscreens — trackpads, mice, pens, and other HID devices are left alone.
- Does not modify any Roblox, game, or app files or settings.
