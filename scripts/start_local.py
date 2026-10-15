"""Start local reviewer processes without exposing credentials."""

import json
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


def port_available(port: int) -> bool:
    with socket.socket() as listener:
        try:
            listener.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def healthy(url: str, *, api: bool) -> bool:
    try:
        with urlopen(url, timeout=2) as response:
            body = response.read().decode("utf-8").strip()
        if api:
            return json.loads(body) == {"status": "ok", "mode": "synthetic"}
        return body == "ok"
    except (URLError, OSError, ValueError):
        return False


def main() -> int:
    artifacts = Path(".artifacts")
    artifacts.mkdir(exist_ok=True)

    services = (
        (
            "streamlit",
            8501,
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                "app.py",
                "--server.address=0.0.0.0",
                "--server.port=8501",
            ],
            "http://127.0.0.1:8501/_stcore/health",
            False,
        ),
        (
            "api",
            8000,
            [
                sys.executable,
                "-m",
                "uvicorn",
                "bond.api:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
            ],
            "http://127.0.0.1:8000/health/live",
            True,
        ),
    )

    for name, port, command, url, api in services:
        if healthy(url, api=api):
            print(name, "already responds to its expected health check.")
            continue
        if not port_available(port):
            print("STOP: Port", port, "is occupied by an unverified process.")
            return 1

        with (artifacts / f"{name}.log").open("ab") as log:
            process = subprocess.Popen(
                command,
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )

        (artifacts / f"{name}.pid").write_text(str(process.pid), encoding="utf-8")
        deadline = time.monotonic() + 35

        while time.monotonic() < deadline:
            if healthy(url, api=api):
                print(name, "health check: PASSED on port", port)
                break
            if process.poll() is not None:
                print(name, "stopped before becoming healthy. Inspect its local log.")
                return 1
            time.sleep(0.5)
        else:
            print(name, "did not become healthy within the startup window.")
            return 1

    print("Local processes are running. Codespaces port visibility was not changed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
