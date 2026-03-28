import pytest

from ui.alerts_view import AlertsView


def test_alerts_view_add_and_clear(tmp_path, tk_root):
    root = tk_root

    view = AlertsView(root)
    view.add_alert("Test alert")
    view.add_info("Test info")

    # au moins du texte doit être écrit
    assert "Test alert" in view.alerts_text.get("1.0", "end")
    assert "Test info" in view.info_text.get("1.0", "end")

    view.clear()
    assert view.alerts_text.get("1.0", "end").strip() == ""
    assert view.info_text.get("1.0", "end").strip() == ""

    file_alerts = tmp_path / "alerts.txt"
    file_info = tmp_path / "info.txt"

    view.add_alert("X")
    view.add_info("Y")
    view.export_alerts(str(file_alerts))
    view.export_info(str(file_info))

    assert file_alerts.exists()
    assert file_info.exists()
