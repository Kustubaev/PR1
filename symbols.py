import math
import tkinter as tk


SYMBOL_SIZE = 18
PX_PER_MM = 96.0 / 25.4
GRID_MODULE_MM = 5.0

WINDING_CIRCLE_R_MM = 10.0
WINDING_CIRCLE_D_MM = WINDING_CIRCLE_R_MM * 2.0
MACHINE_SOURCE_R_MM = 12.0
MACHINE_SINE_SPAN_FRAC = 0.84
MACHINE_SINE_AMP_FRAC = 0.34
MACHINE_LABEL_G_H_MM = 11.0
EXTERNAL_GRID_SYMBOL_OFFSET_Y_MM = 0.8
TRANSFORMER_BODY_HEIGHT_MM = WINDING_CIRCLE_R_MM * 3.0
TRANSFORMER_ROW_GAP_MM = WINDING_CIRCLE_R_MM * 0.5
UGO_GOST_BASE_WINDING_R_MM = 5.0
UGO_AUX_SCALE = WINDING_CIRCLE_R_MM / UGO_GOST_BASE_WINDING_R_MM
AXIS_STUB_MM = 2.0
TRANSFORMER_STUB_MM = 1.5
SWITCH_BODY_AXIS_MM = 10.0
SWITCH_BODY_WIDTH_MM = 8.0
SWITCH_BOX_W_MM = 6.0
SWITCH_BOX_H_MM = 4.0
LINE_HALF_SPAN_MM = 8.0
MIN_LINE_HALF_EXTENT = 10.0
LINE_END_MARK_D_MM = 2.0
CABLE_END_TRI_WIDTH_MM = 2.0
CABLE_END_TRI_HEIGHT_MM = 3.0
CABLE_END_TRI_MM = CABLE_END_TRI_WIDTH_MM
LOAD_OFFSET_Y_MM = 1.0
LOAD_INPUT_STUB_MM = 2.5
LOAD_STEM_MM = 4.0
LOAD_ARROW_H_MM = 2.2
LOAD_ARROW_SPREAD_MM = 1.6
NODE_DOT_D_MM = 2.0
GPU_CENTER_OFFSET_Y_MM = 1.5
BUSBAR_WIDTH_MM = 1.5
BUSBAR_DEFAULT_EXTRA_MM = 5.0
LABEL_FONT_H_MM = 2.5
LABEL_FONT_LARGE_H_MM = 3.5

MV_CHEVRON_SIZE_MM = 2.8
MV_AXISSTUB_MM = 5.5
MV_CONTACT_INNER_FRAC = 0.35
MV_CONTACT_OUTER_FRAC = 0.72
MV_CONTACT_BODY_PAD_MM = 0.0
MV_CONTACT_BODY_CLEAR_MM = 1.2
MV_CONTACT_MIN_DASH_MM = 1.5

AV_POLE_PITCH_MM = 4.0
AV_SLANT_H_MM = 3.0
AV_GAP_ABOVE_SLANT_MM = 1.0
AV_SLANT_V_MM = 6.0
AV_GAP_BELOW_SLANT_MM = 2.0
AV_LINK_SPACING_MM = 2.0
AV_RECT_W_MM = 1.5
AV_RECT_L_MM = 3.0
AV_OL_STUB_MM = 2.0
AV_OL_STUB_TOP_MM = 3.5
AV_OL_HEIGHT_MM = AV_GAP_ABOVE_SLANT_MM + AV_SLANT_V_MM + AV_GAP_BELOW_SLANT_MM
AV_OL_BLADE_MM = AV_SLANT_H_MM
AV_OL_TICK_MM = 1.8
AV_OL_TRIP_HALF_MM = 1.2
AV_OL_CONTACT_D_MM = 1.2

COLOR = "#000000"
FONT_SYMBOL = ("Arial", 8, "bold")
FONT_LABEL = ("Arial", 8)
FONT_SMALL = ("Arial", 7)
SELECTION_COLOR = "#2563eb"
HANDLE_COLOR = "#2563eb"
HANDLE_SIZE = 5


def _busbar_line_width(symbol_size = None):
    return _stroke_w(max(2, int(round(_gost_mm(BUSBAR_WIDTH_MM, symbol_size)))))


BUSBAR_LINE_WIDTH = 4  # fallback до первой отрисовки с масштабом

_BREAKER_DRAW_TYPES = (
    "Выключатель",
    "АВ 220 В",
    "АВ 380 В",
    "Автоматический выключатель 0,4 кВ",
    "Выключатель 6(10) кВ",
    "Выключатель 6/10 кВ с выкатным элементом",
    "Автоматический выключатель 1P",
    "Автоматический выключатель 2P",
    "Автоматический выключатель 3P",
    "Автоматический выключатель 4P",
    "Секционный автоматический выключатель",
    "Выключатель нагрузки",
    "Рубильник",
    "Контактор",
    "УЗО",
    "Дифференциальный автомат",
)


def _u(symbol_size = None):
    return float(symbol_size if symbol_size is not None else SYMBOL_SIZE)


def symbol_size_for_element(element_type, base_size = None):
    return max(8.0, _u(base_size))


def _scale_factor(symbol_size = None):
    return _u(symbol_size) / float(SYMBOL_SIZE)


def _mm(v, symbol_size = None):
    return v * PX_PER_MM * _scale_factor(symbol_size)


def _gost_mm(v, symbol_size = None):
    return _mm(v * UGO_AUX_SCALE, symbol_size)


def _font_mm(height_mm, symbol_size = None, *, bold = False):
    px = max(3, int(round(_gost_mm(height_mm, symbol_size) * _view_scale)))
    return ("Arial", px, "bold") if bold else ("Arial", px)


def _font_raw_mm(height_mm, symbol_size = None, *, bold = False):
    px = max(3, int(round(_mm(height_mm, symbol_size) * _view_scale)))
    return ("Arial", px, "bold") if bold else ("Arial", px)


def _ui_font(size_at_100 = 8.0, *, bold = False):
    px = max(3, int(round(float(size_at_100) * _view_scale)))
    return ("Arial", px, "bold") if bold else ("Arial", px)


def _winding_radius(symbol_size = None):
    return _mm(WINDING_CIRCLE_R_MM, symbol_size)


def _machine_radius(symbol_size = None):
    return _mm(MACHINE_SOURCE_R_MM, symbol_size)


def _winding_overlap_gap(r):
    return r * 0.5


def _transformer_2w_circle_x(cx, r):
    offset = _winding_overlap_gap(r)
    return cx - offset, cx + offset


def _transformer_triangle_vertical(
    cx, cy, r
):
    half = _winding_overlap_gap(r)
    top = (cx, cy - half)
    bottom_l = (cx - half, cy + half)
    bottom_r = (cx + half, cy + half)
    return top, bottom_l, bottom_r


def _transformer_3w_circle_centers(
    cx, cy, r
):
    return _transformer_triangle_vertical(cx, cy, r)


def _transformer_stub(symbol_size):
    return _gost_mm(TRANSFORMER_STUB_MM, symbol_size)


def _load_input_stub(symbol_size):
    return _gost_mm(LOAD_INPUT_STUB_MM, symbol_size)


def _switch_body_halves(
    symbol_size = None,
):
    bh = _mm(SWITCH_BODY_AXIS_MM / 2.0, symbol_size)
    bw = _mm(SWITCH_BODY_WIDTH_MM / 2.0, symbol_size)
    return bh, bw


def _geom(symbol_size = None):
    u = float(_u(symbol_size))
    r = _winding_radius(symbol_size)
    stub = _gost_mm(AXIS_STUB_MM, symbol_size)
    hw, hh = _switch_body_halves(symbol_size)
    span = _gost_mm(LINE_HALF_SPAN_MM, symbol_size)
    return u, r, stub, hw, hh, span


def _switch_axis_half(symbol_size):
    _, _, stub, hw, _, _ = _geom(symbol_size)
    return hw + stub


def _mv_breaker_layout(symbol_size):
    ss = symbol_size
    bh, bw = _switch_body_halves(symbol_size)
    stub = _gost_mm(MV_AXISSTUB_MM, symbol_size)
    ch = _gost_mm(MV_CHEVRON_SIZE_MM, symbol_size)
    _, depth = _mv_chevron_shape(ch)
    return {
        "body_half": bh,
        "body_half_w": bw,
        "ch": ch,
        "chev_depth": depth,
        "stub_len": stub,
        "axis_half": bh + stub,
        "symbol_size": ss,
    }


def av_pole_count_for_element(element):
    if element.element_type in ("АВ 380 В", "Автоматический выключатель 3P"):
        return 3
    if element.element_type == "Автоматический выключатель 1P":
        return 1
    if element.element_type == "Автоматический выключатель 2P":
        return 2
    if element.element_type in ("Автоматический выключатель 4P", "Секционный автоматический выключатель"):
        return 4
    poles = int(getattr(element, "pole_count", 0) or 0)
    if poles > 0:
        return max(1, min(poles, 4))
    if element.element_type.endswith("1P"):
        return 1
    if element.element_type.endswith("2P"):
        return 2
    if element.element_type.endswith("3P"):
        return 3
    if element.element_type.endswith("4P"):
        return 4
    if element.element_type in ("УЗО", "Дифференциальный автомат"):
        return 2
    u = float(getattr(element, "u_nom_kv", 0.4) or 0.4)
    if abs(u - 0.23) < 0.03:
        return 1 if element.element_type == "АВ 220 В" else 2
    return 3


def _link_is_vertical(rotation):
    return _norm_rotation(rotation) in (90, 270)


def _neighbor_elements(element):
    if _connection_project is None:
        return []
    out = []
    for conn in _connection_project.connections.values():
        oid = None
        if conn.from_element_id == element.id:
            oid = conn.to_element_id
        elif conn.to_element_id == element.id:
            oid = conn.from_element_id
        if oid is None:
            continue
        other = _connection_project.get_element(oid)
        if other is not None:
            out.append(other)
    return out


def is_breaker_element(element):
    t = element.element_type
    return (
        t == "Выключатель"
        or t in _MV_TYPES
        or t in _BREAKER_DRAW_TYPES
        or uses_mv_withdrawable_symbol(element)
    )


def effective_breaker_rotation(element):
    from ugo_model import DEFAULT_ROTATION_VERTICAL

    if not is_breaker_element(element):
        return _norm_rotation(element.rotation)

    nbs = _neighbor_elements(element)
    tol = 12.0
    name_lc = (element.name or "").lower()

    if "сек" in name_lc:
        return 0

    buses = [n for n in nbs if n.element_type in _BUS_TYPES]
    if len(buses) >= 2 and all(abs(float(b.y) - float(element.y)) < tol for b in buses):
        return 0

    if not nbs:
        stored = _norm_rotation(element.rotation)
        if stored in (0, 90, 180, 270):
            return stored
        return DEFAULT_ROTATION_VERTICAL

    cx, cy = float(element.x), float(element.y)
    above = any(float(n.y) < cy - tol for n in nbs)
    below = any(float(n.y) > cy + tol for n in nbs)
    left = any(float(n.x) < cx - tol for n in nbs)
    right = any(float(n.x) > cx + tol for n in nbs)

    if above and below and not (left and right):
        return DEFAULT_ROTATION_VERTICAL
    if left and right and not (above and below):
        return 0

    if len(nbs) == 1:
        nb = nbs[0]
        dx = abs(float(nb.x) - cx)
        dy = abs(float(nb.y) - cy)
        if dy > dx:
            return DEFAULT_ROTATION_VERTICAL
        if dx > dy:
            return 0

    ys = [float(n.y) for n in nbs]
    xs = [float(n.x) for n in nbs]
    if len(nbs) >= 2 and max(ys) - min(ys) > max(xs) - min(xs):
        return DEFAULT_ROTATION_VERTICAL
    if len(nbs) >= 2 and max(xs) - min(xs) > max(ys) - min(ys):
        return 0
    if above or below:
        return DEFAULT_ROTATION_VERTICAL
    if left or right:
        return 0
    return DEFAULT_ROTATION_VERTICAL


def sync_breaker_rotations(project):
    if project is None:
        return 0
    prev = _connection_project
    set_connection_project(project)
    try:
        changed = 0
        for el in project.elements.values():
            if not is_breaker_element(el):
                continue
            new_rot = effective_breaker_rotation(el)
            if _norm_rotation(el.rotation) != _norm_rotation(new_rot):
                el.rotation = new_rot
                changed += 1
        return changed
    finally:
        set_connection_project(prev)


def _element_rotation(element):
    return _norm_rotation(element.rotation)


def _visual_element_type(element):
    return element.element_type


_AV_TYPES = frozenset(
    {
        "Автоматический выключатель 0,4 кВ",
        "АВ 220 В",
        "АВ 380 В",
        "Автоматический выключатель 1P",
        "Автоматический выключатель 2P",
        "Автоматический выключатель 3P",
        "Автоматический выключатель 4P",
        "Секционный автоматический выключатель",
        "УЗО",
        "Дифференциальный автомат",
    }
)
_MV_TYPES = frozenset(
    {"Выключатель 6(10) кВ", "Выключатель 6/10 кВ с выкатным элементом"}
)
_TRANSFORMER_TYPES = frozenset(
    {
        "Трансформатор 2-обм.",
        "Трансформатор",
        "Трансформатор 2-обм. расщепл.",
        "Трансформатор 3-обм.",
    }
)


def uses_mv_withdrawable_symbol(element):
    if element.element_type in _MV_TYPES:
        return True
    if element.element_type == "Выключатель":
        from ugo_model import is_mv_voltage

        u = float(getattr(element, "u_nom_kv", 0.0) or 0.0)
        return is_mv_voltage(u)
    return False


def needs_link_axis_visual_gap(a, b):
    tr = a.element_type in _TRANSFORMER_TYPES or b.element_type in _TRANSFORMER_TYPES
    mv = uses_mv_withdrawable_symbol(a) or uses_mv_withdrawable_symbol(b)
    return tr and mv


