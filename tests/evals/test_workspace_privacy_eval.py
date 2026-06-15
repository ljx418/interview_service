from pathlib import Path

import pytest

from services.storage.workspace import init_workspace, safe_child


def test_workspace_privacy_rejects_path_traversal(tmp_path):
    workspace = init_workspace("privacy-eval", str(tmp_path / "workspace"))
    root = Path(workspace["root_path"])

    with pytest.raises(ValueError):
        safe_child(root, "../../private.txt")
