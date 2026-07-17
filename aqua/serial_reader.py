"""
Live sensor input (optional) — read pH/temperature from the real hardware.

Two supported paths, matching the device table:
  * USB serial straight from the Arduino Uno  (needs `pip install pyserial`)
  * HTTP JSON from the NodeMCU's Wi-Fi web server (uses only the stdlib)

Both are OPTIONAL. The POC runs entirely on the pendrive / mock data without
either, so the demo never depends on hardware being present.

Expected Arduino serial line:   PH:7.24 TEMP:26.5
Expected NodeMCU JSON:          {"ph": 7.24, "temperature": 26.5}
"""
from __future__ import annotations

import json
import re
import urllib.request

_LINE_RE = re.compile(r"PH:\s*([-\d.]+)(?:.*TEMP:\s*([-\d.]+))?", re.IGNORECASE)


def read_from_serial(port: str, baud: int = 9600, timeout: float = 3.0) -> dict:
    """Read one pH/temperature reading from the Arduino over USB serial."""
    try:
        import serial  # type: ignore
    except ImportError as e:
        raise RuntimeError("pyserial not installed. Run: pip install pyserial") from e

    with serial.Serial(port, baud, timeout=timeout) as ser:
        for _ in range(20):  # skip banner lines, wait for a data line
            line = ser.readline().decode("utf-8", "ignore").strip()
            m = _LINE_RE.search(line)
            if m:
                ph = float(m.group(1))
                temp = float(m.group(2)) if m.group(2) else None
                return {"ph": ph, "temperature": temp, "source": f"serial:{port}"}
    raise TimeoutError(f"No pH line seen on {port} within timeout.")


def read_from_nodemcu(url: str, timeout: float = 3.0) -> dict:
    """Read a JSON reading from the NodeMCU Wi-Fi endpoint, e.g. http://<ip>/ph."""
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return {
        "ph": float(data["ph"]),
        "temperature": float(data["temperature"]) if data.get("temperature") is not None else None,
        "source": f"nodemcu:{url}",
    }
