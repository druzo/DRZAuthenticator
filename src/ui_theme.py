"""UI theme, animated banner, and arrow-key navigation for DRZAuthenticator."""

import os
import time
import threading
from typing import List, Optional, Tuple

from rich.align import Align
from rich.box import ROUNDED
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

import readchar

# Pastel palette on dark background
PALETTE = {
    "bg":          "#1E1E2E",
    "panel":       "#2A2A3C",
    "panel_dim":   "#232333",
    "border":      "#B4A7D6",  # lavender
    "lavender":    "#B4A7D6",
    "mint":        "#A8D8B9",
    "peach":       "#F5C6A5",
    "rose":        "#F4ACB7",
    "sky":         "#9BD1E5",
    "gold":        "#E8D895",
    "text_dim":    "#8A8AA0",
}

PASTEL_CYCLE = [
    PALETTE["lavender"],
    PALETTE["sky"],
    PALETTE["mint"],
    PALETTE["gold"],
    PALETTE["peach"],
    PALETTE["rose"],
]

# Build Rich theme mapping style-name -> color
THEME = Theme({
    "title":        f"bold {PALETTE['lavender']}",
    "subtitle":     f"italic {PALETTE['sky']}",
    "border":       PALETTE["border"],
    "panel_bg":     f"on {PALETTE['panel']}",
    "menu_item":    PALETTE["mint"],
    "menu_sel":     f"bold {PALETTE['peach']}",
    "menu_cursor":  f"bold {PALETTE['rose']}",
    "menu_dim":     PALETTE["text_dim"],
    "label":        PALETTE["lavender"],
    "value":        PALETTE["sky"],
    "ok":           f"bold {PALETTE['mint']}",
    "warn":         f"bold {PALETTE['gold']}",
    "err":          f"bold {PALETTE['rose']}",
    "hint":         f"italic {PALETTE['text_dim']}",
})

# ASCII-art "DRZ AUTHENTICATOR" — small variant (narrow terminals)
BANNER_ART_SMALL = [
    " ____  ____  _____",
    "|  _ \\/  _ \\| ____|",
    "| | | | | | |  _|  ",
    "| |_| | |_| | |___ ",
    "|____/|____/|_____|",
    "",
    "    _   _     ___ _   _ _____    ____ _   _ ___ _____ ____  ",
    "   / \\ | | | | _| \\ | |_   _|  / ___| | | / __|_   _/ ___| ",
    "  / _ \\| | | || ||  \\| | | |   | |   | |/ / /_  | | \\___ \\  ",
    " / ___ \\ |_| || || |\\  | | |   | |___|   / / /  | |  ___) | ",
    "/_/   \\_\\___/|___|_| \\_| |_|    \\____|_|_\\/_/   |_| |____/  ",
]

