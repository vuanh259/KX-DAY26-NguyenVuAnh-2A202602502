"""Run the real CLI demos and save their output for lab evidence screenshots."""
from pathlib import Path
import html
import os
import subprocess
import sys
import time
import socket
from datetime import datetime

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "evidence"
OUT.mkdir(exist_ok=True)
ENV = os.environ.copy()
ENV.pop("PYTHONHOME", None)
ENV.pop("UV_INTERNAL__PYTHONHOME", None)
ENV.pop("__PYVENV_LAUNCHER__", None)
ENV["PYTHONIOENCODING"] = "utf-8"
for line in (ROOT / ".env").read_text(encoding="utf-8-sig").splitlines():
    if "=" in line and not line.lstrip().startswith("#"):
        name, value = line.split("=", 1)
        if name.strip() in {"GEMINI_API_KEY", "WEATHERAPI_KEY", "MCP_SERVER_URL"}:
            ENV[name.strip()] = value.strip().strip('"').strip("'")

def save(name, command, output, code):
    for key in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "WEATHERAPI_KEY"):
        value = ENV.get(key)
        if value:
            output = output.replace(value, "[KEY HIDDEN]")
    (OUT / f"{name}.txt").write_text(output, encoding="utf-8")
    page = f'''<!doctype html><html lang="vi"><meta charset="utf-8">
<title>{name} — Lab Day 26</title><style>
body{{background:#101820;color:#e9f1f7;margin:24px;font:16px/1.45 Consolas,monospace}}
h1{{font-size:22px;color:#7dd3fc;margin:0 0 8px}}p{{color:#b7c9d8;margin:6px 0}}
pre{{white-space:pre-wrap;overflow-wrap:anywhere;border-top:1px solid #405365;padding-top:14px;font:inherit}}
</style><h1>{html.escape(name)}</h1><p>Actual CLI output / Kết quả chạy thật</p>
<p>{html.escape(command)} | exit code: {code}</p>
<p>Captured: {datetime.now().astimezone().isoformat(timespec="seconds")}</p>
<pre>{html.escape(output)}</pre></html>'''
    (OUT / f"{name}.html").write_text(page, encoding="utf-8")
    print(f"Saved {name}: exit {code}", flush=True)

def run(name, folder, script, env=None, expect_failure=False, python=None):
    interpreter = python or ROOT / ".venv/Scripts/python.exe"
    result = subprocess.run([str(interpreter), "-u", script], cwd=ROOT / folder,
                            env=env or ENV, capture_output=True, encoding="utf-8", timeout=120)
    save(name, f"{folder} > python {script}", result.stdout + result.stderr, result.returncode)
    if (result.returncode == 0) == expect_failure:
        raise RuntimeError(f"Unexpected exit code for {name}: {result.returncode}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        run("04-verify-setup", "04-lab/mcp-client", "verify_setup.py",
            python=ROOT / "04-lab/mcp-client/.venv/Scripts/python.exe")
    else:
        run("01-function-calling", "01-function-calling", "weather_function_calling.py")
        run("02-mcp-client", "02-mcp-basics", "weather_client.py")
        run("03b-registry", "03-production", "registry_client.py")
        run("03c-versioning", "03-production", "versioned_client.py")
        server_env = {**ENV, "MCP_AUTH_TOKEN": "dev-token-abc123"}
        log_path = OUT / "auth-server.txt"
        with log_path.open("w", encoding="utf-8") as log:
            server = subprocess.Popen([str(ROOT / ".venv/Scripts/python.exe"), "-u", "auth_server.py"],
                                      cwd=ROOT / "03-production", env=server_env, stdout=log, stderr=log)
            try:
                for _ in range(40):
                    if server.poll() is not None:
                        raise RuntimeError("Auth server exited before startup")
                    try:
                        with socket.create_connection(("127.0.0.1", 8000), timeout=0.5):
                            break
                    except OSError:
                        time.sleep(0.25)
                run("03a-auth-ok", "03-production", "auth_client.py", env=server_env)
                run("03a-auth-fail", "03-production", "auth_client.py",
                    env={**ENV, "MCP_AUTH_TOKEN": "wrong-token"}, expect_failure=True)
            finally:
                server.terminate()
                server.wait(timeout=10)
        fail_path = OUT / "03a-auth-fail.txt"
        failure = fail_path.read_text(encoding="utf-8")
        server_log = log_path.read_text(encoding="utf-8")
        auth_lines = "\n".join(line for line in server_log.splitlines() if "401" in line or "403" in line)
        if not auth_lines:
            raise RuntimeError("Missing HTTP rejection in auth server log")
        save("03a-auth-fail", "auth_client.py with wrong-token (expected failure)",
             auth_lines + "\n\n" + failure, 1)
