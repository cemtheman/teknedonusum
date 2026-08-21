from pathlib import Path


UI = Path("ui/grant_program.py").read_text(encoding="utf-8")


def test_grant_ui_describes_strict_priority_semantics():
  assert "daha düşük öncelik seviyesine geçilmez" in UI
