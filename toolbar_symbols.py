"""Compact vector UGO previews for the scheme ribbon.

The drawings use only Canvas primitives.  There are no bitmap assets or filled
tile backgrounds, so a symbol stays sharp and follows the current UI palette.
"""

from ugo_model import PLAN_TOOL_NAMES, SCHEME_TOOL_NAMES

TILE = 30
STROKE = 1.6

SCHEME_SYMBOLS = frozenset(SCHEME_TOOL_NAMES)
PLAN_SYMBOLS = frozenset(PLAN_TOOL_NAMES)


def supports_toolbar_symbol(name):
    return name in SCHEME_SYMBOLS


def supports_plan_toolbar_symbol(name):
    return name in PLAN_SYMBOLS


def _line(canvas, points, color, tag, width=STROKE, dash=()):
    return canvas.create_line(
        *points, fill=color, width=width, dash=dash,
        capstyle="round", joinstyle="round", tags=tag,
    )


def _oval(canvas, box, color, tag, width=STROKE):
    return canvas.create_oval(*box, outline=color, fill="", width=width, tags=tag)


def _rect(canvas, box, color, tag, width=STROKE):
    return canvas.create_rectangle(*box, outline=color, fill="", width=width, tags=tag)


def _poly(canvas, points, color, tag, width=STROKE, fill=""):
    return canvas.create_polygon(*points, outline=color, fill=fill, width=width, tags=tag)


def _dot(canvas, x, y, color, tag, radius=1.6):
    return canvas.create_oval(
        x - radius, y - radius, x + radius, y + radius,
        outline=color, fill=color, width=0, tags=tag,
    )


def _text(canvas, x, y, text, color, tag, size=7):
    return canvas.create_text(
        x, y, text=text, fill=color, font=("Segoe UI", size, "bold"), tags=tag,
    )


def _contact(canvas, y, color, tag):
    _line(canvas, (4, y, 10, y), color, tag)
    _line(canvas, (10, y, 18, y - 4), color, tag)
    _line(canvas, (18, y, 25, y), color, tag)


def _automatic_breaker(canvas, poles, color, tag, sectional=False, rcd=False, diff=False):
    positions = {1: (14,), 2: (10, 18), 3: (7, 14, 21), 4: (5, 11, 17, 23)}[poles]
    for y in positions:
        _contact(canvas, y, color, tag)
    if poles > 1:
        _line(canvas, (9, positions[0], 9, positions[-1]), color, tag, width=1)
    if sectional:
        _line(canvas, (14.5, 3, 14.5, 26), color, tag, width=1, dash=(2, 2))
    if rcd:
        _oval(canvas, (19, 3, 25, 9), color, tag, width=1.2)
    if diff:
        _poly(canvas, (21, 4, 25, 8, 17, 8), color, tag, width=1.1)


def _transformer_2w(canvas, color, tag):
    _line(canvas, (3, 14, 6, 14), color, tag)
    _oval(canvas, (6, 8, 16, 20), color, tag)
    _oval(canvas, (14, 8, 24, 20), color, tag)
    _line(canvas, (24, 14, 27, 14), color, tag)


def _transformer_split(canvas, color, tag):
    _line(canvas, (14, 2, 14, 5), color, tag)
    _oval(canvas, (9, 4, 19, 14), color, tag)
    _oval(canvas, (4, 13, 14, 23), color, tag)
    _oval(canvas, (14, 13, 24, 23), color, tag)
    _line(canvas, (14, 15, 7, 24), color, tag, width=1.1)
    _line(canvas, (14, 15, 21, 24), color, tag, width=1.1)
    _line(canvas, (7, 22, 7, 27), color, tag)
    _line(canvas, (21, 22, 21, 27), color, tag)


def _transformer_3w(canvas, color, tag):
    _line(canvas, (14, 2, 14, 5), color, tag)
    _oval(canvas, (9, 4, 19, 14), color, tag)
    _oval(canvas, (4, 13, 14, 23), color, tag)
    _oval(canvas, (14, 13, 24, 23), color, tag)
    _line(canvas, (7, 22, 7, 27), color, tag)
    _line(canvas, (24, 18, 28, 18), color, tag)