_LV_SWITCH_TYPES = frozenset({"Выключатель нагрузки", "Рубильник", "Контактор"})
_BUS_TYPES = frozenset({"Секция шин", "Фазная шина", "Шина N", "Шина PE", "Шина PEN"})
_LINE_TYPES = frozenset({"ВЛ", "КЛ", "Кабельная линия 0,4 кВ"})
_PANEL_TYPES = frozenset({"ГРЩ", "ЩСУ", "ЩО", "ШР"})

_draw_coord_transform = None
_connection_project = None
_view_scale = 1.0
LINK_MIN_DRAW_MM = 1.5


def set_connection_project(project):
    global _connection_project
    _connection_project = project


def set_draw_coord_transform(fn):
    global _draw_coord_transform
    _draw_coord_transform = fn


def set_view_scale(scale):
    global _view_scale
    _view_scale = 1.0 if scale is None else max(0.05, float(scale))


def _stroke_w(base):
    return max(1, int(round(base * _view_scale)))


def _map_xy(x, y):
    if _draw_coord_transform is None:
        return x, y
    return _draw_coord_transform(x, y)


def _map_flat(coords):
    mapped = []
    for i in range(0, len(coords) - 1, 2):
        mx, my = _map_xy(coords[i], coords[i + 1])
        mapped.extend((mx, my))
    return tuple(mapped)


def _wl(
    canvas,
    x1,
    y1,
    x2,
    y2,
    tags,
    *,
    width = 2,
    dash = None,
):
    kw = {"fill": COLOR, "width": _stroke_w(width), "tags": tags}
    if dash:
        kw["dash"] = dash
    x1, y1 = _map_xy(x1, y1)
    x2, y2 = _map_xy(x2, y2)
    canvas.create_line(x1, y1, x2, y2, **kw)


def _wpl(
    canvas,
    coords,
    tags,
    *,
    width = 2,
    dash = None,
):
    if len(coords) < 4:
        return
    kw = {"fill": COLOR, "width": _stroke_w(width), "tags": tags}
    if dash:
        kw["dash"] = dash
    canvas.create_line(*_map_flat(coords), **kw)


def _wo(
    canvas, x1, y1, x2, y2, tags
):
    x1, y1 = _map_xy(x1, y1)
    x2, y2 = _map_xy(x2, y2)
    canvas.create_oval(x1, y1, x2, y2, outline=COLOR, width=_stroke_w(1), fill="", tags=tags)


def _wr(
    canvas,
    x1,
    y1,
    x2,
    y2,
    tags,
    *,
    fill = "white",
    outline = COLOR,
):
    x1, y1 = _map_xy(x1, y1)
    x2, y2 = _map_xy(x2, y2)
    kw = {"fill": fill, "tags": tags}
    if outline is not None:
        kw["outline"] = outline
        kw["width"] = _stroke_w(2)
    canvas.create_rectangle(x1, y1, x2, y2, **kw)


def _switch_body_fill(*, closed = True):
    return "white" if closed else COLOR


def _breaker_port_points(
    cx, cy, axis_half, rotation
):
    if _link_is_vertical(rotation):
        return (cx, cy - axis_half), (cx, cy + axis_half)
    return (cx - axis_half, cy), (cx + axis_half, cy)


def _av_port_points(
    cx, cy, lay, rotation
):
    neg = lay["axis_neg"]
    pos = lay["axis_pos"]
    if _link_is_vertical(rotation):
        return (cx, cy - neg), (cx, cy + pos)
    return (cx - neg, cy), (cx + pos, cy)


def _av_breaker_layout(symbol_size, pole_count):
    stub_top = _gost_mm(AV_OL_STUB_TOP_MM, symbol_size)
    stub_bot = _gost_mm(AV_OL_STUB_MM, symbol_size)
    spread = _gost_mm(AV_SLANT_H_MM, symbol_size)
    pitch = _gost_mm(AV_POLE_PITCH_MM, symbol_size)
    gap_above = _gost_mm(AV_GAP_ABOVE_SLANT_MM, symbol_size)
    slant_v = _gost_mm(AV_SLANT_V_MM, symbol_size)
    gap_below = _gost_mm(AV_GAP_BELOW_SLANT_MM, symbol_size)
    half_contact = (gap_above + slant_v + gap_below) / 2.0
    axis_neg = half_contact + stub_top
    axis_pos = half_contact + stub_bot
    axis_half = max(axis_neg, axis_pos)
    rect_w = _gost_mm(AV_RECT_W_MM / 2.0, symbol_size)
    rect_l = _gost_mm(AV_RECT_L_MM / 2.0, symbol_size)
    link_half = _gost_mm(AV_LINK_SPACING_MM / 2.0, symbol_size)
    n = max(1, int(pole_count))
    half_spread = (n - 1) / 2.0 * pitch + spread + rect_w + _gost_mm(0.5, symbol_size)
    return {
        "axis_half": axis_half,
        "axis_neg": axis_neg,
        "axis_pos": axis_pos,
        "half_contact": half_contact,
        "stub": stub_bot,
        "stub_top": stub_top,
        "spread": spread,
        "pitch": pitch,
        "gap_above": gap_above,
        "slant_v": slant_v,
        "gap_below": gap_below,
        "rect_w": rect_w,
        "rect_l": rect_l,
        "link_half": link_half,
        "half_spread": half_spread,
        "half_h": half_contact,
        "gap": half_contact,
        "cross": rect_l * 2.0,
        "blade_dx": spread,
        "blade_dy": -slant_v,
        "tick": rect_l * 2.0,
        "trip": _gost_mm(AV_OL_TRIP_HALF_MM, symbol_size),
        "dot_r": _gost_mm(AV_OL_CONTACT_D_MM / 2.0, symbol_size),
    }


def visual_center_offset(
    element_type,
    *,
    rotation = 0,
    symbol_size = None,
    pole_count = None,
):

    poles = pole_count
    el = PowerElement(0, "", element_type, 0.0, 0.0, rotation=rotation)
    if poles is None and element_type in _AV_TYPES:
        if element_type == "АВ 220 В":
            el.pole_count = 2  # type: ignore[attr-defined]
            el.u_nom_kv = 0.23
        else:
            el.pole_count = 3  # type: ignore[attr-defined]
        poles = av_pole_count_for_element(el)
    if poles:
        el.pole_count = poles  # type: ignore[attr-defined]
    ss = symbol_size_for_element(element_type, symbol_size)
    el.x, el.y = 0.0, 0.0
    x1, y1, x2, y2 = symbol_bounds(el, symbol_size=ss)
    return (x1 + x2) / 2.0, (y1 + y2) / 2.0


def anchor_for_visual_center(
    element_type,
    pointer_x,
    pointer_y,
    *,
    rotation = 0,
    symbol_size = None,
    pole_count = None,
):
    ox, oy = visual_center_offset(
        element_type,
        rotation=rotation,
        symbol_size=symbol_size,
        pole_count=pole_count,
    )
    return pointer_x - ox, pointer_y - oy


def _norm_rotation(deg):
    return int(deg) % 360


def rot_point(cx, cy, x, y, deg):
    deg = _norm_rotation(deg)
    if deg == 0:
        return x, y
    rad = math.radians(deg)
    dx, dy = x - cx, y - cy
    cos_r, sin_r = math.cos(rad), math.sin(rad)
    return cx + dx * cos_r - dy * sin_r, cy + dx * sin_r + dy * cos_r


def rot_bounds(
    cx, cy, x1, y1, x2, y2, deg
):
    deg = _norm_rotation(deg)
    if deg == 0:
        return int(x1), int(y1), int(x2), int(y2)
    corners = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
    rotated = [rot_point(cx, cy, px, py, deg) for px, py in corners]
    xs = [p[0] for p in rotated]
    ys = [p[1] for p in rotated]
    return int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))


def _line(canvas, x1, y1, x2, y2, tags, width = 2, **kw):
    x1, y1 = _map_xy(x1, y1)
    x2, y2 = _map_xy(x2, y2)
    w = kw.pop("width", width)
    return canvas.create_line(x1, y1, x2, y2, fill=COLOR, width=_stroke_w(w), tags=tags, **kw)


def _oval(canvas, x1, y1, x2, y2, tags, width = 2, fill = ""):
    x1, y1 = _map_xy(x1, y1)
    x2, y2 = _map_xy(x2, y2)
    return canvas.create_oval(x1, y1, x2, y2, outline=COLOR, width=_stroke_w(width), fill=fill, tags=tags)


def _text(canvas, x, y, text, tags, font=None, anchor=tk.CENTER):
    x, y = _map_xy(x, y)
    if font is None or font is FONT_LABEL:
        font = _ui_font(8)
    return canvas.create_text(x, y, text=text, fill=COLOR, font=font, anchor=anchor, tags=tags)


def _rline(
    canvas,
    cx,
    cy,
    x1,
    y1,
    x2,
    y2,
    rot,
    tags,
    width = 2,
):
    ax, ay = rot_point(cx, cy, x1, y1, rot)
    bx, by = rot_point(cx, cy, x2, y2, rot)
    return _line(canvas, ax, ay, bx, by, tags, width=width)


def _rpline(
    canvas,
    cx,
    cy,
    local_coords,
    rot,
    tags,
    *,
    width = 2,
):
    if len(local_coords) < 4:
        return
    rotated = []
    for i in range(0, len(local_coords), 2):
        px, py = rot_point(cx, cy, local_coords[i], local_coords[i + 1], rot)
        rotated.extend([px, py])
    _wpl(canvas, tuple(rotated), tags, width=width)


def _machine_sine_coords(center_x, center_y, r):
    half_span = r * MACHINE_SINE_SPAN_FRAC
    amp = r * MACHINE_SINE_AMP_FRAC
    steps = 36
    coords = []
    for i in range(steps + 1):
        t = i / steps
        x = center_x - half_span + 2.0 * half_span * t
        y = center_y + amp * math.sin(t * 2.0 * math.pi)
        coords.extend([x, y])
    return coords


def _draw_machine_sine(
    canvas,
    cx,
    cy,
    center_x,
    center_y,
    r,
    rot,
    tags,
):
    _rpline(canvas, cx, cy, _machine_sine_coords(center_x, center_y, r), rot, tags)


def _roval(
    canvas,
    cx,
    cy,
    x1,
    y1,
    x2,
    y2,
    rot,
    tags,
    width = 2,
    fill = "",
):
    pts = [
        rot_point(cx, cy, x1, y1, rot),
        rot_point(cx, cy, x2, y1, rot),
        rot_point(cx, cy, x2, y2, rot),
        rot_point(cx, cy, x1, y2, rot),
    ]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return _oval(canvas, min(xs), min(ys), max(xs), max(ys), tags, width=width, fill=fill)


def _rrect(
    canvas,
    cx,
    cy,
    x1,
    y1,
    x2,
    y2,
    rot,
    tags,
    width = 2,
    fill = "white",
):
    pts = [
        rot_point(cx, cy, x1, y1, rot),
        rot_point(cx, cy, x2, y1, rot),
        rot_point(cx, cy, x2, y2, rot),
        rot_point(cx, cy, x1, y2, rot),
    ]
    return canvas.create_polygon(
        *_map_flat([c for p in pts for c in p]),
        outline=COLOR,
        width=width,
        fill=fill,
        tags=tags,
    )


def _rtext(
    canvas,
    cx,
    cy,
    lx,
    ly,
    text,
    rot,
    tags,
    font=None,
    anchor=tk.CENTER,
):
    tx, ty = rot_point(cx, cy, lx, ly, rot)
    return _text(canvas, tx, ty, text, tags, font=font, anchor=anchor)


def draw_external_grid(
    canvas, x, y, sym_tags, anno_tags, symbol_size = None, rotation = 0,
    *, linked = None,
):
    _, _, stub, _, _, _ = _geom(symbol_size)
    r = _machine_radius(symbol_size)
    cx, cy = float(x), float(y)
    cy_sym = cy - _gost_mm(EXTERNAL_GRID_SYMBOL_OFFSET_Y_MM, symbol_size)
    _roval(canvas, cx, cy, cx - r, cy_sym - r, cx + r, cy_sym + r, rotation, sym_tags)
    _draw_machine_sine(canvas, cx, cy, cx, cy_sym, r, rotation, sym_tags)
    if "pos" not in (linked or frozenset()):
        _rline(canvas, cx, cy, cx, cy_sym + r, cx, cy_sym + r + stub, rotation, sym_tags)


def draw_generator(
    canvas, x, y, sym_tags, anno_tags, symbol_size = None, rotation = 0,
    *, linked = None,
):
    _, _, stub, _, _, _ = _geom(symbol_size)
    r = _machine_radius(symbol_size)
    cx, cy = float(x), float(y)
    if "neg" not in (linked or frozenset()):
        _rline(canvas, cx, cy, cx, cy - r - stub, cx, cy - r, rotation, sym_tags)
    _roval(canvas, cx, cy, cx - r, cy - r, cx + r, cy + r, rotation, sym_tags)
    _rtext(
        canvas, cx, cy, cx, cy, "G", rotation, sym_tags,
        font=_font_raw_mm(MACHINE_LABEL_G_H_MM, symbol_size, bold=True),
    )


def draw_gpu(
    canvas, x, y, sym_tags, anno_tags, symbol_size = None, rotation = 0,
    *, linked = None,
):
    _, _, stub, _, _, _ = _geom(symbol_size)
    r = _machine_radius(symbol_size)
    cx, cy = float(x), float(y) - _gost_mm(GPU_CENTER_OFFSET_Y_MM, symbol_size)
    if "neg" not in (linked or frozenset()):
        _rline(canvas, cx, cy, cx, cy - r - stub, cx, cy - r, rotation, sym_tags)
    _roval(canvas, cx, cy, cx - r, cy - r, cx + r, cy + r, rotation, sym_tags)
    _rtext(
        canvas, cx, cy, cx, cy, "G", rotation, sym_tags,
        font=_font_raw_mm(MACHINE_LABEL_G_H_MM, symbol_size, bold=True),
    )


