"""Verify actual installed component discovery, not just manifest syntax."""

from pathlib import Path

from streamlit.components.v2.manifest_scanner import scan_component_manifests


def test_installed_streamlit_discovers_bond_assets() -> None:
    matches = [
        (manifest, root) for manifest, root in scan_component_manifests() if manifest.name == "bond"
    ]

    assert len(matches) == 1, (
        "The installed Streamlit scanner must discover exactly one BOND manifest."
    )

    manifest, root = matches[0]
    components = [
        component for component in manifest.components if component.name == "evidence_explorer"
    ]

    assert len(components) == 1
    component = components[0]
    assert component.asset_dir == "data/web/evidence"

    asset_root = component.resolve_asset_root(Path(root))
    assert asset_root is not None
    assert (asset_root / "evidence.js").is_file()
    assert (asset_root / "evidence.css").is_file()