def _cable(canvas, color, tag):
    _line(canvas, (4, 14, 25, 14), color, tag)
    _poly(canvas, (6, 11, 6, 17, 10, 14), color, tag, width=1.2)
    _poly(canvas, (23, 11, 23, 17, 19, 14), color, tag, width=1.2)


def _bus(canvas, color, tag, kind):
    if kind == "section":
        _line(canvas, (3, 11, 26, 11), color, tag, width=3.0)
        for x in (8, 14, 20):
            _line(canvas, (x, 11, x, 20), color, tag, width=1.4)
            _dot(canvas, x, 20, color, tag, radius=1.5)
    elif kind == "phase":
        for y in (8, 14, 20):
            _line(canvas, (4, y, 25, y), color, tag, width=1.4)
    elif kind == "neutral":
        _line(canvas, (3, 14, 26, 14), color, tag, width=STROKE)
        _oval(canvas, (11, 10.5, 18, 17.5), color, tag, width=1.1)
    elif kind == "pe":
        _line(canvas, (3, 8, 26, 8), color, tag, width=2.1)
        _line(canvas, (14.5, 8, 14.5, 14), color, tag, width=1.2)
        _line(canvas, (9, 14, 20, 14), color, tag, width=1.4)
        _line(canvas, (11, 17, 18, 17), color, tag, width=1.3)
        _line(canvas, (13, 20, 16, 20), color, tag, width=1.2)
    elif kind == "pen":
        _line(canvas, (3, 9, 26, 9), color, tag, width=2.1)
        _line(canvas, (3, 18, 26, 18), color, tag, width=1.3, dash=(3, 2))
        _line(canvas, (14.5, 9, 14.5, 18), color, tag, width=1)
        _line(canvas, (10.5, 22, 18.5, 22), color, tag, width=1.2)


def _load(canvas, color, tag, low_voltage=False):
    if low_voltage:
        _line(canvas, (4, 14, 20, 14), color, tag)
        _poly(canvas, (25, 14, 19, 10, 19, 18), color, tag, width=1.1, fill=color)
        return
    _line(canvas, (14, 3, 14, 21), color, tag)
    _poly(canvas, (14, 26, 9, 20, 19, 20), color, tag, width=1.1, fill=color)


def _panel(canvas, color, tag, kind):
    _rect(canvas, (5, 5, 24, 23), color, tag)
    if kind == "ГРЩ":
        for x in (10, 14.5, 19):
            _line(canvas, (x, 8, x, 20), color, tag, width=1)
    elif kind == "ЩСУ":
        _oval(canvas, (9, 8, 20, 19), color, tag, width=1.2)
        _line(canvas, (14.5, 8, 14.5, 19), color, tag, width=1)
        _line(canvas, (9, 13.5, 20, 13.5), color, tag, width=1)
    elif kind == "ЩО":
        _oval(canvas, (10, 9, 19, 18), color, tag, width=1.2)
        for x1, y1, x2, y2 in ((14.5, 6, 14.5, 8), (14.5, 19, 14.5, 21), (7, 13.5, 9, 13.5), (20, 13.5, 22, 13.5)):
            _line(canvas, (x1, y1, x2, y2), color, tag, width=1)
    else:  # ШР
        for y in (9, 14, 19):
            _line(canvas, (8, y, 21, y), color, tag, width=1.2)


def _factory(canvas, color, tag, *, chimney=True, generator=False, heat=False):
    _line(canvas, (4, 24, 4, 13, 9, 13, 9, 9, 14, 13, 19, 8, 24, 13, 24, 24, 4, 24), color, tag)
    if chimney:
        _rect(canvas, (6, 5, 9, 13), color, tag, width=1.2)
    if generator:
        _oval(canvas, (14, 15, 21, 22), color, tag, width=1.2)
        _text(canvas, 17.5, 18.5, "G", color, tag, size=5)
    if heat:
        _line(canvas, (18, 6, 20, 4, 22, 6, 20, 8), color, tag, width=1)


