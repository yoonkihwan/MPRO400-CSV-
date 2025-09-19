LINE_STYLE_MAP = {
    "solid": "-",
    "dash": "--",
    "dot": ":",
}


def to_matplotlib(style: str) -> str:
    return LINE_STYLE_MAP.get(style, "-")


__all__ = ["to_matplotlib", "LINE_STYLE_MAP"]