# ASCII-art "DRZ AUTHENTICATOR" — big block variant (wide terminals, ~130 cols)
BANNER_ART_BIG = [
    r"▀\▀\▀\   ▀\▀\▀\▀\ ▀\▀\▀\▀\      ▀\▀\▀\▀\ ▀\    ▀\ ▀\▀\▀\▀\ ▀\    ▀\ ▀\▀\▀\▀\ ▀\▀\  ▀\ ▀\▀\▀\▀\ ▀\ ▀\▀\▀\▀\ ▀\▀\▀\▀\ ▀\▀\▀\▀\ ▀\▀\▀\▀\ ▀\▀\▀" "\\",
    r"▀\    ▀\ ▀\    ▀\       ▀\      ▀\    ▀\ ▀\    ▀\    ▀\    ▀\    ▀\ ▀\       ▀\ ▀\ ▀\    ▀\    ▀\ ▀\       ▀\    ▀\    ▀\    ▀\    ▀\ ▀\    ▀" "\\",
    r"▀\    ▀\ ▀\▀\▀\▀\     ▀\        ▀ ▀\▀\▀\ ▀\    ▀\    ▀\    ▀\▀\▀\▀\ ▀\▀\▀\   ▀\ ▀\ ▀\    ▀\    ▀\ ▀\       ▀ ▀\▀\▀\    ▀\    ▀\    ▀\ ▀\▀\▀" "\\",
    r"▀\    ▀\ ▀\  ▀\      ▀\         ▀\    ▀\ ▀\    ▀\    ▀\    ▀\    ▀\ ▀\       ▀\ ▀\ ▀\    ▀\    ▀\ ▀\       ▀\    ▀\    ▀\    ▀\    ▀\ ▀\  ▀\  ",
    r"▀\    ▀\ ▀\   ▀\   ▀\           ▀\    ▀\ ▀\    ▀\    ▀\    ▀\    ▀\ ▀\       ▀\ ▀\ ▀\    ▀\    ▀  ▀\       ▀\    ▀\    ▀\    ▀\    ▀\ ▀\   ▀\ ",
    r"▀\▀\▀\▀\ ▀\    ▀\ ▀\▀\▀\▀\      ▀\    ▀\ ▀\▀\▀\▀\    ▀\    ▀\    ▀\ ▀\▀\▀\▀\ ▀\  ▀\▀\    ▀\    ▀\ ▀\▀\▀\▀\ ▀\    ▀\    ▀\    ▀\▀\▀\▀\ ▀\    ▀\ ",
]

# Minimum console width needed to render the big banner without wrapping
BANNER_BIG_MIN_WIDTH = 135


def _gradient_color(pos: float, phase: float) -> str:
    """Return a hex color for position `pos` (0..1) shifted by `phase` (0..1)."""
    n = len(PASTEL_CYCLE)
    # continuous index into palette (wraps)
    idx = (pos * n + phase * n) % n
    i0 = int(idx) % n
    i1 = (i0 + 1) % n
    frac = idx - int(idx)
    return _lerp_hex(PASTEL_CYCLE[i0], PASTEL_CYCLE[i1], frac)


def _lerp_hex(c1: str, c2: str, t: float) -> str:
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02X}{g:02X}{b:02X}"


def render_banner(phase: float = 0.0, width: Optional[int] = None) -> Text:
    """Render the DRZ AUTHENTICATOR banner with a sweeping pastel gradient.

    `phase` shifts the gradient horizontally to animate. Returns a Rich Text.
    `width`: console width; picks big block art when wide enough, else small.
    """
    if width is None:
        width = Console().size.width
    art = BANNER_ART_BIG if width >= BANNER_BIG_MIN_WIDTH else BANNER_ART_SMALL
    text = Text()
    max_len = max(len(line) for line in art)
    for row_i, line in enumerate(art):
        for col_i, ch in enumerate(line):
            if ch == " ":
                text.append(" ")
                continue
            pos = (col_i / max_len + row_i * 0.04) % 1.0
            color = _gradient_color(pos, phase)
            text.append(ch, style=f"bold {color}")
        if row_i != len(art) - 1:
            text.append("\n")
    return text


def render_banner_panel(phase: float = 0.0, width: Optional[int] = None) -> Panel:
    """Wrap the animated banner in a styled panel."""
    banner = render_banner(phase, width=width)
    return Panel(
        Align.center(banner, vertical="middle"),
        border_style=PALETTE["border"],
        box=ROUNDED,
        padding=(0, 2),
        expand=False,
        style=f"on {PALETTE['panel']}",
        width=width,
    )


