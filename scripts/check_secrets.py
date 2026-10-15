"""Small local disclosure guard, not a comprehensive security scanner."""

import os
import re
import subprocess
import sys
from pathlib import Path

PATTERNS = (
    re.compile(r"sb_secret_[A-Za-z0-9_-]{16,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"postgres(?:ql)?://[^\s:/]+:[^\s@]+@"),
)


def main() -> int:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        check=True,
        capture_output=True,
    )
    password = os.environ.get("BOND_DB_PASSWORD", "")
    findings: list[str] = []
    checked = 0

    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        path = Path(os.fsdecode(raw))
        if not path.is_file():
            continue
        content = path.read_bytes()
        if b"\0" in content:
            continue
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            continue

        checked += 1
        if any(pattern.search(text) for pattern in PATTERNS):
            findings.append(str(path))
        elif len(password) >= 8 and password in text:
            findings.append(str(path))

    if findings:
        print("LOCAL DISCLOSURE GUARD FAILED")
        for name in sorted(set(findings)):
            print("Inspect privately:", name)
        print("Matched values were not printed.")
        return 1

    print("Local disclosure guard passed. Text files checked:", checked)
    print("This is not a comprehensive secret or vulnerability audit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
