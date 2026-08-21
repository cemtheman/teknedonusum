from pathlib import Path


SOURCE = Path("ui/inputs.py").read_text(encoding="utf-8")


def test_sidebar_copy_matches_collapsed_default_state():
  assert "Tüm girdi grupları düzenli bir görünüm için kapalı başlar." in SOURCE
  assert "Sık kullanılan gruplar açık" not in SOURCE


def test_market_fallback_is_labeled_as_backup_value():
  assert "🟡 Yedek değer" in SOURCE
  assert "Canlı kaynağa erişilemezse tanımlı yedek değer kullanılır." in SOURCE
