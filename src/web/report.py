import json
import tempfile
from datetime import datetime
from typing import Any, Dict


def build_report_file(result: Dict[str, Any]) -> str:
    """Создание отчета в JSON."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    with tempfile.NamedTemporaryFile(
        mode="w",
        prefix=f"autoangioscore_report_{ts}_",
        suffix=".json",
        encoding="utf-8",
        delete=False,
    ) as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        return handle.name
