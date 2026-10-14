"""Check required evidence and ensure configured API keys are absent from submission files."""
from pathlib import Path
import json
import subprocess
import struct

ROOT = Path(__file__).resolve().parent
NAMES = ["01-function-calling", "02-mcp-client", "03a-auth-ok", "03a-auth-fail",
         "03b-registry", "03c-versioning", "04-verify-setup", "04-adk-current", "04-adk-forecast"]
for name in NAMES:
    data = (ROOT / "screenshots" / f"{name}.png").read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", name
    width, height = struct.unpack(">II", data[16:24])
    assert width >= 800 and height >= 500, name

checks = {"01-function-calling": "[app thực thi]", "02-mcp-client": "Haiphong",
          "03a-auth-ok": "Tools (có auth)", "03a-auth-fail": "401 Unauthorized",
          "03b-registry": "Best match: get_weather_v2 v2.0.0",
          "03c-versioning": '"api_version": "2.0"',
          "04-verify-setup": "All checks passed!"}
for name, text in checks.items():
    assert text in (ROOT / "evidence" / f"{name}.txt").read_text(encoding="utf-8"), name
weather = json.loads((ROOT / "evidence/live-weather.json").read_text(encoding="utf-8"))
assert "Last updated:" in weather["get_current_weather"]
assert weather["get_forecast"].count("Chance of Rain:") == 3

secrets = []
for path in [ROOT / ".env", ROOT / "04-lab/mcp-client/.env"]:
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            name, value = line.split("=", 1)
            if name.strip() in {"GEMINI_API_KEY", "GOOGLE_API_KEY", "WEATHERAPI_KEY"}:
                value = value.strip().strip('"').strip("'")
                if value:
                    secrets.append(value.encode())
files = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT).decode().split("\0")
for name in filter(None, files):
    assert not name.endswith(".env"), "Environment file included"
    path = ROOT / name
    if path.is_file():
        data = path.read_bytes()
        assert not any(key in data for key in secrets), f"Configured secret found in {name}"
print("PASS: 9 PNG screenshots, CLI checkpoints, live weather data, no configured API keys in submission files.")
