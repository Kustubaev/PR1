DEFAULT_ROTATION_VERTICAL = 90

ROUTE_STYLE_AUTO = "auto"
ROUTE_STYLE_HV = "hv"
ROUTE_STYLE_VH = "vh"
ROUTE_STYLES = (ROUTE_STYLE_AUTO, ROUTE_STYLE_HV, ROUTE_STYLE_VH)

# One catalogue for the command ribbon and compact UGO previews.  The last
# flag controls visibility in the compact Plan ribbon; gas infrastructure is
# still available when creating an object from the project commands.
PLAN_TOOL_GROUPS = (
    ("Объекты", (
        "Завод", "Цех", "Компрессорная", "Насосная", "Котельная",
        "Административный корпус", "Прочий объект",
    ), False, True),
    ("Энергетика", (
        "Энергосистема", "ГПП", "ТП", "РП",
        "Собственная электростанция", "Мини-ТЭЦ", "Системная подстанция",
    ), False, True),
    ("Газовая инфраструктура", ("Точка подключения ПГ",), False, False),
    ("Связи", ("КЛ", "ВЛ", "Газопровод", "Технологическая связь", "Прочая связь"), True, True),
)

SCHEME_TOOL_GROUPS = (
    ("Источники", ("Внешняя энергосистема", "Генератор", "ГПУ"), False),
    ("Оборудование", (
        "Трансформатор 2-обм.", "Трансформатор 2-обм. расщепл.", "Трансформатор 3-обм.",
    ), False),
    ("Соединения", ("ВЛ", "КЛ", "Выключатель", "Секция шин"), False),
    ("Нагрузка", ("Нагрузка", "Узел"), False),
    ("Защита", (
        "Автоматический выключатель 1P", "Автоматический выключатель 2P",
        "Автоматический выключатель 3P", "Автоматический выключатель 4P",
        "Секционный автоматический выключатель", "УЗО", "Дифференциальный автомат",
    ), False),
    ("Коммутация", ("Рубильник", "Контактор"), False),
    ("Шины", ("Фазная шина", "Шина N", "Шина PE", "Шина PEN"), False),
    ("Распределение", ("Кабельная линия 0,4 кВ", "Нагрузка 0,4 кВ", "ГРЩ", "ЩСУ", "ЩО", "ШР"), False),
)


def tool_names(groups):
    """Return a flat, ordered tuple of tool names from a catalogue."""
    return tuple(name for group in groups for name in group[1])


PLAN_TOOL_NAMES = tool_names(PLAN_TOOL_GROUPS)
SCHEME_TOOL_NAMES = tool_names(SCHEME_TOOL_GROUPS)


class PowerElement:
    def __init__(self, eid, name, element_type, x, y, rotation=0, **kw):
        self.id = eid
        self.name = name or ""
        self.element_type = element_type
        self.x = float(x)
        self.y = float(y)
        self.rotation = int(rotation or 0)
        self.busbar_left_extent = 50.0
        self.busbar_right_extent = 50.0
        self.closed = True
        self.line_extent_a = 0.0
        self.line_extent_b = 0.0
        self.cable_seal_mode = "both"
        self.u_nom_kv = 0.0
        self.pole_count = 0
        self.catalog_model = ""
        for key, value in kw.items():
            setattr(self, key, value)


def is_mv_voltage(u_kv):
    u = abs(float(u_kv or 0.0))
    return 5.5 <= u <= 7.2 or 9.4 <= u <= 11.6


def normalize_route_style(style):
    raw = str(style or ROUTE_STYLE_AUTO).strip().lower()
    aliases = {
        "": ROUTE_STYLE_AUTO,
        "авто": ROUTE_STYLE_AUTO,
        "горизонталь": ROUTE_STYLE_HV,
        "h-v": ROUTE_STYLE_HV,
        "h_v": ROUTE_STYLE_HV,
        "вертикаль": ROUTE_STYLE_VH,
        "v-h": ROUTE_STYLE_VH,
        "v_h": ROUTE_STYLE_VH,
    }
    mapped = aliases.get(raw, raw)
    return mapped if mapped in ROUTE_STYLES else ROUTE_STYLE_AUTO
