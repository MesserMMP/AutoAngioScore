import base64
import os

DEFAULT_LOGO = "assets/logo.png"
LOGO_PATH = os.environ.get("LOGO_PATH", DEFAULT_LOGO)


def logo_html() -> str:
    """Генерация HTML для логотипа."""
    path = LOGO_PATH
    if not path or not os.path.exists(path):
        return ""
    try:
        with open(path, "rb") as handle:
            data = base64.b64encode(handle.read()).decode("ascii")
        ext = os.path.splitext(path)[1].lower()
        mime = "image/png" if ext in {".png", ""} else "image/jpeg"
        return (
            f'<img src="data:{mime};base64,{data}" alt="Логотип" '
            "style=\"height: 36px; width: auto; border-radius: 10px; "
            "filter: drop-shadow(0 2px 6px rgba(0,0,0,0.08));\" />"
        )
    except Exception:
        return ""