def draw_transformer_2w(
    canvas, x, y, sym_tags, anno_tags, symbol_size = None, rotation = 0,
    *, linked = None,
):
    _, r, stub, _, _, _ = _geom(symbol_size)
    t_stub = _transformer_stub(symbol_size)
    cx, cy = float(x), float(y)
    c1x, c2x = _transformer_2w_circle_x(cx, r)
    active = linked or frozenset()
    if "neg" not in active:
        _rline(canvas, cx, cy, c1x - r - t_stub, cy, c1x - r, cy, rotation, sym_tags)
    if "pos" not in active:
        _rline(canvas, cx, cy, c2x + r, cy, c2x + r + t_stub, cy, rotation, sym_tags)
    _roval(canvas, cx, cy, c1x - r, cy - r, c1x + r, cy + r, rotation, sym_tags)
    _roval(canvas, cx, cy, c2x - r, cy - r, c2x + r, cy + r, rotation, sym_tags)


def _split_lv_lead_dirs():
    s = math.sqrt(0.5)
    return (-s, s), (s, s)


def _split_transformer_geometry(
    cx, cy, r, stub
):
    top, bl, br = _transformer_triangle_vertical(cx, cy, r)
    dir_l, dir_r = _split_lv_lead_dirs()
    blx, bly = bl
    brx, bry = br
    edge_l = (blx + r * dir_l[0], bly + r * dir_l[1])
    edge_r = (brx + r * dir_r[0], bry + r * dir_r[1])
    tip_l = (edge_l[0] + stub * dir_l[0], edge_l[1] + stub * dir_l[1])
    tip_r = (edge_r[0] + stub * dir_r[0], edge_r[1] + stub * dir_r[1])
    tip_hv = (top[0], top[1] - r - stub)
    edge_hv = (top[0], top[1] - r)
    return top, bl, br, edge_hv, tip_hv, tip_l, tip_r


def draw_transformer_split_2w(
    canvas, x, y, sym_tags, anno_tags, symbol_size = None, rotation = 0,
    *, linked = None,
):
    _, r, stub, _, _, _ = _geom(symbol_size)
    t_stub = _transformer_stub(symbol_size)
    cx, cy = float(x), float(y)
    top, bl, br, edge_hv, tip_hv, tip_l, tip_r = _split_transformer_geometry(
        cx, cy, r, t_stub
    )
    tx, ty = top
    blx, bly = bl
    brx, bry = br
    dir_l, dir_r = _split_lv_lead_dirs()
    edge_l = (blx + r * dir_l[0], bly + r * dir_l[1])
    edge_r = (brx + r * dir_r[0], bry + r * dir_r[1])
    del linked
    _rline(
        canvas, cx, cy, tip_hv[0], tip_hv[1], edge_hv[0], edge_hv[1], rotation, sym_tags
    )
    _roval(canvas, cx, cy, tx - r, ty - r, tx + r, ty + r, rotation, sym_tags)
    _roval(canvas, cx, cy, blx - r, bly - r, blx + r, bly + r, rotation, sym_tags)
    _roval(canvas, cx, cy, brx - r, bry - r, brx + r, bry + r, rotation, sym_tags)
    _rline(
        canvas, cx, cy, edge_l[0], edge_l[1], tip_l[0], tip_l[1], rotation, sym_tags
    )
    _rline(
        canvas, cx, cy, edge_r[0], edge_r[1], tip_r[0], tip_r[1], rotation, sym_tags
    )


def draw_transformer_3w(
    canvas, x, y, sym_tags, anno_tags, symbol_size = None, rotation = 0,
    *, linked = None,
):
    _, r, _, _, _, _ = _geom(symbol_size)
    t_stub = _transformer_stub(symbol_size)
    cx, cy = float(x), float(y)
    top, bl, br = _transformer_3w_circle_centers(cx, cy, r)
    tx, ty = top
    blx, bly = bl
    brx, bry = br
    active = linked or frozenset()
    rotated_centers = [
        rot_point(cx, cy, tx, ty, rotation),
        rot_point(cx, cy, blx, bly, rotation),
        rot_point(cx, cy, brx, bry, rotation),
    ]
    hv_x, hv_y = min(rotated_centers, key=lambda p: p[1])
    lv_x, lv_y = max(rotated_centers, key=lambda p: p[1])
    mv_x, mv_y = max(rotated_centers, key=lambda p: p[0])
    if "neg" not in active:
        _line(canvas, hv_x, hv_y - r - t_stub, hv_x, hv_y - r, sym_tags)
    if "pos" not in active:
        _line(canvas, lv_x, lv_y + r, lv_x, lv_y + r + t_stub, sym_tags)
    if "mv" not in active:
        _line(canvas, mv_x + r, mv_y, mv_x + r + t_stub, mv_y, sym_tags)
    _roval(canvas, cx, cy, tx - r, ty - r, tx + r, ty + r, rotation, sym_tags)
    _roval(canvas, cx, cy, blx - r, bly - r, blx + r, bly + r, rotation, sym_tags)
    _roval(canvas, cx, cy, brx - r, bry - r, brx + r, bry + r, rotation, sym_tags)


def draw_overhead_line(
    canvas,
    x,
    y,
    sym_tags,
    anno_tags,
    symbol_size = None,
    rotation = 0,
    *,
    line_extent_a = None,
    line_extent_b = None,
):
    cx, cy = float(x), float(y)
    default = _gost_mm(LINE_HALF_SPAN_MM, symbol_size)
    ea = line_extent_a if line_extent_a is not None else default
    eb = line_extent_b if line_extent_b is not None else default
    x_outer_l, x_outer_r = cx - ea, cx + eb
    _rline(
        canvas,
        cx,
        cy,
        x_outer_l,
        cy,
        x_outer_r,
        cy,
        rotation,
        sym_tags,
        width=4,
    )


def draw_plan_cable_seal(
    canvas,
    tip_x,
    tip_y,
    along_x,
    along_y,
    *,
    color,
    tags,
    symbol_size = None,
    width_px = None,
    height_px = None,
    fill = "white",
    width = 1,
):
    dx = along_x - tip_x
    dy = along_y - tip_y
    length = math.hypot(dx, dy)
    if length < 1e-9:
        return
    ux, uy = dx / length, dy / length
    if width_px is not None and height_px is not None:
        w, half_h = float(width_px), float(height_px) / 2.0
    else:
        w = _gost_mm(CABLE_END_TRI_WIDTH_MM, symbol_size)
        half_h = _gost_mm(CABLE_END_TRI_HEIGHT_MM / 2.0, symbol_size)
    apex_x = tip_x + ux * w
    apex_y = tip_y + uy * w
    pts = (
        tip_x - uy * half_h,
        tip_y + ux * half_h,
        tip_x + uy * half_h,
        tip_y - ux * half_h,
        apex_x,
        apex_y,
    )
    canvas.create_polygon(
        *_map_flat(pts),
        outline=color,
        fill=fill,
        width=width,
        tags=tags,
    )


def _line_extents(
    element, symbol_size = None
):
    ss = symbol_size_for_element(element.element_type, symbol_size)
    default = _gost_mm(LINE_HALF_SPAN_MM, ss)
    a = float(getattr(element, "line_extent_a", 0.0) or 0.0)
    b = float(getattr(element, "line_extent_b", 0.0) or 0.0)
    return (a if a > 0 else default), (b if b > 0 else default)


def _line_segment_layout(
    symbol_size,
    line_type,
    extent_a,
    extent_b,
):
    if line_type == "КЛ":
        inset = _gost_mm(CABLE_END_TRI_WIDTH_MM, symbol_size)
    else:
        inset = 0.0
    return extent_a, extent_b, inset


def _line_local_ports(
    cx,
    cy,
    extent_a,
    extent_b,
    inset,
    *,
    line_type = "ВЛ",
):
    del inset
    return (cx - extent_a, cy), (cx + extent_b, cy)


def _cable_end_triangle(
    canvas,
    cx,
    cy,
    tip_x,
    tip_y,
    outward,
    rot,
    tags,
    *,
    symbol_size = None,
    apex_outward = False,
):
    w = _gost_mm(CABLE_END_TRI_WIDTH_MM, symbol_size)
    half_h = _gost_mm(CABLE_END_TRI_HEIGHT_MM / 2.0, symbol_size)
    side = 1 if outward >= 0 else -1
    if apex_outward:
        apex_x = tip_x + side * w
        base_x = tip_x
        local = [base_x, tip_y - half_h, base_x, tip_y + half_h, apex_x, tip_y]
    else:
        base_x = tip_x + side * w
        local = [base_x, tip_y - half_h, base_x, tip_y + half_h, tip_x, tip_y]
    pts = []
    for i in range(0, len(local), 2):
        px, py = rot_point(cx, cy, local[i], local[i + 1], rot)
        pts.extend([px, py])
    canvas.create_polygon(
        *_map_flat(pts),
        outline=COLOR,
        fill="white",
        width=_stroke_w(1),
        tags=tags,
    )


def draw_cable_line(
    canvas,
    x,
    y,
    sym_tags,
    anno_tags,
    symbol_size = None,
    rotation = 0,
    *,
    line_extent_a = None,
    line_extent_b = None,
    cable_seal_mode = "both",
):
    cx, cy = float(x), float(y)
    default = _gost_mm(LINE_HALF_SPAN_MM, symbol_size)
    ea = line_extent_a if line_extent_a is not None else default
    eb = line_extent_b if line_extent_b is not None else default
    seal_w = _gost_mm(CABLE_END_TRI_WIDTH_MM, symbol_size)
    mode = (cable_seal_mode or "both").strip().lower()
    port_l, port_r = cx - ea, cx + eb
    tip_l, tip_r = port_l + seal_w, port_r - seal_w
    draw_a = mode in ("both", "a", "a_out")
    draw_b = mode in ("both", "b", "b_out")
    line_left = tip_l if draw_a and mode != "a_out" else port_l
    line_right = tip_r if draw_b and mode != "b_out" else port_r
    if mode == "a_out":
        line_left = tip_l  # линия от основания перевернутой заделки
    if mode == "b_out":
        line_right = tip_r
    if not draw_a:
        line_left = port_l
    if not draw_b:
        line_right = port_r
    if line_right > line_left + 1.0:
        _rline(canvas, cx, cy, line_left, cy, line_right, cy, rotation, sym_tags)
    if draw_a:
        _cable_end_triangle(
            canvas,
            cx,
            cy,
            tip_l,
            cy,
            outward=-1,
            rot=rotation,
            tags=sym_tags,
            symbol_size=symbol_size,
            apex_outward=mode == "a_out",
        )
    if draw_b:
        _cable_end_triangle(
            canvas,
            cx,
            cy,
            tip_r,
            cy,
            outward=1,
            rot=rotation,
            tags=sym_tags,
            symbol_size=symbol_size,
            apex_outward=mode == "b_out",
        )


def draw_cable_seal_at(
    canvas,
    tip_x,
    tip_y,
    along_x,
    along_y,
    tags,
    *,
    symbol_size = None,
    apex_outward = True,
):
    dx = along_x - tip_x
    dy = along_y - tip_y
    length = math.hypot(dx, dy)
    if length < 1e-9:
        return
    ux, uy = dx / length, dy / length
    w = _gost_mm(CABLE_END_TRI_WIDTH_MM, symbol_size)
    half_h = _gost_mm(CABLE_END_TRI_HEIGHT_MM / 2.0, symbol_size)
    if apex_outward:
        apex_x, apex_y = tip_x, tip_y
        base_x = tip_x + ux * w
        base_y = tip_y + uy * w
    else:
        apex_x = tip_x + ux * w
        apex_y = tip_y + uy * w
        base_x, base_y = tip_x, tip_y
    pts = (
        base_x - uy * half_h,
        base_y + ux * half_h,
        base_x + uy * half_h,
        base_y - ux * half_h,
        apex_x,
        apex_y,
    )
    canvas.create_polygon(
        *_map_flat(pts),
        outline=COLOR,
        fill="white",
        width=_stroke_w(1),
        tags=tags,
    )


def draw_circuit_breaker(
    canvas,
    x,
    y,
    sym_tags,
    anno_tags,
    symbol_size = None,
    rotation = 0,
    *,
    linked = None,
    closed = True,
):
    del linked
    _, _, stub, bh, bw, _ = _geom(symbol_size)
    cx, cy = float(x), float(y)
    axis = bh + stub
    fill = _switch_body_fill(closed=closed)
    if _link_is_vertical(rotation):
        _wr(canvas, cx - bw, cy - bh, cx + bw, cy + bh, sym_tags, fill=fill)
        _wl(canvas, cx, cy - axis, cx, cy - bh, sym_tags, width=2)
        _wl(canvas, cx, cy + bh, cx, cy + axis, sym_tags, width=2)
    else:
        _wr(canvas, cx - bh, cy - bw, cx + bh, cy + bw, sym_tags, fill=fill)
        _wl(canvas, cx - axis, cy, cx - bh, cy, sym_tags, width=2)
        _wl(canvas, cx + bh, cy, cx + axis, cy, sym_tags, width=2)


def _mv_outer_chevron_tip(
    body_edge,
    conn_edge,
    depth,
    symbol_size,
):
    clear = _gost_mm(MV_CONTACT_BODY_CLEAR_MM, symbol_size)
    tips = _mv_stub_chevron_tips(body_edge, conn_edge, depth, count=2, body_clear=clear)
    if not tips:
        return conn_edge
    if conn_edge < body_edge:
        return min(tips)
    return max(tips)


def _mv_connection_port_points(
    cx, cy, lay, rotation
):
    bh = lay["body_half"]
    axis = lay["axis_half"]
    if _link_is_vertical(rotation):
        return (cx, cy - axis), (cx, cy + axis)
    return (cx - axis, cy), (cx + axis, cy)


def _mv_chevron_shape(size):
    leg = size * 0.55
    return leg, leg


