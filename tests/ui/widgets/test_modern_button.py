import pytest
from unittest.mock import MagicMock

from ui.widgets.modern_button import ModernButton


def test_modern_button_click_hover_leave(tmp_path, monkeypatch, tk_root):
    root = tk_root

    clicked = {"value": False}

    def on_click():
        clicked["value"] = True

    btn = ModernButton(root, "Test", "#112233", on_click)

    btn._on_click(None)
    assert clicked["value"] is True

    before = btn.cget("bg")
    btn._on_hover(None)
    assert btn.cget("bg") != before

    btn._on_leave(None)
    assert btn.cget("bg") == before
