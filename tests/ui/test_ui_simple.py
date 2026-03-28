import pytest

from ui.widgets.theme import BG_DARK, COLOR_ALERT, BTN_START
from ui.widgets.modern_button import ModernButton


def test_theme_constants():
    assert BG_DARK.startswith("#")
    assert COLOR_ALERT == "#ff3333"
    assert BTN_START == "#0e639c"


def test_modern_button_lighten_color(tmp_path, monkeypatch, tk_root):
    root = tk_root

    called = {"click": False}
    def on_click():
        called["click"] = True

    btn = ModernButton(root, "Test", "#112233", on_click)
    # on click
    btn._on_click(None)
    assert called["click"]

    # hover and leave toggles background
    btn._on_hover(None)
    assert btn.cget("bg") != "#112233"
    btn._on_leave(None)
    assert btn.cget("bg") == "#112233"