def _mv_stub_chevron_tips(
    body_edge,
    conn_edge,
    depth,
    *,
    count = 2,
    body_clear = 0.0,
):
    if count <= 0:
        return []
    margin = depth + body_clear
    if conn_edge < body_edge:
        zone_start = conn_edge
        zone_end = body_edge - margin
        if zone_start >= zone_end:
            zone_end = body_edge - depth * 0.45
    elif conn_edge > body_edge:
        zone_start = body_edge + margin
        zone_end = conn_edge
        if zone_start >= zone_end:
            zone_start = body_edge + depth * 0.45
    else:
        return [body_edge]
    if count == 1:
        return [(zone_start + zone_end) / 2.0]
    tips = []
    for frac in (MV_CONTACT_OUTER_FRAC, MV_CONTACT_INNER_FRAC):
        tips.append(zone_start + (zone_end - zone_start) * frac)
    if len(tips) == 2:
        min_dash = _gost_mm(MV_CONTACT_MIN_DASH_MM, None)
        if abs(tips[1] - tips[0]) < min_dash:
            mid = (tips[0] + tips[1]) / 2.0
            half = min_dash / 2.0
            tips = [mid - half, mid + half]
    return tips

def _mv_chevron_v(
    canvas,
    cx,
    tip_y,
    size,
    upward,
    tags,
):
    spread, depth = _mv_chevron_shape(size)
    if upward:
        _wpl(
            canvas,
            (cx - spread, tip_y + depth, cx, tip_y, cx + spread, tip_y + depth),
            tags,
            width=2,
        )
    else:
        _wpl(
            canvas,
            (cx - spread, tip_y - depth, cx, tip_y, cx + spread, tip_y - depth),
            tags,
            width=2,
        )


def _mv_chevron_h(
    canvas,
    tip_x,
    cy,
    size,
    outward,
    tags,
):
    spread, depth = _mv_chevron_shape(size)
    if outward < 0:
        _wpl(
            canvas,
            (tip_x + depth, cy - spread, tip_x, cy, tip_x + depth, cy + spread),
            tags,
            width=2,
        )
    else:
        _wpl(
            canvas,
            (tip_x - depth, cy - spread, tip_x, cy, tip_x - depth, cy + spread),
            tags,
            width=2,
        )


def _draw_mv_withdrawable_contact_v(
    canvas,
    cx,
    body_edge,
    conn_edge,
    ch,
    depth,
    *,
    conn_above_body,
    tags,
    symbol_size = None,
):
    clear = _gost_mm(MV_CONTACT_BODY_CLEAR_MM, symbol_size)
    tips = _mv_stub_chevron_tips(body_edge, conn_edge, depth, count=2, body_clear=clear)
    if len(tips) < 2:
        return
    if conn_above_body:
        t_outer, t_inner = min(tips), max(tips)
        _wl(canvas, cx, body_edge, cx, t_inner, tags)
        _wl(canvas, cx, t_outer, cx, conn_edge, tags)
        _mv_chevron_v(canvas, cx, t_outer, ch, True, tags)
        _mv_chevron_v(canvas, cx, t_inner, ch, True, tags)
    else:
        t_inner, t_outer = min(tips), max(tips)
        _wl(canvas, cx, body_edge, cx, t_inner, tags)
        _wl(canvas, cx, t_outer, cx, conn_edge, tags)
        _mv_chevron_v(canvas, cx, t_inner, ch, False, tags)
        _mv_chevron_v(canvas, cx, t_outer, ch, False, tags)

def _draw_mv_withdrawable_contact_h(
    canvas,
    cy,
    body_edge,
    conn_edge,
    ch,
    depth,
    *,
    conn_is_less,
    tags,
    symbol_size = None,
):
    clear = _gost_mm(MV_CONTACT_BODY_CLEAR_MM, symbol_size)
    tips = _mv_stub_chevron_tips(body_edge, conn_edge, depth, count=2, body_clear=clear)
    if len(tips) < 2:
        return
    outward = -1 if conn_is_less else 1

    if conn_is_less:
        t_outer, t_inner = min(tips), max(tips)
        _wl(canvas, body_edge, cy, t_inner, cy, tags)
        _wl(canvas, t_outer, cy, conn_edge, cy, tags)
        _mv_chevron_h(canvas, t_outer, cy, ch, outward, tags)
        _mv_chevron_h(canvas, t_inner, cy, ch, outward, tags)
    else:
        t_inner, t_outer = min(tips), max(tips)
        _wl(canvas, body_edge, cy, t_inner, cy, tags)
        _wl(canvas, t_outer, cy, conn_edge, cy, tags)
        _mv_chevron_h(canvas, t_inner, cy, ch, outward, tags)
        _mv_chevron_h(canvas, t_outer, cy, ch, outward, tags)


def _draw_mv_vertical_link(
    canvas,
    cx,
    cy,
    lay,
    tags,
    *,
    body_fill = "white",
):
    bh, bw, ch = lay["body_half"], lay["body_half_w"], lay["ch"]
    depth, axis = lay["chev_depth"], lay["axis_half"]
    y_top, y_bot = cy - bh, cy + bh
    y_conn_t, y_conn_b = cy - axis, cy + axis

    _wr(canvas, cx - bw, y_top, cx + bw, y_bot, tags, fill=body_fill)
    _draw_mv_withdrawable_contact_v(
        canvas, cx, y_top, y_conn_t, ch, depth,
        conn_above_body=True, tags=tags, symbol_size=lay.get("symbol_size"),
    )
    _draw_mv_withdrawable_contact_v(
        canvas, cx, y_bot, y_conn_b, ch, depth,
        conn_above_body=False, tags=tags, symbol_size=lay.get("symbol_size"),
    )


def _draw_mv_horizontal_link(
    canvas,
    cx,
    cy,
    lay,
    tags,
    *,
    body_fill = "white",
):
    bh, bw, ch = lay["body_half"], lay["body_half_w"], lay["ch"]
    depth, axis = lay["chev_depth"], lay["axis_half"]
    x_left, x_right = cx - bh, cx + bh
    x_conn_l, x_conn_r = cx - axis, cx + axis

    _wr(canvas, x_left, cy - bw, x_right, cy + bw, tags, fill=body_fill)
    _draw_mv_withdrawable_contact_h(
        canvas, cy, x_left, x_conn_l, ch, depth,
        conn_is_less=True, tags=tags, symbol_size=lay.get("symbol_size"),
    )
    _draw_mv_withdrawable_contact_h(
        canvas, cy, x_right, x_conn_r, ch, depth,
        conn_is_less=False, tags=tags, symbol_size=lay.get("symbol_size"),
    )


def _draw_av_blade_tick(
    canvas,
    px,
    py,
    bx,
    by,
    tick,
    tags,
):
    dx, dy = bx - px, by - py
    length = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / length, dx / length
    _wl(canvas, bx, by, bx + nx * tick, by + ny * tick, tags)


def _draw_av_breaker_rect(
    canvas,
    cx,
    cy,
    ux,
    uy,
    half_len,
    half_w,
    tags,
    *,
    fill = "",
):
    nx, ny = -uy, ux
    corners = []
    for sl, sw in ((1, 1), (1, -1), (-1, -1), (-1, 1)):
        corners.append((cx + sl * half_len * ux + sw * half_w * nx, cy + sl * half_len * uy + sw * half_w * ny))
    if fill:
        flat = []
        for px, py in corners:
            mx, my = _map_xy(px, py)
            flat.extend([mx, my])
        canvas.create_polygon(*flat, fill=fill, outline=COLOR, width=_stroke_w(1), tags=tags)
        return
    for i in range(4):
        a = corners[i]
        b = corners[(i + 1) % 4]
        _wl(canvas, a[0], a[1], b[0], b[1], tags)


def _draw_av_breaker(
    canvas,
    cx,
    cy,
    lay,
    tags,
    *,
    vertical,
    poles = 1,
    linked = None,
    closed = True,
):
    axis_neg = lay["axis_neg"]
    axis_pos = lay["axis_pos"]
    half_contact = lay["half_contact"]
    spread = lay["spread"]
    pitch = lay["pitch"]
    gap_above = lay["gap_above"]
    slant_v = lay["slant_v"]
    rect_w = lay["rect_w"]
    rect_l = lay["rect_l"]
    link_half = lay["link_half"]
    n = max(1, int(poles))

    y_top = -half_contact
    y_tip = y_top + gap_above
    y_piv = y_tip + slant_v
    slant_mid_y = (y_piv + y_tip) / 2.0

    def pt(dx, dy):
        if vertical:
            return (cx + dx, cy + dy)
        return (cx + dy, cy - dx)

    def slant_x(off, y):
        t = (y - y_piv) / (y_tip - y_piv)
        t = max(0.0, min(1.0, t))
        return off - t * spread

    offs = [(i - (n - 1) / 2.0) * pitch for i in range(n)]
    left_off = offs[0]

    for off in offs:
        piv = pt(off, y_piv)
        tip = pt(off - spread, y_tip)
        _wl(canvas, *pt(off, -axis_neg), *pt(off, y_top), tags)
        _wl(canvas, *piv, *tip, tags)
        _wl(canvas, *piv, *pt(off, axis_pos), tags)

    t_c = 0.5
    touch = pt(left_off + t_c * (-spread), y_piv + t_c * (y_tip - y_piv))
    piv0 = pt(left_off, y_piv)
    tip0 = pt(left_off - spread, y_tip)
    ux, uy = tip0[0] - piv0[0], tip0[1] - piv0[1]
    ln = math.hypot(ux, uy) or 1.0
    ux, uy = ux / ln, uy / ln
    nx, ny = -uy, ux
    rcx = touch[0] - nx * rect_w
    rcy = touch[1] - ny * rect_w
    _draw_av_breaker_rect(
        canvas,
        rcx,
        rcy,
        ux,
        uy,
        rect_l,
        rect_w,
        tags,
        fill="",
    )

    if n >= 2:
        for y_link in (slant_mid_y - link_half, slant_mid_y + link_half):
            _wl(
                canvas,
                *pt(slant_x(offs[0], y_link), y_link),
                *pt(slant_x(offs[-1], y_link), y_link),
                tags,
            )


def draw_automatic_breaker(
    canvas,
    x,
    y,
    sym_tags,
    anno_tags,
    symbol_size = None,
    rotation = 0,
    *,
    pole_count = 3,
    linked = None,
    closed = True,
):
    cx, cy = float(x), float(y)
    lay = _av_breaker_layout(symbol_size, pole_count)
    _draw_av_breaker(
        canvas,
        cx,
        cy,
        lay,
        sym_tags,
        vertical=_link_is_vertical(rotation),
        poles=pole_count,
        linked=linked,
        closed=closed,
    )


def draw_lv_breaker(
    canvas,
    x,
    y,
    sym_tags,
    anno_tags,
    symbol_size = None,
    rotation = 0,
    *,
    pole_count = 3,
):
    draw_automatic_breaker(
        canvas, x, y, sym_tags, anno_tags, symbol_size, rotation, pole_count=pole_count
    )


def _draw_rotated_line(
    canvas,
    cx,
    cy,
    x1,
    y1,
    x2,
    y2,
    rotation,
    tags,
    *,
    width = 2,
    dash = None,
):
    ax, ay = rot_point(cx, cy, x1, y1, rotation)
    bx, by = rot_point(cx, cy, x2, y2, rotation)
    _wl(canvas, ax, ay, bx, by, tags, width=width, dash=dash)


def draw_lv_switchgear_contact(
    canvas,
    x,
    y,
    sym_tags,
    anno_tags,
    symbol_size = None,
    rotation = 0,
    *,
    linked = None,
):
    cx, cy = float(x), float(y)
    lay = _av_breaker_layout(symbol_size, 3)
    gap = lay["gap"]
    axis_neg = lay["axis_neg"]
    axis_pos = lay["axis_pos"]
    spread = lay["spread"]
    if _link_is_vertical(rotation):
        pivot_y = cy + gap
        fixed_y = cy - gap
        _wl(canvas, cx, cy - axis_neg, cx, fixed_y, sym_tags)
        _wl(canvas, cx, cy + axis_pos, cx, pivot_y, sym_tags)
        _wl(canvas, cx, pivot_y, cx + spread, fixed_y, sym_tags)
    else:
        pivot_x = cx - gap
        fixed_x = cx + gap
        _wl(canvas, cx - axis_neg, cy, pivot_x, cy, sym_tags)
        _wl(canvas, cx + axis_pos, cy, fixed_x, cy, sym_tags)
        _wl(canvas, pivot_x, cy, fixed_x, cy - spread, sym_tags)


def draw_contactor(
    canvas,
    x,
    y,
    sym_tags,
    anno_tags,
    symbol_size = None,
    rotation = 0,
    *,
    linked = None,
):
    draw_lv_switchgear_contact(canvas, x, y, sym_tags, anno_tags, symbol_size, rotation, linked=linked)
    cx, cy = float(x), float(y)
    r = _gost_mm(1.3, symbol_size)
    off = _gost_mm(4.2, symbol_size)
    ox, oy = (cx + off, cy) if _link_is_vertical(rotation) else (cx, cy + off)
    _oval(canvas, ox - r, oy - r, ox + r, oy + r, sym_tags, width=2)


def _draw_bus_line(
    canvas,
    x,
    y,
    sym_tags,
    anno_tags,
    symbol_size,
    rotation,
    busbar_left_extent,
    busbar_right_extent,
    *,
    label,
    dashed = False,
    thick = False,
):
    _, _, _, _, _, span = _geom(symbol_size)
    cx, cy = float(x), float(y)
    default_half = span + _gost_mm(BUSBAR_DEFAULT_EXTRA_MM, symbol_size)
    left = busbar_left_extent if busbar_left_extent is not None else default_half
    right = busbar_right_extent if busbar_right_extent is not None else default_half
    width = _busbar_line_width(symbol_size) if thick else 2
    _draw_rotated_line(
        canvas,
        cx,
        cy,
        cx - left,
        cy,
        cx + right,
        cy,
        rotation,
        sym_tags,
        width=width,
        dash=(6, 5) if dashed else None,
    )
    tx, ty = rot_point(cx, cy, cx - left - _gost_mm(4.0, symbol_size), cy, rotation)
    _text(canvas, tx, ty, label, anno_tags, font=_font_mm(2.5, symbol_size), anchor=tk.E)