def _render_menu_items(
    items: List[Tuple[str, str]],
    selected: int,
    nav_hint: str,
) -> Table:
    """Render the menu list as a table with a cursor on the selected row."""
    table = Table(show_header=False, box=None, padding=(0, 2), expand=False)
    table.add_column("cursor", style=PALETTE["rose"], width=2)
    table.add_column("idx", style=PALETTE["text_dim"], width=4)
    table.add_column("label", style=PALETTE["mint"], min_width=20)
    for i, (_key, label) in enumerate(items):
        cursor = "❯" if i == selected else " "
        idx_text = f"{i + 1:>2}"
        # highlighted row uses selected style
        if i == selected:
            label_text = Text(label, style=f"bold {PALETTE['peach']}")
            cursor_text = Text(cursor, style=f"bold {PALETTE['rose']}")
            idx_text_obj = Text(idx_text, style=f"bold {PALETTE['peach']}")
        else:
            label_text = Text(label, style=PALETTE["mint"])
            cursor_text = Text(cursor, style=PALETTE["text_dim"])
            idx_text_obj = Text(idx_text, style=PALETTE["text_dim"])
        table.add_row(cursor_text, idx_text_obj, label_text)
    # hint row
    table.add_row("", "", Text(nav_hint, style=f"italic {PALETTE['text_dim']}"))
    return table


def _composite_frame(
    items: List[Tuple[str, str]],
    selected: int,
    nav_hint: str,
    title: str,
    phase: float,
) -> Group:
    """Build one full frame: animated banner + menu panel."""
    banner = render_banner_panel(phase)
    menu_table = _render_menu_items(items, selected, nav_hint)
    menu_panel = Panel(
        Align.center(menu_table, vertical="middle"),
        title=f"[title]{title}[/title]",
        title_align="center",
        border_style=PALETTE["border"],
        box=ROUNDED,
        padding=(1, 2),
        expand=False,
        style=f"on {PALETTE['panel']}",
    )
    return Group(Align.center(banner), Align.center(menu_panel))


def arrow_menu(
    console: Console,
    title: str,
    items: List[Tuple[str, str]],
    nav_hint: str = "",
    selected: int = 0,
    fps: float = 12.0,
) -> int:
    """Render an animated banner + arrow-key menu. Returns chosen index.

    `items`: list of (key, label). Returns index of chosen item, or -1 for back/quit.
    Keys: ↑/↓ navigate, Enter select, q/Esc/← back (returns -1).
    """
    if not items:
        return -1
    selected = max(0, min(selected, len(items) - 1))
    period = 1.0 / fps
    phase = 0.0

    # Disable cursor blink for cleanliness
    try:
        console.show_cursor(False)
    except Exception:
        pass

    try:
        with Live(
            _composite_frame(items, selected, nav_hint, title, phase),
            console=console,
            refresh_per_second=fps,
            transient=True,
            screen=False,
        ) as live:
            while True:
                # animate phase
                phase = (phase + period * 0.25) % 1.0
                live.update(_composite_frame(items, selected, nav_hint, title, phase))

                # poll key — readchar blocks until a key is pressed.
                key = readchar.readkey()

                if key in (readchar.key.UP, "k"):
                    selected = (selected - 1) % len(items)
                elif key in (readchar.key.DOWN, "j"):
                    selected = (selected + 1) % len(items)
                elif key in (readchar.key.ENTER, readchar.key.RIGHT, "l"):
                    return selected
                elif key in ("q", "Q", readchar.key.ESC, readchar.key.LEFT, "h"):
                    return -1
                elif key in ("0",):
                    # zero = exit option convenience
                    for i, (k, _lbl) in enumerate(items):
                        if k == "0":
                            return i
    finally:
        try:
            console.show_cursor(True)
        except Exception:
            pass


def make_console() -> Console:
    """Build a Console configured with the DRZ pastel-dark theme."""
    return Console(theme=THEME, force_terminal=True)


def styled_panel(content, title: Optional[str] = None) -> Panel:
    """Wrap content in the standard pastel-dark panel."""
    return Panel(
        content,
        title=None if title is None else f"[title]{title}[/title]",
        title_align="center",
        border_style=PALETTE["border"],
        box=ROUNDED,
        padding=(1, 2),
        expand=False,
        style=f"on {PALETTE['panel']}",
    )
