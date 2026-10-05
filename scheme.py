import tkinter as tk
import math

import symbols
from ui_theme import LIGHT

GRID = 20
MARGIN = 36


class Elem:
    def __init__(self, eid, kind, x, y):
        self.id = eid
        self.kind = kind
        self.x = float(x)
        self.y = float(y)
        self.rot = 90 if kind == "Трансформатор 3-обм." else 0
        self.name = ""
        self.busbar_left_extent = 70.0
        self.busbar_right_extent = 70.0
        self.closed = True
        self.line_extent_a = 0.0
        self.line_extent_b = 0.0
        self.cable_seal_mode = "both"
        self.u_nom_kv = 0.0
        self.pole_count = 0
        self.catalog_model = ""

    @property
    def element_type(self):
        return self.kind

    @property
    def rotation(self):
        return self.rot

    @rotation.setter
    def rotation(self, value):
        self.rot = int(value) % 360


class Wire:
    def __init__(self, a, b):
        self.a = a
        self.b = b


class SchemeView(tk.Canvas):
    def __init__(self, master, on_select, on_status, on_change=None, on_context=None):
        super().__init__(
            master,
            bg=LIGHT["canvas"],
            highlightthickness=0,
            xscrollincrement=1,
            yscrollincrement=1,
        )
        self.on_select = on_select
        self.on_status = on_status
        self.on_change = on_change or (lambda: None)
        self.on_context = on_context
        self.colors = LIGHT
        self.items = []
        self.wires = []
        self._seq = 1
        self.tool = None
        self.connecting = False
        self._from = None
        self.selected = None
        self.selected_ids = set()
        self.show_grid = True
        self.zoom = 1.0
        # The diagram uses the same bounded, zoomable sheet model as the plan.
        # Coordinates remain in the legacy 800×600 scheme space.
        self.sheet_width = 800.0
        self.sheet_height = 600.0
        self.ppm = 1.0
        self.view_mode = "manual"
        self._origin_x = MARGIN
        self._origin_y = MARGIN
        self._drag = None
        self._marquee = None
        self.bind("<Button-1>", self._down)
        self.bind("<B1-Motion>", self._move)
        self.bind("<ButtonRelease-1>", self._up)
        self.bind("<Motion>", self._preview)
        self.bind("<Button-3>", self._context)
        self.bind("<MouseWheel>", self._wheel)
        self.bind("<Button-4>", lambda e: self._zoom_at(e, 1.1))
        self.bind("<Button-5>", lambda e: self._zoom_at(e, 0.9))
        self.bind("<Button-2>", self._pan_start)
        self.bind("<B2-Motion>", self._pan_move)
        self.bind("<ButtonRelease-2>", self._pan_end)
        self.bind("<Configure>", self._enforce_zoom)

    def set_theme(self, colors):
        self.colors = colors
        self.configure(bg=colors["canvas"])
        symbols.COLOR = colors["text"]
        symbols.SELECTION_COLOR = colors["selection"]
        symbols.HANDLE_COLOR = colors["selection"]
        self.redraw()

    def _fit_zoom(self):
        return self._fit_scale() / self.ppm

    def _fit_scale(self):
        return max(100, self.winfo_width()) * 0.25 / self.sheet_width

    def _scale(self):
        return self.ppm * self.zoom

    def _sheet_bounds(self):
        scale = self._fit_scale()
        width, height = max(100, self.winfo_width()), max(100, self.winfo_height())
        cx, cy = self.sheet_width / 2, self.sheet_height / 2
        return cx - width / (2 * scale), cy - height / (2 * scale), cx + width / (2 * scale), cy + height / (2 * scale)

    def _center_origin(self):
        s = self._scale()
        self._origin_x = self.canvasx(self.winfo_width() / 2) - self.sheet_width / 2 * s
        self._origin_y = self.canvasy(self.winfo_height() / 2) - self.sheet_height / 2 * s

    def _to_screen(self, x, y):
        s = self._scale()
        return self._origin_x + x * s, self._origin_y + y * s

    def _to_world(self, event):
        s = self._scale()
        return (self.canvasx(event.x) - self._origin_x) / s, (self.canvasy(event.y) - self._origin_y) / s

    def fit_sheet(self):
        self.view_mode = "fit"
        self.zoom = self._fit_zoom()
        self.xview_moveto(0)
        self.yview_moveto(0)
        self._center_origin()
        self.redraw()

    def zoom_one_to_one(self):
        self.view_mode = "one"
        self.zoom = self._one_to_one_zoom()
        self.xview_moveto(0)
        self.yview_moveto(0)
        self._center_origin()
        self.redraw()

    def _enforce_zoom(self, _event=None):
        minimum = self._fit_zoom()
        if self.view_mode == "fit":
            self.fit_sheet()
        elif self.view_mode == "one":
            self.zoom_one_to_one()
        elif self.zoom < minimum:
            self.zoom = minimum
            self.redraw()

    def _pan_start(self, event):
        if self.view_mode == "fit":
            return
        self.view_mode = "manual"
        self.configure(cursor="fleur")
        self.scan_mark(event.x, event.y)
        self.on_status("Панорамирование: перемещайте поле, удерживая среднюю кнопку мыши")

    def _pan_move(self, event):
        self.scan_dragto(event.x, event.y, gain=1)

    def _pan_end(self, _event):
        self.configure(cursor="")
        self.on_status("Готово")

    def set_tool(self, kind):
        self.tool = kind
        self.connecting = False
        self._from = None
        if kind:
            self.on_status("Клик по полю — поставить «%s»" % kind)

    def set_connect(self, on):
        self.connecting = on
        self._from = None
        if on:
            self.tool = None
            self.on_status("Соединение: укажите два элемента")

    def clear(self):
        self.items.clear()
        self.wires.clear()
        self._seq = 1
        self.selected = None
        self.selected_ids.clear()
        self._from = None
        self.redraw()
        self.on_select(None)

    def dump(self):
        return {
            "items": [
                {"id": it.id, "kind": it.kind, "x": it.x, "y": it.y, "rot": it.rot, "name": it.name}
                for it in self.items
            ],
            "wires": [{"a": w.a, "b": w.b} for w in self.wires],
        }

    def load(self, data):
        self.items.clear()
        self.wires.clear()
        for raw in data.get("items", []):
            it = Elem(int(raw["id"]), raw["kind"], raw["x"], raw["y"])
            it.rot = int(raw.get("rot") or 0)
            it.name = raw.get("name") or ""
            self.items.append(it)
        for raw in data.get("wires", []):
            self.wires.append(Wire(int(raw["a"]), int(raw["b"])))
        self._seq = 1 + max([it.id for it in self.items], default=0)
        self.selected = None
        self.selected_ids.clear()
        self.redraw()
        self.on_select(None)

    def current(self):
        for it in self.items:
            if it.id == self.selected:
                return it
        return None

    def rotate_selected(self):
        it = self.current()
        if not it:
            return
        it.rot = (it.rot + 90) % 360
        self.redraw()

    def delete_selected(self):
        if not self.selected_ids:
            return
        self.items = [it for it in self.items if it.id not in self.selected_ids]
        self.wires = [w for w in self.wires if w.a not in self.selected_ids and w.b not in self.selected_ids]
        self.selected = None
        self.selected_ids.clear()
        self._from = None
        self.redraw()
        self.on_select(None)

    def rename(self, text):
        it = self.current()
        if not it:
            return
        it.name = text
        self.redraw()

    def _find(self, x, y):
        return symbols.hit_test_element(self.items, x, y)

    def _down(self, event):
        self.focus_set()
        x, y = self._to_world(event)
        hit = self._find(x, y)
        self._drag = None
        if self.connecting:
            self._pick_connect(hit)
            return
        if hit:
            additive = bool(event.state & 0x0004)
            if additive:
                if hit.id in self.selected_ids:
                    self.selected_ids.remove(hit.id)
                    self.selected = next(iter(self.selected_ids), None)
                else:
                    self.selected_ids.add(hit.id)
                    self.selected = hit.id
            elif hit.id not in self.selected_ids:
                self.selected_ids = {hit.id}
                self.selected = hit.id
            if self.selected_ids:
                origin = {it.id: (it.x, it.y) for it in self.items if it.id in self.selected_ids}
                self._drag = (x, y, origin)
                self.on_select(self.current())
            else:
                self.on_select(None)
            self.redraw()
            return
        if self.tool:
            wx, wy = self._clamp_world(x, y)
            it = Elem(self._seq, self.tool, wx, wy)
            self._seq += 1
            self.items.append(it)
            self.selected = it.id
            self.selected_ids = {it.id}
            self.on_select(it)
            self.on_change()
            self.redraw()
            return
        self._marquee = (x, y, bool(event.state & 0x0004))
        sx, sy = self._to_screen(x, y)
        self.create_rectangle(sx, sy, sx, sy, outline=self.colors["selection"], dash=(3, 2), tags="marquee")
        return
        self.selected = None
        self.selected_ids.clear()
        self.on_select(None)
        self.redraw()

    def _pick_connect(self, hit):
        if hit is None:
            return
        if self._from is None:
            self._from = hit.id
            self.selected = hit.id
            self.selected_ids = {hit.id}
            self.on_status("Укажите второй элемент")
            self.redraw()
            return
        if hit.id == self._from:
            return
        pair = (self._from, hit.id)
        if not any((w.a, w.b) == pair or (w.b, w.a) == pair for w in self.wires):
            self.wires.append(Wire(*pair))
        self.selected = hit.id
        self.selected_ids = {hit.id}
        self._from = None
        self.on_status("Элементы соединены")
        self.on_select(hit)
        self.on_change()
        self.redraw()

    def _move(self, event):
        if self._marquee:
            x0, y0, _ = self._marquee
            sx, sy = self._to_screen(x0, y0)
            self.coords("marquee", sx, sy, self.canvasx(event.x), self.canvasy(event.y))
            return
        if not self._drag:
            return
        x, y = self._to_world(event)
        start_x, start_y, origin = self._drag
        dx, dy = x - start_x, y - start_y
        for eid, (old_x, old_y) in origin.items():
            item = self._by_id(eid)
            if item:
                item.x, item.y = self._clamp_world(old_x + dx, old_y + dy)
        self.redraw()

    def _up(self, event):
        if self._marquee:
            x0, y0, additive = self._marquee
            x1, y1 = self._to_world(event)
            left, right = sorted((x0, x1))
            top, bottom = sorted((y0, y1))
            picked = {it.id for it in self.items if left <= it.x <= right and top <= it.y <= bottom}
            if additive:
                self.selected_ids |= picked
            else:
                self.selected_ids = picked
            self.selected = next(iter(self.selected_ids), None)
            self._marquee = None
            self.redraw()
            self.on_select(self.current())
            return
        changed = self._drag is not None
        self._drag = None
        if changed:
            self.on_change()

    def _preview(self, event):
        self.delete("preview")
        if not self.tool:
            return
        x, y = self._to_world(event)
        sx, sy = self._to_screen(x, y)
        self.create_oval(sx - 10, sy - 10, sx + 10, sy + 10, outline=self.colors["selection"], dash=(2, 2), tags="preview")

    def _context(self, event):
        hit = self._find(*self._to_world(event))
        if hit:
            self.selected = hit.id
            self.selected_ids = {hit.id}
            self.on_select(hit)
            self.redraw()
        if self.on_context:
            self.on_context(hit, event.x_root, event.y_root, "scheme")

    def _wheel(self, event):
        factor = 1.1 if event.delta > 0 else 0.9
        self._zoom_at(event, factor)

    def _zoom_at(self, event, factor):
        anchor_world = self._to_world(event)
        self.view_mode = "manual"
        self.zoom = min(4.0, max(self._fit_zoom(), self.zoom * factor))
        self.redraw()
        if self.zoom > self._fit_zoom() + 0.001:
            self._keep_world_at_pointer(anchor_world, event.x, event.y)

    def _keep_world_at_pointer(self, world, pointer_x, pointer_y):
        """Scroll so the world point beneath the pointer remains stationary."""
        sx, sy = self._to_screen(*world)
        region = tuple(float(value) for value in str(self.cget("scrollregion")).split())
        if len(region) != 4:
            return
        x1, y1, x2, y2 = region
        width, height = max(1.0, x2 - x1), max(1.0, y2 - y1)
        desired_left = min(max(x1, sx - pointer_x), max(x1, x2 - self.winfo_width()))
        desired_top = min(max(y1, sy - pointer_y), max(y1, y2 - self.winfo_height()))
        self.xview_moveto((desired_left - x1) / width)
        self.yview_moveto((desired_top - y1) / height)

    def zoom_reset(self):
        self.zoom_one_to_one()

    def _one_to_one_zoom(self):
        width, height = max(100, self.winfo_width()), max(100, self.winfo_height())
        return min(4.0, min(width / (self.sheet_width + 50), height / (self.sheet_height + 50)) / self.ppm)

    def _label_font_size(self):
        reference = max(0.001, self._one_to_one_zoom())
        relative_zoom = max(0.001, self.zoom / reference)
        return max(9, min(15, round(11 * math.sqrt(relative_zoom))))

    def _clamp_world(self, x, y):
        x1, y1, x2, y2 = self._sheet_bounds()
        return min(max(x1, x), x2), min(max(y1, y), y2)

    def redraw(self):
        self.delete("all")
        z = self._scale()
        px1, py1, px2, py2 = self._sheet_bounds()
        page_x1, page_y1 = self._to_screen(px1, py1)
        page_x2, page_y2 = self._to_screen(px2, py2)
        x1, y1 = self._to_screen(0, 0)
        x2, y2 = self._to_screen(self.sheet_width, self.sheet_height)
        self.configure(scrollregion=(page_x1, page_y1, page_x2, page_y2))
        if self.show_grid:
            self._draw_grid()
        self.create_rectangle(page_x1, page_y1, page_x2, page_y2, outline=self.colors["border"], width=1)
        self.create_rectangle(x1, y1, x2, y2, outline=self.colors["muted"], width=1)
        symbols.set_view_scale(z)
        symbols.set_draw_coord_transform(self._to_screen)
        symbols.set_connection_project(_Sheet(self.items, self.wires))
        try:
            bridges = []
            for wire in self.wires:
                bridges.extend(self._draw_wire(wire))
            for it in self.items:
                symbols.draw_element_symbol(self, it, "el%s" % it.id, "ann%s" % it.id)
                self._mark(it, z)
            if bridges:
                symbols.draw_link_crossing_bridges(
                    self, bridges, width=max(1, int(round(2 * z))), tags="link_bridge"
                )
        finally:
            symbols.set_view_scale(None)
            symbols.set_draw_coord_transform(None)
            symbols.set_connection_project(None)
        if self.zoom <= self._fit_zoom() + 0.001:
            self.xview_moveto(0)
            self.yview_moveto(0)
        if not self.items:
            self.create_text(
                (x1 + x2) / 2, (y1 + y2) / 2 - 12,
                text="Схема объекта", fill=self.colors["muted"], font=("Arial", 13, "bold"),
            )
            self.create_text(
                (x1 + x2) / 2, (y1 + y2) / 2 + 13,
                text="Выберите элемент в верхней ленте и щёлкните на листе",
                fill=self.colors["muted"], font=("Arial", 9),
            )

    def _mark(self, it, z):
        try:
            x1, y1, x2, y2 = symbols.symbol_bounds(it)
        except Exception:
            x1, y1, x2, y2 = it.x - 20, it.y - 20, it.x + 20, it.y + 20
        if it.name:
            sx, sy = self._to_screen((x1 + x2) / 2, y2)
            self.create_text(
                sx,
                sy + self._label_font_size() + 3,
                text=it.name,
                fill=self.colors["text"],
                font=("Segoe UI", self._label_font_size()),
                anchor=tk.N,
                justify=tk.CENTER,
            )
        if it.id in self.selected_ids or it.id == self._from:
            sx1, sy1 = self._to_screen(x1, y1)
            sx2, sy2 = self._to_screen(x2, y2)
            self.create_rectangle(
                sx1 - 3, sy1 - 3, sx2 + 3, sy2 + 3,
                outline=self.colors["selection"], width=2, dash=(3, 2),
            )

    def _draw_grid(self):
        px1, py1, px2, py2 = self._sheet_bounds()
        page_x1, page_y1 = self._to_screen(px1, py1)
        page_x2, page_y2 = self._to_screen(px2, py2)
        start_x = (int(px1) // GRID) * GRID
        start_y = (int(py1) // GRID) * GRID
        for wx in range(start_x, int(px2) + 1, GRID):
            gx, _ = self._to_screen(wx, 0)
            self.create_line(gx, page_y1, gx, page_y2, fill=self.colors["border"] if wx % (GRID * 5) == 0 else self.colors["grid"], tags="grid")
        for wy in range(start_y, int(py2) + 1, GRID):
            _, gy = self._to_screen(0, wy)
            self.create_line(page_x1, gy, page_x2, gy, fill=self.colors["border"] if wy % (GRID * 5) == 0 else self.colors["grid"], tags="grid")

    def _by_id(self, eid):
        for it in self.items:
            if it.id == eid:
                return it
        return None

    def _draw_wire(self, wire):
        a = self._by_id(wire.a)
        b = self._by_id(wire.b)
        if not a or not b:
            return []
        p1, p2 = symbols.best_connection_points(a, b)
        world = symbols.draw_link_line(
            self, p1[0], p1[1], p2[0], p2[1], "wire",
            width=max(1, int(round(2 * self.zoom))),
        )
        return [(wire.a * 100000 + wire.b, seg[0], seg[1]) for seg in world]


class _Link:
    def __init__(self, a, b):
        self.from_element_id = a
        self.to_element_id = b


class _Sheet:
    def __init__(self, items, wires):
        self.connections = {i: _Link(w.a, w.b) for i, w in enumerate(wires)}
        self._els = {it.id: it for it in items}

    def get_element(self, eid):
        return self._els.get(eid)