def draw_phase_bus(
    canvas,
    x,
    y,
    sym_tags,
    anno_tags,
    symbol_size = None,
    rotation = 0,
    busbar_left_extent = None,
    busbar_right_extent = None,
):
    _draw_bus_line(
        canvas, x, y, sym_tags, anno_tags, symbol_size, rotation,
        busbar_left_extent, busbar_right_extent, label="L1 L2 L3", thick=True
    )


def draw_neutral_bus(
    canvas,
    x,
    y,
    sym_tags,
    anno_tags,
    symbol_size = None,
    rotation = 0,
    busbar_left_extent = None,
    busbar_right_extent = None,
):
    _draw_bus_line(
        canvas, x, y, sym_tags, anno_tags, symbol_size, rotation,
        busbar_left_extent, busbar_right_extent, label="N"
    )


def draw_pe_bus(
    canvas,
    x,
    y,
    sym_tags,
    anno_tags,
    symbol_size = None,
    rotation = 0,
    busbar_left_extent = None,
    busbar_right_extent = None,
):
    _draw_bus_line(
        canvas, x, y, sym_tags, anno_tags, symbol_size, rotation,
        busbar_left_extent, busbar_right_extent, label="PE", dashed=True
    )


def draw_pen_bus(
    canvas,
    x,
    y,
    sym_tags,
    anno_tags,
    symbol_size = None,
    rotation = 0,
    busbar_left_extent = None,
    busbar_right_extent = None,
):
    _draw_bus_line(
        canvas, x, y, sym_tags, anno_tags, symbol_size, rotation,
        busbar_left_extent, busbar_right_extent, label="PEN", thick=True
    )


def draw_lv_load(
    canvas,
    x,
    y,
    sym_tags,
    anno_tags,
    symbol_size = None,
    rotation = 0,
):
    cx, cy = float(x), float(y)
    length = _gost_mm(9.0, symbol_size)
    ah = _gost_mm(2.2, symbol_size)
    a = rot_point(cx, cy, cx - length / 2, cy, rotation)
    b = rot_point(cx, cy, cx + length / 2, cy, rotation)
    _wl(canvas, a[0], a[1], b[0], b[1], sym_tags)
    left = rot_point(cx, cy, cx + length / 2 - ah, cy - ah, rotation)
    right = rot_point(cx, cy, cx + length / 2 - ah, cy + ah, rotation)
    flat = [c for p in (b, left, right) for c in p]
    canvas.create_polygon(*_map_flat(flat), fill=COLOR, outline=COLOR, tags=sym_tags)


def draw_panel(
    canvas,
    x,
    y,
    sym_tags,
    anno_tags,
    symbol_size = None,
    rotation = 0,
    *,
    label = "Щ",
):
    cx, cy = float(x), float(y)
    hw = _gost_mm(SWITCH_BOX_W_MM / 2.0, symbol_size)
    hh = _gost_mm(SWITCH_BOX_H_MM / 2.0, symbol_size)
    pts = [
        rot_point(cx, cy, cx - hw, cy - hh, rotation),
        rot_point(cx, cy, cx + hw, cy - hh, rotation),
        rot_point(cx, cy, cx + hw, cy + hh, rotation),
        rot_point(cx, cy, cx - hw, cy + hh, rotation),
    ]
    canvas.create_polygon(
        *_map_flat([v for p in pts for v in p]),
        outline=COLOR,
        fill="white",
        width=2,
        tags=sym_tags,
    )
    _text(canvas, cx, cy, label, anno_tags, font=_font_mm(2.5, symbol_size, bold=True))


def draw_lv_breaker_220(
    canvas,
    x,
    y,
    sym_tags,
    anno_tags,
    symbol_size = None,
    rotation = 0,
):
    draw_automatic_breaker(
        canvas, x, y, sym_tags, anno_tags, symbol_size, rotation, pole_count=2
    )


def draw_mv_withdrawable_breaker(
    canvas,
    x,
    y,
    sym_tags,
    anno_tags,
    symbol_size = None,
    rotation = 0,
    *,
    linked = None,
    closed = True,
):
    del linked
    cx, cy = float(x), float(y)
    lay = _mv_breaker_layout(symbol_size)
    fill = _switch_body_fill(closed=closed)
    if _link_is_vertical(rotation):
        _draw_mv_vertical_link(canvas, cx, cy, lay, sym_tags, body_fill=fill)
    else:
        _draw_mv_horizontal_link(canvas, cx, cy, lay, sym_tags, body_fill=fill)


def _breaker_symbol_bounds(
    element, symbol_size = None
):
    ss = symbol_size_for_element(element.element_type, symbol_size)
    cx, cy = float(element.x), float(element.y)
    pad = 4.0
    t = element.element_type
    if t in _AV_TYPES:
        poles = av_pole_count_for_element(element)
        lay = _av_breaker_layout(ss, poles)
        if _link_is_vertical(_element_rotation(element)):
            hx = lay["half_spread"] + pad
            hy = lay["axis_half"] + pad
        else:
            hx = lay["axis_half"] + pad
            hy = lay["half_spread"] + pad
    else:
        lay = _mv_breaker_layout(ss)
        spread, _ = _mv_chevron_shape(lay["ch"])
        chev_w = spread + pad
        if _link_is_vertical(_element_rotation(element)):
            hx = lay["body_half_w"] + chev_w
            hy = lay["axis_half"] + pad
        else:
            hx = lay["axis_half"] + pad
            hy = lay["body_half_w"] + chev_w
    return int(cx - hx), int(cy - hy), int(cx + hx), int(cy + hy)


def draw_busbar(
    canvas,
    x,
    y,
    sym_tags,
    anno_tags,
    symbol_size = None,
    rotation = 0,
    busbar_left_extent = None,
    busbar_right_extent = None,
):
    _, _, _, _, _, span = _geom(symbol_size)
    cx, cy = float(x), float(y)
    default_half = span + _gost_mm(BUSBAR_DEFAULT_EXTRA_MM, symbol_size)
    left = busbar_left_extent if busbar_left_extent is not None else default_half
    right = busbar_right_extent if busbar_right_extent is not None else default_half
    lw = _busbar_line_width(symbol_size)

    _rline(
        canvas, cx, cy, cx - left, cy, cx + right, cy, rotation, sym_tags,
        width=lw,
    )


def draw_load(
    canvas, x, y, sym_tags, anno_tags, symbol_size = None, rotation = 0
):
    _, _, stub, _, _, _ = _geom(symbol_size)
    cx, cy = float(x), float(y) - _gost_mm(LOAD_OFFSET_Y_MM, symbol_size)
    in_stub = _load_input_stub(symbol_size)
    stem = _gost_mm(LOAD_STEM_MM, symbol_size)
    ah = _gost_mm(LOAD_ARROW_H_MM, symbol_size)
    spread = _gost_mm(LOAD_ARROW_SPREAD_MM, symbol_size)
    _rline(canvas, cx, cy, cx, cy - in_stub, cx, cy, rotation, sym_tags)
    _rline(canvas, cx, cy, cx, cy, cx, cy + stem + stub, rotation, sym_tags)
    tip = rot_point(cx, cy, cx, cy + stem + stub + ah, rotation)
    left = rot_point(cx, cy, cx - spread, cy + stem + stub, rotation)
    right = rot_point(cx, cy, cx + spread, cy + stem + stub, rotation)
    canvas.create_polygon(
        *_map_flat([c for p in (tip, left, right) for c in p]),
        outline=COLOR,
        fill=COLOR,
        tags=sym_tags,
    )


def draw_node(
    canvas, x, y, sym_tags, anno_tags, symbol_size = None, rotation = 0
):
    cx, cy = float(x), float(y)
    dot = _gost_mm(NODE_DOT_D_MM / 2.0, symbol_size)
    _roval(canvas, cx, cy, cx - dot, cy - dot, cx + dot, cy + dot, rotation, sym_tags, width=1, fill=COLOR)


def is_routing_bend_node(element):
    if element.element_type != "Узел":
        return False
    name = (element.name or "").strip()
    return name.startswith("Поворот") or name.startswith("Узел СН")


def _bounds_unrotated(element, symbol_size = None):
    visual_type = _visual_element_type(element)
    ss = symbol_size_for_element(visual_type, symbol_size)
    _, r, stub, hw, hh, span = _geom(ss)
    cx, cy = float(element.x), float(element.y)
    pad = _gost_mm(1.0, ss)
    t = visual_type

    if t == "Внешняя энергосистема":
        cy_sym = cy - _gost_mm(EXTERNAL_GRID_SYMBOL_OFFSET_Y_MM, ss)
        r = _machine_radius(ss)
        return cx - r - pad, cy_sym - r - pad, cx + r + pad, cy_sym + r + stub + pad
    if t == "Генератор":
        r = _machine_radius(ss)
        return cx - r - pad, cy - r - stub - pad, cx + r + pad, cy + r + pad
    if t == "ГПУ":
        r = _machine_radius(ss)
        cy_sym = cy - _gost_mm(GPU_CENTER_OFFSET_Y_MM, ss)
        return cx - r - pad, cy_sym - r - stub - pad, cx + r + pad, cy_sym + r + pad
    if t in ("Трансформатор 2-обм.", "Трансформатор"):
        c1x, c2x = _transformer_2w_circle_x(cx, r)
        return c1x - r - stub - pad, cy - r - pad, c2x + r + stub + pad, cy + r + pad
    if t == "Трансформатор 2-обм. расщепл.":
        t_stub = _transformer_stub(ss)
        top, bl, br, _, tip_hv, tip_l, tip_r = _split_transformer_geometry(
            cx, cy, r, t_stub
        )
        xs = [top[0], bl[0], br[0], tip_hv[0], tip_l[0], tip_r[0]]
        ys = [top[1], bl[1], br[1], tip_hv[1], tip_l[1], tip_r[1]]
        return (
            min(xs) - r - pad,
            min(ys) - r - pad,
            max(xs) + r + pad,
            max(ys) + r + pad,
        )
    if t == "Трансформатор 3-обм.":
        top, bl, br = _transformer_3w_circle_centers(cx, cy, r)
        xs = [top[0], bl[0], br[0]]
        ys = [top[1], bl[1], br[1]]
        return (
            min(xs) - r - pad,
            min(ys) - r - stub - pad,
            max(xs) + r + stub + pad,
            max(ys) + r + stub + pad,
        )
    if t in _LINE_TYPES:
        ea, eb = _line_extents(element, ss)
        return cx - ea - pad, cy - pad, cx + eb + pad, cy + pad
    if t == "Выключатель":
        if uses_mv_withdrawable_symbol(element):
            x1, y1, x2, y2 = _breaker_symbol_bounds(element, symbol_size)
            return float(x1), float(y1), float(x2), float(y2)
        return cx - hw - stub - pad, cy - hh - pad, cx + hw + stub + pad, cy + hh + pad
    if t in _AV_TYPES or t in _MV_TYPES:
        x1, y1, x2, y2 = _breaker_symbol_bounds(element, symbol_size)
        return float(x1), float(y1), float(x2), float(y2)
    if t in _BREAKER_DRAW_TYPES:
        return cx - hw - stub - pad, cy - hh - pad, cx + hw + stub + pad, cy + hh + pad
    if t in _BUS_TYPES:
        left = element.busbar_left_extent
        right = element.busbar_right_extent
        return cx - left - pad, cy - pad - 2, cx + right + pad, cy + pad + 6
    if t == "Нагрузка":
        cy_sym = cy - _gost_mm(LOAD_OFFSET_Y_MM, ss)
        in_stub = _load_input_stub(ss)
        stem = _gost_mm(LOAD_STEM_MM, ss)
        ah = _gost_mm(LOAD_ARROW_H_MM, ss)
        spread = _gost_mm(LOAD_ARROW_SPREAD_MM, ss)
        return cx - spread - pad, cy_sym - in_stub - pad, cx + spread + pad, cy_sym + stem + stub + ah + pad
    if t == "Нагрузка 0,4 кВ":
        return cx - span - pad, cy - _gost_mm(4.0, ss) - pad, cx + span + pad, cy + _gost_mm(4.0, ss) + pad
    if t in _PANEL_TYPES:
        hw_panel = _gost_mm(SWITCH_BOX_W_MM / 2.0, ss)
        hh_panel = _gost_mm(SWITCH_BOX_H_MM / 2.0, ss)
        return cx - hw_panel - pad, cy - hh_panel - pad, cx + hw_panel + pad, cy + hh_panel + pad
    if t == "Узел":
        dot = _gost_mm(NODE_DOT_D_MM / 2.0, ss)
        return cx - dot - pad, cy - dot - pad, cx + dot + pad, cy + dot + pad
    return cx - span - pad, cy - span - pad, cx + span + pad, cy + span + pad


def _link_axis_body_extent(
    element, symbol_size = None
):
    ss = symbol_size_for_element(element.element_type, symbol_size)
    cx, cy = float(element.x), float(element.y)
    rot = _element_rotation(element)
    t = element.element_type

    if t == "Выключатель" or uses_mv_withdrawable_symbol(element) or t in _MV_TYPES:
        bh, _ = _switch_body_halves(ss)
        if rot in (90, 270):
            return cy - bh, cy + bh
        return cx - bh, cx + bh

    x1, y1, x2, y2 = _bounds_unrotated(element, ss)
    x1, y1, x2, y2 = rot_bounds(cx, cy, x1, y1, x2, y2, rot)
    if rot in (90, 270):
        return min(y1, y2), max(y1, y2)
    return min(x1, x2), max(x1, x2)


