"""Shared visual tokens for the PВК desktop interface."""

LIGHT = {
    "name": "light",
    "window": "#e7e7e7",
    "surface": "#F2F2F2",
    "surface_alt": "#e4e4e4",
    "canvas": "#FFFFFF",
    "text": "#1e1e1e",
    "symbol": "#111111",
    "muted": "#686868",
    "border": "#c8c8c8",
    "divider": "#d5d5d5",
    "grid": "#e4e4e4",
    "accent": "#5780B2",
    "accent_soft": "#dce7f4",
    "accent_text": "#ffffff",
    "danger": "#dc2626",
    "selection": "#5780B2",
}

DARK = {
    "name": "dark",
    "window": "#454545",
    "surface": "#5C5C5C",
    "surface_alt": "#696969",
    "canvas": "#2A2A2A",
    "text": "#f2f2f2",
    "symbol": "#f4f4f4",
    "muted": "#d0d0d0",
    "border": "#555555",
    "divider": "#4b4b4b",
    "grid": "#3b3b3b",
    "accent": "#77B0F5",
    "accent_soft": "#355878",
    "accent_text": "#ffffff",
    "danger": "#ff7676",
    "selection": "#77B0F5",
}


def palette(name):
    return DARK if name == "dark" else LIGHT