def _pylon(canvas, color, tag, *, substation=False):
    _line(canvas, (14, 3, 5, 25, 24, 25, 14, 3), color, tag)
    _line(canvas, (8, 16, 21, 16), color, tag, width=1.2)
    _line(canvas, (10, 11, 19, 11), color, tag, width=1.2)
    _line(canvas, (6, 25, 22, 25), color, tag, width=1.2)
    if substation:
        _line(canvas, (3, 7, 8, 7), color, tag, width=1)
        _line(canvas, (20, 7, 26, 7), color, tag, width=1)


def _power_grid(canvas, color, tag):
    """External grid: a three-level pylon with an incoming line."""
    _line(canvas, (14.5, 3, 6, 25, 23, 25, 14.5, 3), color, tag)
    for y, x1, x2 in ((9, 10, 19), (14, 8, 21), (19, 7, 22)):
        _line(canvas, (x1, y, x2, y), color, tag, width=1.2)
    _line(canvas, (3, 9, 10, 9), color, tag, width=1.2)
    _dot(canvas, 10, 9, color, tag, radius=1.1)
    _dot(canvas, 19, 9, color, tag, radius=1.1)
    _line(canvas, (6, 25, 23, 25), color, tag, width=1.2)


def _external_power_system(canvas, color, tag):
    """Scheme source: incoming three-phase utility supply through a pylon."""
    # Three conductors on the left make the external source distinct from a
    # generator, while the bottom stub keeps its reading as a scheme source.
    for y in (8, 14, 20):
        _line(canvas, (3, y, 9, y), color, tag, width=1.1)
        _dot(canvas, 9, y, color, tag, radius=1.0)
    _line(canvas, (16, 3, 10, 23, 23, 23, 16, 3), color, tag)
    _line(canvas, (12, 9, 21, 9), color, tag, width=1.2)
    _line(canvas, (11, 15, 22, 15), color, tag, width=1.2)
    _line(canvas, (10, 23, 23, 23), color, tag, width=1.2)
    _line(canvas, (16, 23, 16, 27), color, tag, width=1.3)


def _main_substation(canvas, color, tag):
    """GPP: HV bus, transformer and LV distribution bus in one silhouette."""
    # High-voltage incoming bus.
    _line(canvas, (3, 6, 10, 6), color, tag, width=1.3)
    _line(canvas, (7, 3.5, 7, 8.5), color, tag, width=1)
    _dot(canvas, 10, 6, color, tag, radius=1.1)
    # The paired coils identify the step-down transformer.
    _line(canvas, (10, 6, 10, 10), color, tag, width=1.2)
    _oval(canvas, (8, 9, 16, 19), color, tag, width=1.5)
    _oval(canvas, (14, 9, 22, 19), color, tag, width=1.5)
    # Low-voltage outgoing bus, deliberately lower than the HV feed.
    _line(canvas, (20, 19, 20, 23), color, tag, width=1.2)
    _line(canvas, (20, 23, 27, 23), color, tag, width=1.5)
    _line(canvas, (23, 20.5, 23, 25.5), color, tag, width=1)
    _dot(canvas, 20, 23, color, tag, radius=1.1)


def _knife_switch(canvas, color, tag):
    """An open knife contact, intentionally distinct from a circuit breaker."""
    _line(canvas, (3, 21, 8, 21), color, tag)
    _dot(canvas, 8, 21, color, tag, radius=1.5)
    _line(canvas, (8, 21, 18.5, 10.5), color, tag, width=2.0)
    _dot(canvas, 20.5, 10.5, color, tag, radius=1.45)
    _line(canvas, (20.5, 10.5, 27, 10.5), color, tag)
    # Fixed jaw: the visible gap keeps the contact unmistakably open.
    _line(canvas, (20.5, 7.5, 20.5, 10.5), color, tag, width=1.2)
    _line(canvas, (22.8, 8.2, 22.8, 12.8), color, tag, width=1.2)