def _link_axis_full_extent(
    element, symbol_size = None
):
    ss = symbol_size_for_element(element.element_type, symbol_size)
    cx, cy = float(element.x), float(element.y)
    rot = _element_rotation(element)

    if uses_mv_withdrawable_symbol(element) or element.element_type in _MV_TYPES:
        axis = _mv_breaker_layout(ss)["axis_half"]
        if rot in (90, 270):
            return cy - axis, cy + axis
        return cx - axis, cx + axis
    if element.element_type == "Выключатель":
        axis = _switch_axis_half(ss)
        if rot in (90, 270):
            return cy - axis, cy + axis
        return cx - axis, cx + axis

    return _link_axis_body_extent(element, ss)


def symbol_bounds(
    element,
    x = None,
    y = None,
    symbol_size = None,
):
    if isinstance(element, str):
        from ugo_model import PowerElement as PE

        el = PE(0, "", element, float(x or 0), float(y or 0))
        ss = symbol_size_for_element(element, symbol_size)
        if element in _AV_TYPES or element in _MV_TYPES:
            return _breaker_symbol_bounds(el, ss)
        x1, y1, x2, y2 = _bounds_unrotated(el, ss)
        return int(x1), int(y1), int(x2), int(y2)
    ss = symbol_size_for_element(element.element_type, symbol_size)
    if (
        element.element_type in _AV_TYPES
        or element.element_type in _MV_TYPES
        or uses_mv_withdrawable_symbol(element)
    ):
        return _breaker_symbol_bounds(element, ss)
    x1, y1, x2, y2 = _bounds_unrotated(element, ss)
    return rot_bounds(element.x, element.y, x1, y1, x2, y2, element.rotation)


def _hit_segment(
    ax, ay, bx, by, px, py, tol
):
    dx, dy = bx - ax, by - ay
    length_sq = dx * dx + dy * dy
    if length_sq < 1e-6:
        return (px - ax) ** 2 + (py - ay) ** 2 <= tol ** 2
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / length_sq))
    proj_x = ax + t * dx
    proj_y = ay + t * dy
    return (px - proj_x) ** 2 + (py - proj_y) ** 2 <= tol ** 2


def _hit_horizontal_segment(cx, cy, half, px, py, tol):
    return _hit_segment(cx - half, cy, cx + half, cy, px, py, tol)


def _nearest_on_segment(
    ax, ay, bx, by, px, py
):
    dx, dy = bx - ax, by - ay
    length_sq = dx * dx + dy * dy
    if length_sq < 1e-6:
        return ax, ay
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / length_sq))
    return ax + t * dx, ay + t * dy


def nearest_point_on_busbar(
    element, target_x, target_y
):
    p1, p2 = busbar_endpoints(element)
    return _nearest_on_segment(p1[0], p1[1], p2[0], p2[1], target_x, target_y)


def point_in_element(
    element,
    px,
    py,
    padding = 4,
    symbol_size = None,
):
    t = element.element_type
    cx, cy = element.x, element.y
    ss = symbol_size_for_element(t, symbol_size)
    u = _u(ss)
    _, r, _, _, _, _ = _geom(ss)
    tol = max(_gost_mm(2.0, ss), r * 0.35) + padding

    if t == "Узел":
        dot = _gost_mm(NODE_DOT_D_MM / 2.0, ss) + padding
        return (px - cx) ** 2 + (py - cy) ** 2 <= dot ** 2
    if t in _LINE_TYPES:
        ea, eb = _line_extents(element, ss)
        line_type = "КЛ" if t == "Кабельная линия 0,4 кВ" else t
        _, _, inset = _line_segment_layout(ss, line_type, ea, eb)
        p1, p2 = _line_local_ports(cx, cy, ea, eb, inset, line_type=line_type)
        a_pt, b_pt = rot_point(cx, cy, p1[0], p1[1], element.rotation), rot_point(cx, cy, p2[0], p2[1], element.rotation)
        return _hit_segment(a_pt[0], a_pt[1], b_pt[0], b_pt[1], px, py, tol)
    if t in _BUS_TYPES:
        p1, p2 = busbar_endpoints(element)
        return _hit_segment(p1[0], p1[1], p2[0], p2[1], px, py, max(8, u) + padding)

    x1, y1, x2, y2 = symbol_bounds(element, symbol_size=ss)
    return x1 - padding <= px <= x2 + padding and y1 - padding <= py <= y2 + padding


def hit_test_element(
    elements,
    px,
    py,
    symbol_size = None,
):
    for el in reversed(elements):
        if point_in_element(el, px, py, symbol_size=symbol_size):
            return el
    return None


def hit_test_busbar_handle(
    element, px, py, handle
):
    if element.element_type not in _BUS_TYPES:
        return False
    left_pt, right_pt = busbar_endpoints(element)
    hx, hy = left_pt if handle == "left" else right_pt
    return abs(px - hx) <= HANDLE_SIZE + 4 and abs(py - hy) <= HANDLE_SIZE + 4


def _connection_side_toward(
    element, other_x, other_y
):
    cx, cy = float(element.x), float(element.y)
    dx = float(other_x) - cx
    dy = float(other_y) - cy
    if element.element_type in _TRANSFORMER_TYPES:
        if abs(dy) >= abs(dx) * 0.85:
            return "neg" if dy < 0 else "pos"
        return "mv" if dx > 0 else "neg"
    rot = _element_rotation(element)
    if _link_is_vertical(rot):
        return "neg" if dy < 0 else "pos"
    return "neg" if dx < 0 else "pos"


def active_link_sides(
    element, symbol_size = None
):
    if _connection_project is None:
        return frozenset()
    sides = set()
    for conn in _connection_project.connections.values():
        if conn.from_element_id == element.id:
            oid = conn.to_element_id
        elif conn.to_element_id == element.id:
            oid = conn.from_element_id
        else:
            continue
        other = _connection_project.get_element(oid)
        if other is None:
            continue
        sides.add(_connection_side_toward(element, other.x, other.y))
    return frozenset(sides)


def _ports_coincide(
    p1,
    p2,
    symbol_size = None,
):
    snap = _gost_mm(2.5, symbol_size)
    return abs(p1[0] - p2[0]) < snap and abs(p1[1] - p2[1]) < snap


def _bus_coincident_link_stub(
    bus,
    other,
    joint,
    symbol_size = None,
):
    min_dist = _gost_mm(LINK_MIN_DRAW_MM, symbol_size)
    jx, jy = joint[0], joint[1]
    bx, by = float(bus.x), float(bus.y)
    ox, oy = float(other.x), float(other.y)
    chain_tol = max(20.0, _gost_mm(5.0, symbol_size))

    if abs(by - oy) <= chain_tol and abs(bx - ox) > chain_tol:
        if ox > bx:
            return (jx - min_dist, jy), (jx, jy)
        return (jx, jy), (jx + min_dist, jy)
    if abs(bx - ox) <= chain_tol and abs(by - oy) > chain_tol:
        if oy > by:
            return (jx, jy - min_dist), (jx, jy)
        return (jx, jy), (jx, jy + min_dist)

    half = max(min_dist / 2.0, _gost_mm(0.9, symbol_size))
    return (jx - half, jy), (jx + half, jy)


def connection_ports(element, symbol_size = None):
    visual_type = _visual_element_type(element)
    ss = symbol_size_for_element(visual_type, symbol_size)
    _, r, stub, hw, _, span = _geom(ss)
    cx, cy = float(element.x), float(element.y)
    rot = _element_rotation(element)
    t = visual_type

    def rp(lx, ly):
        return rot_point(cx, cy, lx, ly, rot)

    if t == "Внешняя энергосистема":
        cy_sym = cy - _gost_mm(EXTERNAL_GRID_SYMBOL_OFFSET_Y_MM, ss)
        r = _machine_radius(ss)
        return [rp(cx, cy_sym - r), rp(cx, cy_sym + r)]
    if t in ("Генератор", "ГПУ"):
        cy_sym = cy - _gost_mm(GPU_CENTER_OFFSET_Y_MM, ss) if t == "ГПУ" else cy
        r = _machine_radius(ss)
        return [rp(cx, cy_sym - r), rp(cx, cy_sym + r)]
    if t in ("Трансформатор 2-обм.", "Трансформатор"):
        c1x, c2x = _transformer_2w_circle_x(cx, r)
        return [rp(c1x - r, cy), rp(c2x + r, cy)]
    if t == "Трансформатор 2-обм. расщепл.":
        t_stub = _transformer_stub(ss)
        _, _, _, _, tip_hv, tip_l, tip_r = _split_transformer_geometry(cx, cy, r, t_stub)
        return [rp(tip_hv[0], tip_hv[1]), rp(tip_l[0], tip_l[1]), rp(tip_r[0], tip_r[1])]
    if t == "Трансформатор 3-обм.":
        top, bl, br = _transformer_3w_circle_centers(cx, cy, r)
        centers = [rp(top[0], top[1]), rp(bl[0], bl[1]), rp(br[0], br[1])]
        hv = min(centers, key=lambda p: p[1])
        lv = max(centers, key=lambda p: p[1])
        mv = max(centers, key=lambda p: p[0])
        return [
            (hv[0], hv[1] - r),
            (lv[0], lv[1] + r),
            (mv[0] + r, mv[1]),
        ]
    if t in _LINE_TYPES:
        ea, eb = _line_extents(element, ss)
        line_type = "КЛ" if t == "Кабельная линия 0,4 кВ" else t
        _, _, inset = _line_segment_layout(ss, line_type, ea, eb)
        p1, p2 = _line_local_ports(cx, cy, ea, eb, inset, line_type=line_type)
        return [rp(p1[0], p1[1]), rp(p2[0], p2[1])]
    if t in _AV_TYPES:
        poles = av_pole_count_for_element(element)
        lay = _av_breaker_layout(ss, poles)
        return list(_av_port_points(cx, cy, lay, rot))
    if t in _MV_TYPES or (t == "Выключатель" and uses_mv_withdrawable_symbol(element)):
        lay = _mv_breaker_layout(ss)
        return list(_mv_connection_port_points(cx, cy, lay, rot))
    if t == "Выключатель":
        axis = _switch_axis_half(ss)
        p1, p2 = _breaker_port_points(cx, cy, axis, rot)
        return [p1, p2]
    if t in _LV_SWITCH_TYPES:
        lay = _av_breaker_layout(ss, 3)
        return list(_av_port_points(cx, cy, lay, rot))
    if t in _BREAKER_DRAW_TYPES:
        return [
            rp(cx - hw, cy),
            rp(cx + hw, cy),
        ]
    if t in _BUS_TYPES:
        return [rp(cx - element.busbar_left_extent, cy), rp(cx + element.busbar_right_extent, cy)]
    if t == "Нагрузка":
        cy_sym = cy - _gost_mm(LOAD_OFFSET_Y_MM, ss)
        in_stub = _load_input_stub(ss)
        return [
            rot_point(cx, cy_sym, cx, cy_sym - in_stub, rot),
            rot_point(cx, cy_sym, cx, cy_sym, rot),
        ]
    if t == "Нагрузка 0,4 кВ":
        half = _gost_mm(5.0, ss)
        return [rp(cx - half, cy), rp(cx + half, cy)]
    if t in _PANEL_TYPES:
        half = _gost_mm(SWITCH_BOX_W_MM / 2.0, ss)
        return [rp(cx, cy - half), rp(cx, cy + half), rp(cx - half, cy), rp(cx + half, cy)]
    if t == "Узел":
        return [rp(cx, cy)]
    return [rp(cx, cy)]


def nearest_port(
    element,
    target_x,
    target_y,
    symbol_size = None,
):
    if element.element_type in _BUS_TYPES:
        return nearest_point_on_busbar(element, target_x, target_y)
    ports = connection_ports(element, symbol_size)
    best = ports[0]
    best_d = float("inf")
    for px, py in ports:
        d = (px - target_x) ** 2 + (py - target_y) ** 2
        if d < best_d:
            best_d = d
            best = (px, py)
    return best


def connection_point_toward(
    element,
    toward_x,
    toward_y,
    symbol_size = None,
):
    if element.element_type in _BUS_TYPES:
        return nearest_point_on_busbar(element, toward_x, toward_y)
    return nearest_port(element, toward_x, toward_y, symbol_size)


def port_exit_direction(
    element,
    port,
    symbol_size = None,
):
    cx, cy = float(element.x), float(element.y)
    dx, dy = port[0] - cx, port[1] - cy
    length = math.hypot(dx, dy)
    if length < 1e-6:
        rot = _element_rotation(element)
        if rot in (90, 270):
            return (0.0, -1.0)
        return (-1.0, 0.0)
    return dx / length, dy / length


def _snap_collinear(
    x1, y1, x2, y2, snap
):
    if snap <= 0:
        return x1, y1, x2, y2
    dx = abs(x1 - x2)
    dy = abs(y1 - y2)
    if dx <= dy and dx < snap:
        x2 = x1
    elif dy < dx and dy < snap:
        y2 = y1
    return x1, y1, x2, y2


def _facing_port_pair(
    el_a,
    el_b,
    ports_a,
    ports_b,
):
    if not ports_a or not ports_b:
        return ports_a[0], ports_b[0]
    if len(ports_a) == 1 or len(ports_b) == 1:
        return nearest_port_pair(ports_a, ports_b)
    dx = float(el_b.x) - float(el_a.x)
    dy = float(el_b.y) - float(el_a.y)
    tie = 1.0

    def _extreme_axis(
        ports,
        *,
        axis,
        want_max,
        prefer_x,
        prefer_y,
    ):
        vals = [p[axis] for p in ports]
        target = max(vals) if want_max else min(vals)
        cands = [p for p in ports if abs(p[axis] - target) <= tie]
        if axis == 1:  # выбирали по Y — ничью ломаем по X
            return min(cands, key=lambda p: abs(p[0] - prefer_x))
        return min(cands, key=lambda p: abs(p[1] - prefer_y))

    if abs(dy) >= abs(dx):
        if dy >= 0:
            pa = _extreme_axis(
                ports_a, axis=1, want_max=True, prefer_x=float(el_b.x), prefer_y=float(el_b.y)
            )
            pb = min(ports_b, key=lambda p: (p[1], abs(p[0] - pa[0])))
        else:
            pa = _extreme_axis(
                ports_a, axis=1, want_max=False, prefer_x=float(el_b.x), prefer_y=float(el_b.y)
            )
            pb = max(ports_b, key=lambda p: (p[1], -abs(p[0] - pa[0])))
        return pa, pb
    if dx >= 0:
        pa = _extreme_axis(
            ports_a, axis=0, want_max=True, prefer_x=float(el_b.x), prefer_y=float(el_b.y)
        )
        pb = min(ports_b, key=lambda p: (p[0], abs(p[1] - pa[1])))
    else:
        pa = _extreme_axis(
            ports_a, axis=0, want_max=False, prefer_x=float(el_b.x), prefer_y=float(el_b.y)
        )
        pb = max(ports_b, key=lambda p: (p[0], -abs(p[1] - pa[1])))
    return pa, pb


