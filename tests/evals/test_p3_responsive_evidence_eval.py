import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/reports/evidence"


def _png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as image:
        header = image.read(24)
    assert header[:8] == b"\x89PNG\r\n\x1a\n"
    return struct.unpack(">II", header[16:24])


def test_p3_responsive_screenshots_exist_with_expected_widths():
    expected = {
        "p3_chatbox_initial_1280.png": 1280,
        "p3_chatbox_error_state_1280.png": 1280,
        "p3_chatbox_response_1280.png": 1280,
        "p3_chatbox_narrow_720.png": 720,
        "p3_chatbox_mobile_390.png": 390,
    }

    for file_name, expected_width in expected.items():
        path = EVIDENCE / file_name
        assert path.exists(), f"Missing screenshot evidence: {path}"
        width, height = _png_size(path)
        assert width == expected_width
        assert height >= 800
        assert path.stat().st_size > 50_000