def _plant_object(canvas, color, tag, name):
    if name == "Завод":
        _factory(canvas, color, tag)
    elif name == "Цех":
        _line(canvas, (4, 24, 4, 12, 9, 8, 13, 12, 17, 8, 24, 12, 24, 24, 4, 24), color, tag)
        _line(canvas, (8, 18, 20, 18), color, tag, width=1)
    elif name == "Компрессорная":
        _line(canvas, (3, 14, 8, 14), color, tag)
        _oval(canvas, (8, 8, 21, 21), color, tag)
        _line(canvas, (14.5, 10, 14.5, 19), color, tag, width=1)
        _line(canvas, (10, 14.5, 19, 14.5), color, tag, width=1)
        _line(canvas, (21, 14, 26, 14), color, tag)
    elif name == "Насосная":
        _line(canvas, (3, 14, 8, 14), color, tag)
        _oval(canvas, (8, 8, 21, 21), color, tag)
        _poly(canvas, (11, 11, 18, 14.5, 11, 18), color, tag, width=1.1)
        _line(canvas, (21, 14, 26, 14), color, tag)
    elif name == "Котельная":
        _rect(canvas, (7, 8, 21, 24), color, tag)
        _oval(canvas, (7, 5, 21, 12), color, tag)
        _line(canvas, (10, 4, 10, 1), color, tag, width=1)
        _line(canvas, (18, 4, 18, 1), color, tag, width=1)
    elif name == "Административный корпус":
        _rect(canvas, (5, 4, 24, 24), color, tag)
        for x in (9, 14.5, 20):
            _line(canvas, (x, 8, x, 20), color, tag, width=1)
        _line(canvas, (5, 13, 24, 13), color, tag, width=1)
    else:
        _poly(canvas, (4, 12, 14.5, 4, 25, 12, 22, 24, 7, 24), color, tag)


def _energy_object(canvas, color, tag, name):
    if name == "Энергосистема":
        _power_grid(canvas, color, tag)
    elif name == "ГПП":
        _main_substation(canvas, color, tag)
    elif name == "ТП":
        _rect(canvas, (4, 5, 25, 24), color, tag)
        _oval(canvas, (8, 9, 16, 19), color, tag, width=1.2)
        _oval(canvas, (14, 9, 22, 19), color, tag, width=1.2)
    elif name == "РП":
        _rect(canvas, (5, 5, 24, 24), color, tag)
        _line(canvas, (9, 10, 20, 10), color, tag, width=1.2)
        _line(canvas, (9, 16, 20, 16), color, tag, width=1.2)
        _line(canvas, (9, 21, 20, 21), color, tag, width=1.2)
    elif name == "Собственная электростанция":
        _factory(canvas, color, tag, generator=True)
    elif name == "Мини-ТЭЦ":
        _factory(canvas, color, tag, heat=True)
    else:  # Системная подстанция
        _line(canvas, (4, 8, 25, 8), color, tag, width=1.3)
        _line(canvas, (4, 20, 25, 20), color, tag, width=1.3)
        for x in (8, 14.5, 21):
            _line(canvas, (x, 8, x, 20), color, tag, width=1.1)
            _dot(canvas, x, 8, color, tag, radius=1.1)
            _dot(canvas, x, 20, color, tag, radius=1.1)


def _plan_link(canvas, color, tag, name):
    if name == "КЛ":
        _cable(canvas, color, tag)
    elif name == "ВЛ":
        _line(canvas, (3, 14, 26, 14), color, tag)
        _line(canvas, (8, 14, 10, 20, 13, 8, 16, 20, 19, 8, 21, 14), color, tag, width=1.3)
    elif name == "Газопровод":
        _line(canvas, (3, 14, 26, 14), color, tag, width=2.2)
        _poly(canvas, (14, 9, 19, 14, 14, 19, 9, 14), color, tag, width=1.2)
    elif name == "Технологическая связь":
        _line(canvas, (3, 14, 26, 14), color, tag, width=1.5, dash=(4, 2))
        _dot(canvas, 8, 14, color, tag, radius=1.2)
        _dot(canvas, 21, 14, color, tag, radius=1.2)
    else:
        _line(canvas, (3, 14, 26, 14), color, tag, width=1.5, dash=(2, 3))