def nearest_port_pair(
    ports_a,
    ports_b,
):
    best = (ports_a[0], ports_b[0])
    best_d = float("inf")
    for pa in ports_a:
        for pb in ports_b:
            d = (pa[0] - pb[0]) ** 2 + (pa[1] - pb[1]) ** 2
            if d < best_d:
                best_d = d
                best = (pa, pb)
    return best


def best_connection_points(
    el_a,
    el_b,
    symbol_size = None,
    *,
    port_index_a = -1,
    port_index_b = -1,
):
    ss = symbol_size_for_element(el_a.element_type, symbol_size)
    if el_a.element_type in _BUS_TYPES:
        pb = connection_point_toward(el_b, el_a.x, el_a.y, symbol_size)
        if port_index_b >= 0:
            ports_b = connection_ports(el_b, ss)
            if ports_b and port_index_b < len(ports_b):
                pb = ports_b[port_index_b]
        pa = _bus_port_aligned(el_a, pb[0], pb[1])
        if port_index_b < 0:
            pb = connection_point_toward(el_b, pa[0], pa[1], symbol_size)
        return pa, pb
    if el_b.element_type in _BUS_TYPES:
        pa = connection_point_toward(el_a, el_b.x, el_b.y, symbol_size)
        if port_index_a >= 0:
            ports_a = connection_ports(el_a, ss)
            if ports_a and port_index_a < len(ports_a):
                pa = ports_a[port_index_a]
        pb = _bus_port_aligned(el_b, pa[0], pa[1])
        if port_index_a < 0:
            pa = connection_point_toward(el_a, pb[0], pb[1], symbol_size)
        return pa, pb

    ports_a = connection_ports(el_a, ss)
    ports_b = connection_ports(el_b, ss)
    if port_index_a >= 0 and ports_a and port_index_a < len(ports_a):
        pa = ports_a[port_index_a]
        if port_index_b >= 0 and ports_b and port_index_b < len(ports_b):
            return pa, ports_b[port_index_b]
        return pa, nearest_port(el_b, pa[0], pa[1], symbol_size)
    if port_index_b >= 0 and ports_b and port_index_b < len(ports_b):
        pb = ports_b[port_index_b]
        return nearest_port(el_a, pb[0], pb[1], symbol_size), pb

    chain_tol = max(28.0, _gost_mm(8.0, ss))
    vertical_chain = abs(el_a.x - el_b.x) <= chain_tol
    horizontal_chain = abs(el_a.y - el_b.y) <= chain_tol
    if vertical_chain or horizontal_chain:
        return _facing_port_pair(el_a, el_b, ports_a, ports_b)

    align_tol = _gost_mm(2.5, ss)
    best_score = float("inf")
    best_pair = nearest_port_pair(ports_a, ports_b)
    for pa in ports_a:
        for pb in ports_b:
            dx = abs(pa[0] - pb[0])
            dy = abs(pa[1] - pb[1])
            score = (pa[0] - pb[0]) ** 2 + (pa[1] - pb[1]) ** 2
            if dx <= align_tol or dy <= align_tol:
                score *= 0.15
            if score < best_score:
                best_score = score
                best_pair = (pa, pb)
    return best_pair


def nearest_port_index(
    element,
    wx,
    wy,
    symbol_size = None,
):
    ports = connection_ports(element, symbol_size)
    if not ports:
        return -1
    best_i = 0
    best_d = float("inf")
    for i, (px, py) in enumerate(ports):
        d = (px - wx) ** 2 + (py - wy) ** 2
        if d < best_d:
            best_d = d
            best_i = i
    return best_i


def _bus_port_aligned(
    bus, target_x, target_y
):
    p1, p2 = busbar_endpoints(bus)
    if abs(p1[0] - p2[0]) < abs(p1[1] - p2[1]):
        x = (p1[0] + p2[0]) / 2.0
        y_lo, y_hi = min(p1[1], p2[1]), max(p1[1], p2[1])
        y = min(max(target_y, y_lo), y_hi)
        return (x, y)
    y = (p1[1] + p2[1]) / 2.0
    x_lo, x_hi = min(p1[0], p2[0]), max(p1[0], p2[0])
    x = min(max(target_x, x_lo), x_hi)
    return (x, y)


def _link_axis_unit(el_a, el_b):
    dx = float(el_b.x) - float(el_a.x)
    dy = float(el_b.y) - float(el_a.y)
    if abs(dy) >= abs(dx):
        if abs(dy) < 1e-6:
            return (0.0, 1.0)
        return (0.0, 1.0 if dy > 0 else -1.0)
    if abs(dx) < 1e-6:
        return (1.0, 0.0)
    return (1.0 if dx > 0 else -1.0, 0.0)


def _element_span_along_chain_axis(
    element,
    *,
    vertical_chain,
    symbol_size = None,
):
    x1, y1, x2, y2 = symbol_bounds(element, symbol_size=symbol_size)
    if vertical_chain:
        return float(min(y1, y2)), float(max(y1, y2))
    return float(min(x1, x2)), float(max(x1, x2))


def _axis_clearance_segment(
    el_a,
    el_b,
    symbol_size = None,
):
    chain_tol = max(20.0, _gost_mm(5.0, symbol_size))
    ax, ay = float(el_a.x), float(el_a.y)
    bx, by = float(el_b.x), float(el_b.y)
    if abs(ax - bx) <= chain_tol and abs(ay - by) > chain_tol:
        if ay <= by:
            upper, lower = el_a, el_b
        else:
            upper, lower = el_b, el_a
        _, u_hi = _element_span_along_chain_axis(
            upper, vertical_chain=True, symbol_size=symbol_size
        )
        l_lo, _ = _element_span_along_chain_axis(
            lower, vertical_chain=True, symbol_size=symbol_size
        )
        if l_lo - u_hi < _gost_mm(0.4, symbol_size):
            return None
        cx = (ax + bx) / 2.0
        return (cx, u_hi), (cx, l_lo)
    if abs(ay - by) <= chain_tol and abs(ax - bx) > chain_tol:
        if ax <= bx:
            left, right = el_a, el_b
        else:
            left, right = el_b, el_a
        _, l_hi = _element_span_along_chain_axis(
            left, vertical_chain=False, symbol_size=symbol_size
        )
        r_lo, _ = _element_span_along_chain_axis(
            right, vertical_chain=False, symbol_size=symbol_size
        )
        if r_lo - l_hi < _gost_mm(0.4, symbol_size):
            return None
        cy = (ay + by) / 2.0
        return (l_hi, cy), (r_lo, cy)
    return None


def mv_withdrawable_contact_gaps(
    element, symbol_size = None
):
    if not uses_mv_withdrawable_symbol(element):
        return []
    lay = _mv_breaker_layout(symbol_size)
    bh = lay["body_half"]
    axis = lay["axis_half"]
    depth = lay["chev_depth"]
    clear = _gost_mm(MV_CONTACT_BODY_CLEAR_MM, symbol_size)
    cx, cy = float(element.x), float(element.y)
    rot = _element_rotation(element)
    gaps = []
    if _link_is_vertical(rot):
        for body_edge, conn_edge in (
            (cy - bh, cy - axis),
            (cy + bh, cy + axis),
        ):
            tips = _mv_stub_chevron_tips(
                body_edge, conn_edge, depth, count=2, body_clear=clear
            )
            if len(tips) >= 2:
                gaps.append((min(tips), max(tips)))
    else:
        for body_edge, conn_edge in (
            (cx - bh, cx - axis),
            (cx + bh, cx + axis),
        ):
            tips = _mv_stub_chevron_tips(
                body_edge, conn_edge, depth, count=2, body_clear=clear
            )
            if len(tips) >= 2:
                gaps.append((min(tips), max(tips)))
    return gaps


def _point_in_mv_contact_gap(
    element,
    px,
    py,
    symbol_size = None,
):
    gaps = mv_withdrawable_contact_gaps(element, symbol_size)
    if not gaps:
        return False
    rot = _element_rotation(element)
    coord = float(py) if _link_is_vertical(rot) else float(px)
    axis_fixed = float(element.x) if _link_is_vertical(rot) else float(element.y)
    other = float(px) if _link_is_vertical(rot) else float(py)
    if abs(other - axis_fixed) > _gost_mm(1.2, symbol_size):
        return False
    for lo, hi in gaps:
        if lo - 0.3 <= coord <= hi + 0.3:
            return True
    return False


def _pull_point_out_of_mv_gap(
    element,
    px,
    py,
    toward_x,
    toward_y,
    symbol_size = None,
):
    if not _point_in_mv_contact_gap(element, px, py, symbol_size):
        return px, py
    port = connection_point_toward(element, toward_x, toward_y, symbol_size)
    return float(port[0]), float(port[1])


def clip_segment_around_mv_contact_gaps(
    el_a,
    el_b,
    x1,
    y1,
    x2,
    y2,
    symbol_size = None,
):
    segs = [((x1, y1), (x2, y2))]
    for el in (el_a, el_b):
        if not uses_mv_withdrawable_symbol(el):
            continue
        gaps = mv_withdrawable_contact_gaps(el, symbol_size)
        if not gaps:
            continue
        vertical = _link_is_vertical(_element_rotation(el))
        axis = float(el.x) if vertical else float(el.y)
        tol = _gost_mm(1.2, symbol_size)
        next_segs = []
        for (ax, ay), (bx, by) in segs:
            if vertical:
                if abs(ax - axis) > tol or abs(bx - axis) > tol:
                    next_segs.append(((ax, ay), (bx, by)))
                    continue
                c0, c1 = (ay, by) if ay <= by else (by, ay)
                pieces = [(c0, c1)]
                for glo, ghi in gaps:
                    rebuilt = []
                    for p0, p1 in pieces:
                        if p1 <= glo or p0 >= ghi:
                            rebuilt.append((p0, p1))
                            continue
                        if p0 < glo:
                            rebuilt.append((p0, glo))
                        if p1 > ghi:
                            rebuilt.append((ghi, p1))
                    pieces = rebuilt
                for p0, p1 in pieces:
                    if abs(p1 - p0) < 0.4:
                        continue
                    if ay <= by:
                        next_segs.append(((axis, p0), (axis, p1)))
                    else:
                        next_segs.append(((axis, p1), (axis, p0)))
            else:
                if abs(ay - axis) > tol or abs(by - axis) > tol:
                    next_segs.append(((ax, ay), (bx, by)))
                    continue
                c0, c1 = (ax, bx) if ax <= bx else (bx, ax)
                pieces = [(c0, c1)]
                for glo, ghi in gaps:
                    rebuilt = []
                    for p0, p1 in pieces:
                        if p1 <= glo or p0 >= ghi:
                            rebuilt.append((p0, p1))
                            continue
                        if p0 < glo:
                            rebuilt.append((p0, glo))
                        if p1 > ghi:
                            rebuilt.append((ghi, p1))
                    pieces = rebuilt
                for p0, p1 in pieces:
                    if abs(p1 - p0) < 0.4:
                        continue
                    if ax <= bx:
                        next_segs.append(((p0, axis), (p1, axis)))
                    else:
                        next_segs.append(((p1, axis), (p0, axis)))
        segs = next_segs
    return segs


def link_draw_endpoints(
    el_a,
    el_b,
    symbol_size = None,
    *,
    port_index_a = -1,
    port_index_b = -1,
):
    p1, p2 = best_connection_points(
        el_a,
        el_b,
        symbol_size,
        port_index_a=port_index_a,
        port_index_b=port_index_b,
    )
    p1 = _pull_point_out_of_mv_gap(el_a, p1[0], p1[1], p2[0], p2[1], symbol_size)
    p1 = _pull_point_out_of_mv_gap(el_b, p1[0], p1[1], p2[0], p2[1], symbol_size)
    p2 = _pull_point_out_of_mv_gap(el_b, p2[0], p2[1], p1[0], p1[1], symbol_size)
    p2 = _pull_point_out_of_mv_gap(el_a, p2[0], p2[1], p1[0], p1[1], symbol_size)

    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    dist = math.hypot(dx, dy)
    min_dist = _gost_mm(LINK_MIN_DRAW_MM, symbol_size)

    if dist >= min_dist:
        return p1, p2

    gap = _axis_clearance_segment(el_a, el_b, symbol_size)
    if gap is not None:
        g1, g2 = gap
        if math.hypot(g2[0] - g1[0], g2[1] - g1[1]) >= min_dist * 0.5:
            return g1, g2

    if _ports_coincide(p1, p2, symbol_size):
        joint = ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0)
        if el_a.element_type in _BUS_TYPES:
            return _bus_coincident_link_stub(el_a, el_b, joint, symbol_size)
        if el_b.element_type in _BUS_TYPES:
            inner, at_joint = _bus_coincident_link_stub(el_b, el_a, joint, symbol_size)
            return at_joint, inner

    return p1, p2


