"""Shared visual tokens for the PВК desktop interface."""

LIGHT = {
    "name": "light",
    "window": "#e9ecef",
    "surface": "#f5f6f7",
    "surface_alt": "#e1e5e8",
    "canvas": "#f7f8f9",
    "text": "#252a2d",
    "muted": "#687078",
    "border": "#b8bec3",
    "divider": "#c9ced2",
    "grid": "#d9dee1",
    "accent": "#1976b9",
    "accent_soft": "#d6e9f6",
    "accent_text": "#ffffff",
    "danger": "#dc2626",
    "selection": "#2563eb",
}

DARK = {
    "name": "dark",
    "window": "#242829",
    "surface": "#34393b",
    "surface_alt": "#454b4d",
    "canvas": "#1d2122",
    "text": "#e7eaeb",
    "muted": "#aeb5b8",
    "border": "#5b6265",
    "divider": "#454b4d",
    "grid": "#303739",
    "accent": "#3b9ee5",
    "accent_soft": "#1d5278",
    "accent_text": "#ffffff",
    "danger": "#ff7676",
    "selection": "#3b9ee5",
}


def palette(name):
    return DARK if name == "dark" else LIGHT
