#! /usr/bin/env python3

# Standard libraries
# import logging
# import sys
# import os


"""ANSI color formatting for output in terminal."""

import os
import sys
from typing import Iterable, Union


ATTRIBUTES = {
    "bold":      1,
    "dark":      2,
    "underline": 4,
    "blink":     5,
    "reverse":   7,
    "concealed": 8,
}

HIGHLIGHTS = {
    "on_black":          40,
    "on_grey":           40,  # Actually black but kept for backwards compatibility
    "on_red":            41,
    "on_green":          42,
    "on_yellow":         43,
    "on_blue":           44,
    "on_magenta":        45,
    "on_cyan":           46,
    "on_light_grey":     47,
    "on_dark_grey":     100,
    "on_light_red":     101,
    "on_light_green":   102,
    "on_light_yellow":  103,
    "on_light_blue":    104,
    "on_light_magenta": 105,
    "on_light_cyan":    106,
    "on_white":         107,
}

COLORS = {
    "black":         30,
    "grey":          30,  # Actually black but kept for backwards compatibility
    "red":           31,
    "green":         32,
    "yellow":        33,
    "blue":          34,
    "magenta":       35,
    "cyan":          36,
    "light_grey":    37,
    "dark_grey":     90,
    "light_red":     91,
    "light_green":   92,
    "light_yellow":  93,
    "light_blue":    94,
    "light_magenta": 95,
    "light_cyan":    96,
    "white":         97,
}

RESET = "\033[0m"


def _can_do_colour() -> bool:
    """Check env vars and for tty/dumb terminal"""
    if "ANSI_COLORS_DISABLED" in os.environ:
        return False
    if "NO_COLOR" in os.environ:
        return False
    if "FORCE_COLOR" in os.environ:
        return True
    return (
        hasattr(sys.stdout, "isatty")
        and sys.stdout.isatty()
        and os.environ.get("TERM") != "dumb"
    )


def colored(
    text: str,
    color: Union[str, None] = None,
    on_color: Union[str, None] = None,
    attrs: Union[Iterable[str], None] = None,
) -> str:
    if not _can_do_colour():
        return text

    fmt_str = "\033[%dm%s"

    if color is not None:
        text = fmt_str % (COLORS[color], text)

    if on_color is not None:
        text = fmt_str % (HIGHLIGHTS[on_color], text)

    if attrs is not None:
        for attr in attrs:
            text = fmt_str % (ATTRIBUTES[attr], text)

    return text + RESET
