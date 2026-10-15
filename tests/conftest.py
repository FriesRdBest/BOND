"""Initialize real component discovery in the affected AppTest harness.

Streamlit issue 15484 documents missing packaged component discovery
in AppTest. This fixture initializes the actual manager rather than
mocking component registration, assets, rendering, or messages.
"""

from collections.abc import Iterator

import pytest
from streamlit.components.v2.component_manager import BidiComponentManager
from streamlit.testing.v1 import app_test

APPTEST_MODULES = {
    "test_interface.py",
    "test_query_navigation.py",
    "test_console_refinements.py",
}


@pytest.fixture(autouse=True)
def initialize_apptest_component_discovery(
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[None]:
    if request.node.path.name in APPTEST_MODULES:

        def discovered_manager() -> BidiComponentManager:
            manager = BidiComponentManager()
            manager.discover_and_register_components(
                start_file_watching=False,
            )
            return manager

        monkeypatch.setattr(
            app_test,
            "BidiComponentManager",
            discovered_manager,
        )

    yield
