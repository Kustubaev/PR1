DEFAULT_ROTATION_VERTICAL = 90

ROUTE_STYLE_AUTO = "auto"
ROUTE_STYLE_HV = "hv"
ROUTE_STYLE_VH = "vh"
ROUTE_STYLES = (ROUTE_STYLE_AUTO, ROUTE_STYLE_HV, ROUTE_STYLE_VH)


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
