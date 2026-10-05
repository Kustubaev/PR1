import tkinter as tk
import tkinter.font as tkfont
import math

from ui_theme import LIGHT

SELECT = "#2563eb"
MARGIN = 36


class Block:
    def __init__(self, bid, kind, x, y):
        self.id = bid
        self.kind = kind
        self.x = float(x)
        self.y = float(y)
        self.w = 32.0
        self.h = 18.0
        self.name = kind
        self.sheet = {"items": [], "wires": []}
        if kind in ("ГПП", "ТП", "РП", "Энергосистема"):
            self.w, self.h = 16.0, 12.0


class Tie:
    def __init__(self, a, b, kind):
        self.a = a
        self.b = b
        self.kind = kind


FILL = {
    "Энергосистема": "#e2e8f0",
    "Точка подключения ПГ": "#fef3c7",
}
LINE = {
    "КЛ": ("#1d4ed8", ()),
    "ВЛ": ("#b45309", (6, 3)),
    "Газопровод": ("#a16207", (2, 2)),
    "Технологическая связь": ("#64748b", (4, 2)),
    "Прочая связь": ("#94a3b8", (1, 2)),
}


class PlanView(tk.Canvas):
    def __init__(self, master, on_select, on_status, on_open=None, on_change=None, on_context=None):
        super().__init__(master, bg=LIGHT["canvas"], highlightthickness=0)
        self.colors = LIGHT
        self.on_select = on_select
        self.on_status = on_status
        self.on_open = on_open
        self.on_change = on_change or (lambda: None)
        self.on_context = on_context
        self.blocks = []
        self.ties = []
        self._seq = 1
        self.length_m = 200.0
        self.width_m = 150.0
        # At 100% the 200×150 m site is rendered as approximately 800×600 px.
        self.ppm = 4.0
        self.zoom = 1.0
        self.view_mode = "manual"
        self._origin_x = MARGIN
        self._origin_y = MARGIN
        self.show_grid = True
        self.tool = None
        self.link_kind = None
        self._from = None
        self.selected = None
        self.selected_ids = set()
        self._drag = None
        self._marquee = None
        self.bind("<Button-1>", self._down)
        self.bind("<Double-Button-1>", self._double)
        self.bind("<B1-Motion>", self._move)
        self.bind("<ButtonRelease-1>", self._end_drag)
        self.bind("<Motion>", self._preview)
        self.bind("<Button-3>", self._context)
        self.bind("<MouseWheel>", self._wheel)
        self.bind("<Button-4>", lambda e: self._zoom(1.1, e))
        self.bind("<Button-5>", lambda e: self._zoom(0.9, e))
        self.bind("<Button-2>", self._pan_start)
        self.bind("<B2-Motion>", self._pan_move)
        self.bind("<ButtonRelease-2>", self._pan_end)
        self.bind("<Configure>", self._enforce_zoom)

    def set_theme(self, colors):
        self.colors = colors
        self.configure(bg=colors["canvas"])
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

    def _fit_zoom(self):
        return self._fit_scale() / self.ppm

    def _fit_scale(self):
        return max(100, self.winfo_width()) * 0.25 / self.length_m

    def _sheet_bounds(self):
        scale = self._fit_scale()
        width, height = max(100, self.winfo_width()), max(100, self.winfo_height())
        cx, cy = self.length_m / 2, self.width_m / 2
        return cx - width / (2 * scale), cy - height / (2 * scale), cx + width / (2 * scale), cy + height / (2 * scale)

    def _center_origin(self):
        s = self._scale()
        self._origin_x = self.canvasx(self.winfo_width() / 2) - self.length_m / 2 * s
        self._origin_y = self.canvasy(self.winfo_height() / 2) - self.width_m / 2 * s

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

    def set_tool(self, kind):
        self.tool = kind
        self.link_kind = None
        self._from = None
        self.on_status("Клик по плану — поставить «%s»" % kind)

    def set_link(self, kind):
        self.link_kind = kind
        self.tool = None
        self._from = None
        self.on_status("Связь «%s»: укажите два объекта" % kind)

    def clear(self):
        self.blocks.clear()
        self.ties.clear()
        self._seq = 1
        self.selected = None
        self.selected_ids.clear()
        self._from = None
        self.length_m = 200.0
        self.width_m = 150.0
        self.redraw()
        self.on_select(None)

    def dump(self):
        return {
            "length_m": self.length_m,
            "width_m": self.width_m,
            "blocks": [
                {
                    "id": b.id,
                    "kind": b.kind,
                    "x": b.x,
                    "y": b.y,
                    "w": b.w,
                    "h": b.h,
                    "name": b.name,
                    "sheet": b.sheet,
                }
                for b in self.blocks
            ],
            "ties": [{"a": t.a, "b": t.b, "kind": t.kind} for t in self.ties],
        }

    def load(self, data):
        self.blocks.clear()
        self.ties.clear()
        self.length_m = float(data.get("length_m") or 200)
        self.width_m = float(data.get("width_m") or 150)
        for raw in data.get("blocks", []):
            b = Block(int(raw["id"]), raw["kind"], raw["x"], raw["y"])
            b.w = float(raw.get("w") or b.w)
            b.h = float(raw.get("h") or b.h)
            b.name = raw.get("name") or b.kind
            b.sheet = raw.get("sheet") or {"items": [], "wires": []}
            self.blocks.append(b)
        for raw in data.get("ties", []):
            self.ties.append(Tie(int(raw["a"]), int(raw["b"]), raw.get("kind") or "КЛ"))
        self._seq = 1 + max([b.id for b in self.blocks], default=0)
        self.selected = None
        self.selected_ids.clear()
        self.redraw()
        self.on_select(None)

    def current(self):
        for b in self.blocks:
            if b.id == self.selected:
                return b
        return None

    def delete_selected(self):
        if not self.selected_ids:
            return
        self.blocks = [b for b in self.blocks if b.id not in self.selected_ids]
        self.ties = [t for t in self.ties if t.a not in self.selected_ids and t.b not in self.selected_ids]
        self.selected = None
        self.selected_ids.clear()
        self._from = None
        self.redraw()
        self.on_select(None)

    def apply_fields(self, name, w, h, site_l, site_w):
        try:
            site_l = float(str(site_l).replace(",", "."))
            site_w = float(str(site_w).replace(",", "."))
        except ValueError:
            site_l, site_w = self.length_m, self.width_m
        if site_l > 10:
            self.length_m = site_l
        if site_w > 10:
            self.width_m = site_w
        b = self.current()
        if b:
            b.name = name.strip() or b.kind
            try:
                bw = float(str(w).replace(",", "."))
                bh = float(str(h).replace(",", "."))
            except ValueError:
                bw, bh = b.w, b.h
            if bw > 2:
                b.w = bw
            if bh > 2:
                b.h = bh
        self.redraw()

    def block(self, bid):
        for b in self.blocks:
            if b.id == bid:
                return b
        return None

    def add_object(self, kind, name, sheet):
        n = len(self.blocks)
        b = Block(self._seq, kind, 16 + (n % 4) * 42, 16 + (n // 4) * 30)
        b.name = name
        b.sheet = sheet
        self._seq += 1
        self.blocks.append(b)
        self.selected = b.id
        self.selected_ids = {b.id}
        self.redraw()
        self.on_select(b)
        return b

    def zoom_reset(self):
        self.zoom_one_to_one()

    def _one_to_one_zoom(self):
        width, height = max(100, self.winfo_width()), max(100, self.winfo_height())
        scale = min(width / (self.length_m + 50), height / (self.width_m + 50))
        return min(4.0, scale / self.ppm)

    def _label_font_size(self):
        reference = max(0.001, self._one_to_one_zoom())
        relative_zoom = max(0.001, self.zoom / reference)
        return max(9, min(15, round(11 * math.sqrt(relative_zoom))))

    def _fit_label(self, text, width, font_spec):
        value = text or ""
        if width <= 8:
            return ""
        font = tkfont.Font(self, font=font_spec)
        if font.measure(value) <= width:
            return value
        suffix = "…"
        low, high = 0, len(value)
        while low < high:
            middle = (low + high + 1) // 2
            if font.measure(value[:middle] + suffix) <= width:
                low = middle
            else:
                high = middle - 1
        return value[:low].rstrip() + suffix

    def _scale(self):
        return self.ppm * self.zoom

    def _origin(self):
        return self._origin_x, self._origin_y

    def _to_screen(self, x, y):
        s = self._scale()
        ox, oy = self._origin()
        return ox + x * s, oy + y * s

    def _to_world(self, event):
        s = self._scale()
        ox, oy = self._origin()
        x = (self.canvasx(event.x) - ox) / s
        y = (self.canvasy(event.y) - oy) / s
        return x, y

    def _find(self, x, y):
        for b in reversed(self.blocks):
            if b.x <= x <= b.x + b.w and b.y <= y <= b.y + b.h:
                return b
        return None

    def _down(self, event):
        self.focus_set()
        x, y = self._to_world(event)
        hit = self._find(x, y)
        self._drag = None
        if self.link_kind:
            self._pick_link(hit)
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
                origin = {b.id: (b.x, b.y) for b in self.blocks if b.id in self.selected_ids}
                self._drag = (x, y, origin)
                self.on_select(self.current())
            else:
                self.on_select(None)
            self.redraw()
            return
        if self.tool:
            px1, py1, px2, py2 = self._sheet_bounds()
            b = Block(self._seq, self.tool, min(max(px1, x), px2 - 2), min(max(py1, y), py2 - 2))
            self._seq += 1
            self.blocks.append(b)
            self.selected = b.id
            self.selected_ids = {b.id}
            self.on_select(b)
            self.on_change()
            self.redraw()
            return
        if not self.link_kind:
            self._marquee = (x, y, bool(event.state & 0x0004))
            self.create_rectangle(event.x, event.y, event.x, event.y, outline=self.colors["selection"], dash=(3, 2), tags="marquee")
            return
        self.selected = None
        self.selected_ids.clear()
        self.on_select(None)
        self.redraw()

    def _double(self, event):
        if self.link_kind or self.on_open is None:
            return
        hit = self._find(*self._to_world(event))
        if hit is None:
            return
        self._drag = None
        self.selected = hit.id
        self.selected_ids = {hit.id}
        self.on_open(hit)

    def _pick_link(self, hit):
        if hit is None:
            return
        if self._from is None:
            self._from = hit.id
            self.selected = hit.id
            self.selected_ids = {hit.id}
            self.on_status("Укажите второй объект")
            self.redraw()
            return
        if hit.id == self._from:
            return
        self.ties.append(Tie(self._from, hit.id, self.link_kind))
        self.selected = hit.id
        self.selected_ids = {hit.id}
        self._from = None
        self.on_status("Объекты связаны")
        self.on_select(hit)
        self.on_change()
        self.redraw()

    def _move(self, event):
        if self._marquee:
            x0, y0, _ = self._marquee
            sx0, sy0 = self._to_screen(x0, y0)
            self.coords("marquee", sx0, sy0, self.canvasx(event.x), self.canvasy(event.y))
            return
        if not self._drag:
            return
        x, y = self._to_world(event)
        start_x, start_y, origin = self._drag
        dx, dy = x - start_x, y - start_y
        for bid, (old_x, old_y) in origin.items():
            block = self._block(bid)
            if block:
                px1, py1, px2, py2 = self._sheet_bounds()
                block.x = min(max(px1, old_x + dx), px2 - block.w)
                block.y = min(max(py1, old_y + dy), py2 - block.h)
        self.redraw()

    def _end_drag(self, event=None):
        if self._marquee:
            x0, y0, additive = self._marquee
            x1, y1 = self._to_world(event)
            left, right = sorted((x0, x1))
            top, bottom = sorted((y0, y1))
            picked = {b.id for b in self.blocks if left <= b.x and b.x + b.w <= right and top <= b.y and b.y + b.h <= bottom}
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
        s = self._scale()
        x1, y1 = self._to_screen(x, y)
        self.create_rectangle(x1, y1, x1 + 22 * s, y1 + 14 * s, outline=self.colors["selection"], dash=(2, 2), tags="preview")

    def _context(self, event):
        hit = self._find(*self._to_world(event))
        if hit:
            self.selected = hit.id
            self.selected_ids = {hit.id}
            self.on_select(hit)
            self.redraw()
        if self.on_context:
            self.on_context(hit, event.x_root, event.y_root, "plan")

    def _wheel(self, event):
        self._zoom(1.1 if event.delta > 0 else 0.9, event)

    def _zoom(self, factor, event=None):
        if event is not None:
            anchor_world = self._to_world(event)
        minimum = self._fit_zoom()
        self.view_mode = "manual"
        self.zoom = min(4.0, max(minimum, self.zoom * factor))
        self.redraw()
        if event is not None and self.zoom > minimum + 0.001:
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

    def redraw(self):
        self.delete("all")
        s = self._scale()
        x1, y1 = self._to_screen(0, 0)
        x2, y2 = self._to_screen(self.length_m, self.width_m)
        px1, py1, px2, py2 = self._sheet_bounds()
        page_x1, page_y1 = self._to_screen(px1, py1)
        page_x2, page_y2 = self._to_screen(px2, py2)
        self.configure(scrollregion=(page_x1, page_y1, page_x2, page_y2))
        if self.show_grid:
            minor_step = 5
            major_step = minor_step * 5
            start_x = math.floor(px1 / minor_step) * minor_step
            start_y = math.floor(py1 / minor_step) * minor_step
            end_x = math.ceil(px2 / minor_step) * minor_step
            end_y = math.ceil(py2 / minor_step) * minor_step

            for wx in range(start_x, end_x + 1, minor_step):
                gx, _ = self._to_screen(wx, 0)
                is_major = wx % major_step == 0
                self.create_line(
                    gx, page_y1, gx, page_y2,
                    fill=self.colors["border"] if is_major else self.colors["grid"],
                    width=1,
                    tags=("grid", "grid-major" if is_major else "grid-minor"),
                )
            for wy in range(start_y, end_y + 1, minor_step):
                _, gy = self._to_screen(0, wy)
                is_major = wy % major_step == 0
                self.create_line(
                    page_x1, gy, page_x2, gy,
                    fill=self.colors["border"] if is_major else self.colors["grid"],
                    width=1,
                    tags=("grid", "grid-major" if is_major else "grid-minor"),
                )
        self.create_rectangle(page_x1, page_y1, page_x2, page_y2, outline=self.colors["border"], width=1)
        self.create_rectangle(x1, y1, x2, y2, outline=self.colors["muted"], width=1)
        if self.zoom <= self._fit_zoom() + 0.001:
            self.xview_moveto(0)
            self.yview_moveto(0)
        self.create_text(
            x1 + 4, y1 - 6, anchor=tk.SW,
            text="%g × %g м" % (self.length_m, self.width_m),
            fill=self.colors["muted"], font=("Arial", 9),
        )
        if not self.blocks:
            self.create_text(
                (x1 + x2) / 2, (y1 + y2) / 2 - 14,
                text="План площадки", fill=self.colors["muted"], font=("Arial", 13, "bold"),
            )
            self.create_text(
                (x1 + x2) / 2, (y1 + y2) / 2 + 12,
                text="Выберите объект в верхней ленте и щёлкните на листе",
                fill=self.colors["muted"], font=("Arial", 9),
            )
        for t in self.ties:
            self._draw_tie(t)
        for b in self.blocks:
            self._draw_block(b)

    def _block(self, bid):
        for b in self.blocks:
            if b.id == bid:
                return b
        return None

    def _draw_tie(self, tie):
        a = self._block(tie.a)
        b = self._block(tie.b)
        if not a or not b:
            return
        x1, y1 = self._to_screen(a.x + a.w / 2, a.y + a.h / 2)
        x2, y2 = self._to_screen(b.x + b.w / 2, b.y + b.h / 2)
        color, dash = LINE.get(tie.kind, ("#334155", ()))
        self.create_line(x1, y1, x1, y2, x2, y2, fill=color, width=2, dash=dash)
        mx, my = (x1 + x2) / 2, y2 + 10
        self.create_text(mx, my, text=tie.kind, fill=color, font=("Arial", 8))

    def _draw_block(self, b):
        x1, y1 = self._to_screen(b.x, b.y)
        x2, y2 = self._to_screen(b.x + b.w, b.y + b.h)
        on = b.id in self.selected_ids or b.id == self._from
        fill = self.colors["accent_soft"] if on else FILL.get(b.kind, self.colors["surface"])
        outline = self.colors["selection"] if on else self.colors["muted"]
        self.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=2)
        font_spec = ("Segoe UI", self._label_font_size())
        label_width = max(20, int(x2 - x1 - 8))
        label = self._fit_label(b.name or b.kind, label_width, font_spec)
        self.create_text(
            (x1 + x2) / 2, (y1 + y2) / 2,
            text=label,
            fill=self.colors["text"],
            font=font_spec,
            width=label_width,
            justify=tk.CENTER,
        )
