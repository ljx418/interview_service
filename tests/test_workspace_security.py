from pathlib import Path

import pytest

from services.storage.workspace import init_workspace, safe_child


def test_safe_child_blocks_workspace_escape(tmp_path):
    workspace = init_workspace("safe", str(tmp_path / "workspace"))
    root = Path(workspace["root_path"])
    with pytest.raises(ValueError):
        safe_child(root, "../outside.txt")

