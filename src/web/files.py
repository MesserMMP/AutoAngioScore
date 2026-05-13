import os
from typing import List

import pydicom


def is_dicom_path(path: str) -> bool:
    """Проверка, что путь указывает на корректный DICOM файл."""
    if not os.path.exists(path):
        return False
    ext = os.path.splitext(path)[1].lower()
    if ext not in {".dcm", ""}:
        return False
    try:
        pydicom.dcmread(path, stop_before_pixels=True)
        return True
    except Exception:
        return False


def files_to_paths(files) -> List[str]:
    """Конвертация входных файлов Gradio в список путей."""
    if not files:
        return []
    raw_paths = [f.name for f in files if hasattr(f, "name") and os.path.exists(f.name)]
    return [path for path in raw_paths if is_dicom_path(path)]


def collect_input_paths(files_all, folder_files) -> List[str]:
    """Сбор всех путей из загрузок без дублей."""
    combined = files_to_paths(files_all) + files_to_paths(folder_files)
    return list(dict.fromkeys(combined))