def link_orthogonal_world_segments(
    x1,
    y1,
    x2,
    y2,
    *,
    align_snap = 0.0,
    prefer_vertical_first = False,
    route_style = "auto",
):
    from ugo_model import (
        ROUTE_STYLE_AUTO,
        ROUTE_STYLE_HV,
        ROUTE_STYLE_VH,
        normalize_route_style,
    )

    style = normalize_route_style(route_style)
    x1, y1, x2, y2 = _snap_collinear(x1, y1, x2, y2, align_snap)
    dx = abs(x1 - x2)
    dy = abs(y1 - y2)
    if style == ROUTE_STYLE_AUTO and not prefer_vertical_first:
        if dy > 1e-6 and dx <= max(align_snap, dy * 0.35):
            x2 = x1
        elif dx > 1e-6 and dy <= max(align_snap, dx * 0.35):
            y2 = y1
    tol = max(0.35, align_snap * 0.05 if align_snap else 0.35)
    if abs(x1 - x2) < tol and abs(y1 - y2) < tol:
        return []
    if abs(x1 - x2) < tol or abs(y1 - y2) < tol:
        return [((x1, y1), (x2, y2))]
    if style == ROUTE_STYLE_VH or (
        style == ROUTE_STYLE_AUTO
        and (prefer_vertical_first or abs(x1 - x2) < abs(y1 - y2))
    ):
        mid = (x1, y2)
        return [((x1, y1), mid), (mid, (x2, y2))]
    if style == ROUTE_STYLE_HV:
        mid = (x2, y1)
        return [((x1, y1), mid), (mid, (x2, y2))]
    mid = (x2, y1)
    return [((x1, y1), mid), (mid, (x2, y2))]


def _segments_cross_hv(
    a0,
    a1,
    b0,
    b1,
):
    ax0, ay0 = a0
    ax1, ay1 = a1
    bx0, by0 = b0
    bx1, by1 = b1
    a_horiz = abs(ay0 - ay1) <= 1e-6 and abs(ax0 - ax1) > 1e-6
    a_vert = abs(ax0 - ax1) <= 1e-6 and abs(ay0 - ay1) > 1e-6
    b_horiz = abs(by0 - by1) <= 1e-6 and abs(bx0 - bx1) > 1e-6
    b_vert = abs(bx0 - bx1) <= 1e-6 and abs(by0 - by1) > 1e-6
    if a_horiz and b_vert:
        y, x = ay0, bx0
        if min(ax0, ax1) + 1.0 < x < max(ax0, ax1) - 1.0 and min(by0, by1) + 1.0 < y < max(by0, by1) - 1.0:
            return x, y
    if a_vert and b_horiz:
        x, y = ax0, by0
        if min(bx0, bx1) + 1.0 < x < max(bx0, bx1) - 1.0 and min(ay0, ay1) + 1.0 < y < max(ay0, ay1) - 1.0:
            return x, y
    return None


def draw_link_crossing_bridges(
    canvas,
    segments,
    *,
    width = 2,
    color = COLOR,
    tags=(),
    bridge_radius = None,
):
    r = float(bridge_radius if bridge_radius is not None else _gost_mm(0.9))
    stroke = max(1, int(width))
    try:
        bg = str(canvas.cget("background") or "#ffffff")
    except Exception:
        bg = "#ffffff"
    seen = set()
    n = len(segments)
    for i in range(n):
        id_a, a0, a1 = segments[i]
        for j in range(i + 1, n):
            id_b, b0, b1 = segments[j]
            if id_a == id_b:
                continue
            hit = _segments_cross_hv(a0, a1, b0, b1)
            if hit is None:
                continue
            cx, cy = hit
            key = (round(cx), round(cy))
            if key in seen:
                continue
            seen.add(key)
            sx, sy = _map_xy(cx, cy)
            sr = max(1.5, abs(_map_xy(cx + r, cy)[0] - sx))
            mask_w = stroke + 1
            gap = max(stroke * 0.5 + 0.5, 1.0)
            if sx - sr < sx - gap:
                canvas.create_line(
                    sx - sr, sy, sx - gap, sy, fill=bg, width=mask_w, tags=tags
                )
            if sx + gap < sx + sr:
                canvas.create_line(
                    sx + gap, sy, sx + sr, sy, fill=bg, width=mask_w, tags=tags
                )
            canvas.create_arc(
                sx - sr,
                sy - sr,
                sx + sr,
                sy + sr,
                start=0,
                extent=180,
                style=tk.ARC,
                outline=color,
                width=stroke,
                tags=tags,
            )


def draw_link_line(
    canvas,
    x1,
    y1,
    x2,
    y2,
    tags,
    width = 2,
    color = COLOR,
    *,
    exit1 = None,
    exit2 = None,
    align_snap = 0.0,
    link_stub = None,
    prefer_vertical_first = False,
    route_style = "auto",
):
    del exit1, exit2, link_stub
    world_segs = link_orthogonal_world_segments(
        x1,
        y1,
        x2,
        y2,
        align_snap=align_snap,
        prefer_vertical_first=prefer_vertical_first,
        route_style=route_style,
    )
    if not world_segs:
        return []
    kw = dict(fill=color, width=width, tags=tags, capstyle=tk.BUTT, joinstyle=tk.MITER)
    for (ax, ay), (bx, by) in world_segs:
        sx1, sy1 = _map_xy(ax, ay)
        sx2, sy2 = _map_xy(bx, by)
        canvas.create_line(sx1, sy1, sx2, sy2, **kw)
    return world_segs


def draw_element_symbol(
    canvas,
    element,
    sym_tag,
    anno_tag,
    symbol_size = None,
):
    t = _visual_element_type(element)
    if t == "Узел" and is_routing_bend_node(element):
        return
    x, y = element.x, element.y
    rot = _element_rotation(element)
    ss = symbol_size_for_element(t, symbol_size)
    sym_tags = (sym_tag,)
    anno_tags = (anno_tag,)
    linked = active_link_sides(element, ss)

    _LINKED_DRAWERS = frozenset(
        {
            draw_external_grid,
            draw_generator,
            draw_gpu,
            draw_transformer_2w,
            draw_transformer_split_2w,
            draw_transformer_3w,
            draw_mv_withdrawable_breaker,
        }
    )
    drawers = {
        "Внешняя энергосистема": draw_external_grid,
        "Генератор": draw_generator,
        "ГПУ": draw_gpu,
        "Трансформатор 2-обм.": draw_transformer_2w,
        "Трансформатор 2-обм. расщепл.": draw_transformer_split_2w,
        "Трансформатор": draw_transformer_2w,
        "Трансформатор 3-обм.": draw_transformer_3w,
        "ВЛ": draw_overhead_line,
        "КЛ": draw_cable_line,
        "Кабельная линия 0,4 кВ": draw_cable_line,
        "Выключатель": draw_circuit_breaker,
        "АВ 220 В": draw_lv_breaker_220,
        "АВ 380 В": draw_lv_breaker,
        "Автоматический выключатель 0,4 кВ": draw_lv_breaker,
        "Автоматический выключатель 1P": draw_lv_breaker,
        "Автоматический выключатель 2P": draw_lv_breaker,
        "Автоматический выключатель 3P": draw_lv_breaker,
        "Автоматический выключатель 4P": draw_lv_breaker,
        "Секционный автоматический выключатель": draw_lv_breaker,
        "Выключатель нагрузки": draw_lv_switchgear_contact,
        "Рубильник": draw_lv_switchgear_contact,
        "Контактор": draw_contactor,
        "УЗО": draw_lv_breaker,
        "Дифференциальный автомат": draw_lv_breaker,
        "Выключатель 6(10) кВ": draw_mv_withdrawable_breaker,
        "Выключатель 6/10 кВ с выкатным элементом": draw_mv_withdrawable_breaker,
        "Секция шин": draw_busbar,
        "Фазная шина": draw_phase_bus,
        "Шина N": draw_neutral_bus,
        "Шина PE": draw_pe_bus,
        "Шина PEN": draw_pen_bus,
        "Нагрузка": draw_load,
        "Нагрузка 0,4 кВ": draw_lv_load,
        "ГРЩ": draw_panel,
        "ЩСУ": draw_panel,
        "ЩО": draw_panel,
        "ШР": draw_panel,
        "Узел": draw_node,
    }
    drawer = drawers.get(t)
    if drawer in (draw_busbar, draw_phase_bus, draw_neutral_bus, draw_pe_bus, draw_pen_bus):
        drawer(
            canvas,
            x,
            y,
            sym_tags,
            anno_tags,
            ss,
            rotation=rot,
            busbar_left_extent=element.busbar_left_extent,
            busbar_right_extent=element.busbar_right_extent,
        )
    elif drawer in (draw_overhead_line, draw_cable_line):
        ea, eb = _line_extents(element, ss)
        if drawer is draw_cable_line:
            drawer(
                canvas,
                x,
                y,
                sym_tags,
                anno_tags,
                ss,
                rotation=rot,
                line_extent_a=ea,
                line_extent_b=eb,
                cable_seal_mode=str(
                    getattr(element, "cable_seal_mode", "both") or "both"
                ),
            )
        else:
            drawer(
                canvas,
                x,
                y,
                sym_tags,
                anno_tags,
                ss,
                rotation=rot,
                line_extent_a=ea,
                line_extent_b=eb,
            )
    elif t == "Выключатель" and uses_mv_withdrawable_symbol(element):
        draw_mv_withdrawable_breaker(
            canvas,
            x,
            y,
            sym_tags,
            anno_tags,
            ss,
            rotation=rot,
            linked=linked,
            closed=bool(getattr(element, "closed", True)),
        )
    elif t == "Выключатель":
        draw_circuit_breaker(
            canvas,
            x,
            y,
            sym_tags,
            anno_tags,
            ss,
            rotation=rot,
            linked=linked,
            closed=bool(getattr(element, "closed", True)),
        )
    elif drawer in (draw_lv_breaker, draw_lv_breaker_220):
        poles = av_pole_count_for_element(element)
        draw_automatic_breaker(
            canvas,
            x,
            y,
            sym_tags,
            anno_tags,
            ss,
            rotation=rot,
            pole_count=poles,
            linked=linked,
            closed=bool(getattr(element, "closed", True)),
        )
    elif drawer in (draw_lv_switchgear_contact, draw_contactor):
        drawer(canvas, x, y, sym_tags, anno_tags, ss, rotation=rot, linked=linked)
    elif t in _PANEL_TYPES:
        drawer(canvas, x, y, sym_tags, anno_tags, ss, rotation=rot, label=t)
    elif drawer is draw_mv_withdrawable_breaker:
        drawer(
            canvas,
            x,
            y,
            sym_tags,
            anno_tags,
            ss,
            rotation=rot,
            linked=linked,
            closed=bool(getattr(element, "closed", True)),
        )
    elif drawer in _LINKED_DRAWERS:
        drawer(canvas, x, y, sym_tags, anno_tags, ss, rotation=rot, linked=linked)
    elif drawer:
        drawer(canvas, x, y, sym_tags, anno_tags, ss, rotation=rot)
    else:
        draw_node(canvas, x, y, sym_tags, anno_tags, ss, rotation=rot)


def line_endpoints(element):
    cx, cy = element.x, element.y
    rot = _norm_rotation(element.rotation)
    ea, eb = _line_extents(element)
    a = rot_point(cx, cy, cx - ea, cy, rot)
    b = rot_point(cx, cy, cx + eb, cy, rot)
    return a, b


def apply_line_resize(
    element,
    moving_side,
    fixed_world,
    cursor_world,
    min_extent = 10.0,
):
    fx, fy = fixed_world
    mx, my = cursor_world
    rot = _norm_rotation(element.rotation)

    if rot in (0, 180):
        mov_x = mx
        if moving_side == "a":
            end_x, fixed_x = mov_x, fx
        else:
            fixed_x, end_x = fx, mov_x
        if end_x > fixed_x:
            end_x, fixed_x = fixed_x, end_x
        if fixed_x - end_x < min_extent * 2:
            end_x = fixed_x - min_extent * 2
        element.x = (end_x + fixed_x) / 2
        element.line_extent_a = element.x - end_x
        element.line_extent_b = fixed_x - element.x
    else:
        mov_y = my
        if moving_side == "a":
            end_y, fixed_y = mov_y, fy
        else:
            fixed_y, end_y = fy, mov_y
        if end_y > fixed_y:
            end_y, fixed_y = fixed_y, end_y
        if fixed_y - end_y < min_extent * 2:
            end_y = fixed_y - min_extent * 2
        element.y = (end_y + fixed_y) / 2
        element.line_extent_a = element.y - end_y
        element.line_extent_b = fixed_y - element.y


def busbar_endpoints(element):
    cx, cy = element.x, element.y
    rot = _norm_rotation(element.rotation)
    left = rot_point(cx, cy, cx - element.busbar_left_extent, cy, rot)
    right = rot_point(cx, cy, cx + element.busbar_right_extent, cy, rot)
    return left, right


def apply_busbar_resize(
    element,
    moving_side,
    fixed_world,
    cursor_world,
    min_extent = 12.0,
):
    fx, fy = fixed_world
    mx, my = cursor_world
    rot = _norm_rotation(element.rotation)

    if rot in (0, 180):
        mov_x = mx
        if moving_side == "left":
            end_x, fixed_x = mov_x, fx
        else:
            fixed_x, end_x = fx, mov_x
        if end_x > fixed_x:
            end_x, fixed_x = fixed_x, end_x
        if fixed_x - end_x < min_extent * 2:
            end_x = fixed_x - min_extent * 2
        element.x = (end_x + fixed_x) / 2
        element.y = element.y
        element.busbar_left_extent = element.x - end_x
        element.busbar_right_extent = fixed_x - element.x
    else:
        mov_y = my
        if moving_side == "left":
            end_y, fixed_y = mov_y, fy
        else:
            fixed_y, end_y = fy, mov_y
        if end_y > fixed_y:
            end_y, fixed_y = fixed_y, end_y
        if fixed_y - end_y < min_extent * 2:
            end_y = fixed_y - min_extent * 2
        element.x = element.x
        element.y = (end_y + fixed_y) / 2
        element.busbar_left_extent = element.y - end_y
        element.busbar_right_extent = fixed_y - element.y
