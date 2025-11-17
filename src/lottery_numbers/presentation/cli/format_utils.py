from datetime import date


def format_date(d: date) -> str:
    """Format the date for humans."""
    return d.strftime("%A, %d %B %Y")


def center_text(text: str, width: int = 79) -> str:
    """Center a text within a given width."""
    padding: int = max(0, (width - len(text)) // 2)
    return " " * padding + text