def draw_plan_toolbar_symbol(canvas, name, color, tag="ugo"):
    """Draw a transparent plan-toolbar pictogram and return support status."""
    if name not in PLAN_SYMBOLS:
        return False
    if name in {
        "Завод", "Цех", "Компрессорная", "Насосная", "Котельная",
        "Административный корпус", "Прочий объект",
    }:
        _plant_object(canvas, color, tag, name)
    elif name in {
        "Энергосистема", "ГПП", "ТП", "РП", "Собственная электростанция",
        "Мини-ТЭЦ", "Системная подстанция",
    }:
        _energy_object(canvas, color, tag, name)
    else:
        _plan_link(canvas, color, tag, name)
    return True


def draw_toolbar_symbol(canvas, name, color, tag="ugo"):
    """Draw a compact schematic icon and return whether it is supported."""
    if name not in SCHEME_SYMBOLS:
        return False

    if name == "Внешняя энергосистема":
        _external_power_system(canvas, color, tag)
    elif name in ("Генератор", "ГПУ"):
        _oval(canvas, (6, 6, 23, 23), color, tag)
        _text(canvas, 14.5, 14.5, "G", color, tag, size=9)
        if name == "ГПУ":
            _rect(canvas, (21, 11, 27, 18), color, tag, width=1.1)
            _line(canvas, (23, 11, 23, 8), color, tag, width=1)
            _line(canvas, (25, 11, 25, 8), color, tag, width=1)
    elif name == "Трансформатор 2-обм.":
        _transformer_2w(canvas, color, tag)
    elif name == "Трансформатор 2-обм. расщепл.":
        _transformer_split(canvas, color, tag)
    elif name == "Трансформатор 3-обм.":
        _transformer_3w(canvas, color, tag)
    elif name == "ВЛ":
        _line(canvas, (3, 14, 26, 14), color, tag)
        _line(canvas, (8, 14, 10, 20, 13, 8, 16, 20, 19, 8, 21, 14), color, tag, width=1.3)
    elif name in ("КЛ", "Кабельная линия 0,4 кВ"):
        _cable(canvas, color, tag)
    elif name == "Выключатель":
        _line(canvas, (14, 3, 14, 9), color, tag)
        _rect(canvas, (9, 9, 19, 19), color, tag)
        _line(canvas, (14, 19, 14, 26), color, tag)
    elif name == "Секция шин":
        _bus(canvas, color, tag, "section")
    elif name == "Фазная шина":
        _bus(canvas, color, tag, "phase")
    elif name == "Шина N":
        _bus(canvas, color, tag, "neutral")
    elif name == "Шина PE":
        _bus(canvas, color, tag, "pe")
    elif name == "Шина PEN":
        _bus(canvas, color, tag, "pen")
    elif name == "Нагрузка":
        _load(canvas, color, tag)
    elif name == "Нагрузка 0,4 кВ":
        _load(canvas, color, tag, low_voltage=True)
    elif name == "Узел":
        _dot(canvas, 14.5, 14.5, color, tag, radius=2.4)
    elif name.startswith("Автоматический выключатель "):
        poles = int(name[-2])
        _automatic_breaker(canvas, poles, color, tag)
    elif name == "Секционный автоматический выключатель":
        _automatic_breaker(canvas, 3, color, tag, sectional=True)
    elif name == "Рубильник":
        _knife_switch(canvas, color, tag)
    elif name == "Контактор":
        _contact(canvas, 12, color, tag)
        _oval(canvas, (17, 17, 23, 23), color, tag, width=1.2)
    elif name == "УЗО":
        _automatic_breaker(canvas, 2, color, tag, rcd=True)
        _text(canvas, 22, 6, "T", color, tag, size=5)
    elif name == "Дифференциальный автомат":
        _automatic_breaker(canvas, 2, color, tag, diff=True)
        _text(canvas, 21, 6, "Δ", color, tag, size=7)
    elif name in ("ГРЩ", "ЩСУ", "ЩО", "ШР"):
        _panel(canvas, color, tag, name)
    return True
