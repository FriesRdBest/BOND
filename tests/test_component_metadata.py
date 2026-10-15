"""Packaged component metadata must match the declared public asset directory."""

import tomllib
from importlib.resources import files


def test_component_metadata_declares_the_asset_directory() -> None:
    package = files("bond")
    metadata = tomllib.loads(package.joinpath("pyproject.toml").read_text(encoding="utf-8"))
    assert metadata["project"]["name"] == "bond"

    declarations = metadata["tool"]["streamlit"]["component"]["components"]
    assert declarations == [
        {
            "name": "evidence_explorer",
            "asset_dir": "data/web/evidence",
        }
    ]

    assets = package.joinpath("data", "web", "evidence")
    assert assets.joinpath("evidence.js").is_file()
    assert assets.joinpath("evidence.css").is_file()
