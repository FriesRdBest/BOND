"""Verify packaged assets, registration metadata, and source provenance."""

import hashlib
import json
import sys
import tomllib
import zipfile
from pathlib import Path


def main() -> int:
    repository = Path(__file__).resolve().parents[1]
    wheels = sorted((repository / "dist").glob("bond-*.whl"))

    if len(wheels) != 1:
        print("PACKAGE CHECK BLOCKED: Expected exactly one current BOND wheel.")
        return 1

    prefix = "bond/data/web/evidence/"
    required = {"evidence.js", "evidence.css", "build_manifest.json"}

    with zipfile.ZipFile(wheels[0]) as archive:
        names = set(archive.namelist())

        if not all(prefix + name in names for name in required):
            print("PACKAGE CHECK FAILED: Required component asset missing.")
            return 1

        metadata = tomllib.loads(archive.read("bond/pyproject.toml").decode("utf-8"))
        expected = [
            {
                "name": "evidence_explorer",
                "asset_dir": "data/web/evidence",
            }
        ]

        if metadata["project"]["name"] != "bond":
            print("PACKAGE CHECK FAILED: Distribution identity mismatch.")
            return 1

        if metadata["tool"]["streamlit"]["component"]["components"] != expected:
            print("PACKAGE CHECK FAILED: Component declaration mismatch.")
            return 1

        manifest = json.loads(archive.read(prefix + "build_manifest.json"))

        for name, expected_hash in manifest["outputs"].items():
            relative = Path(name)
            if relative.is_absolute() or ".." in relative.parts:
                print("PACKAGE CHECK FAILED: Unsafe manifest output path.")
                return 1

            actual = hashlib.sha256(archive.read(prefix + name)).hexdigest()
            if actual != expected_hash:
                print("PACKAGE CHECK FAILED: Output checksum mismatch.")
                return 1

        for name, expected_hash in manifest["sources"].items():
            source = (repository / name).resolve()
            if not source.is_relative_to(repository) or not source.is_file():
                print("PACKAGE CHECK FAILED: Source provenance path is invalid.")
                return 1

            actual = hashlib.sha256(source.read_bytes()).hexdigest()
            if actual != expected_hash:
                print("PACKAGE CHECK FAILED: Sources changed after component build.")
                return 1

    print("Wheel component assets: VERIFIED")
    print("Registration metadata: VERIFIED")
    print("Output checksums and current source provenance: VERIFIED")
    print("This does not replace browser or hosted acceptance.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
