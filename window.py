import json
import copy
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import ttkbootstrap as ttk
from tkinter_icons import MaterialIcon

from plan import PlanView
from scheme import SchemeView
from ui_theme import palette

FONT = "Segoe UI"

SCHEME_TOOLS = [
    "Внешняя энергосистема",
    "Генератор",
    "ГПУ",
    "Трансформатор 2-обм.",
    "Трансформатор 2-обм. расщепл.",
    "Трансформатор 3-обм.",
    "ВЛ",
    "КЛ",
    "Выключатель",
    "Секция шин",
    "Нагрузка",
    "Узел",
]

LV_TOOLS = [
    "Автоматический выключатель 1P",
    "Автоматический выключатель 2P",
    "Автоматический выключатель 3P",
    "Автоматический выключатель 4P",
    "Секционный автоматический выключатель",
    "Рубильник",
    "Контактор",
    "УЗО",
    "Дифференциальный автомат",
    "Фазная шина",
    "Шина N",
    "Шина PE",
    "Шина PEN",
    "Кабельная линия 0,4 кВ",
    "Нагрузка 0,4 кВ",
    "ГРЩ",
    "ЩСУ",
    "ЩО",
    "ШР",
]

LV_GROUPS = [
    ("Защита", [
        "Автоматический выключатель 1P",
        "Автоматический выключатель 2P",
        "Автоматический выключатель 3P",
        "Автоматический выключатель 4P",
        "Секционный автоматический выключатель",
        "УЗО",
        "Дифференциальный автомат",
    ]),
    ("Коммутация", ["Рубильник", "Контактор"]),
    ("Шины", ["Фазная шина", "Шина N", "Шина PE", "Шина PEN"]),
    ("Распределение", [
        "Кабельная линия 0,4 кВ",
        "Нагрузка 0,4 кВ",
        "ГРЩ",
        "ЩСУ",
        "ЩО",
        "ШР",
    ]),
]

PLAN_GROUPS = [
    ("Производственные объекты", [
        "Завод", "Цех", "Компрессорная", "Насосная", "Котельная",
        "Административный корпус", "Прочий объект",
    ]),
    ("Электроэнергетические объекты", [
        "Энергосистема", "ГПП", "ТП", "РП",
        "Собственная электростанция", "Мини-ТЭЦ", "Системная подстанция",
    ]),
    ("Газовая инфраструктура", [
        "Точка подключения ПГ",
    ]),
    ("Связи объектов", [
        "КЛ", "ВЛ", "Газопровод", "Технологическая связь", "Прочая связь",
    ]),
]

MATERIAL_TOOL_ICONS = {
    "Завод": "factory",
    "Цех": "factory",
    "Компрессорная": "factory",
    "Насосная": "water-pump",
    "Котельная": "radiator",
    "Административный корпус": "office-building",
    "Прочий объект": "home-city",
    "Энергосистема": "transmission-tower-import",
    "Внешняя энергосистема": "transmission-tower-import",
    "ГПП": "transmission-tower",
    "ТП": "power-plug",
    "РП": "electric-switch",
    "Собственная электростанция": "generator-stationary",
    "Мини-ТЭЦ": "factory",
    "Системная подстанция": "transmission-tower",
    "Генератор": "generator-stationary",
    "ГПУ": "generator-mobile",
    "Выключатель": "electric-switch",
    "Нагрузка": "lightning-bolt",
    "Нагрузка 0,4 кВ": "lightning-bolt",
    "КЛ": "cable-data",
    "Кабельная линия 0,4 кВ": "cable-data",
    "ВЛ": "transmission-tower",
    "Газопровод": "pipe",
    "Технологическая связь": "link-variant",
    "Прочая связь": "link-variant",
}


class App:
    def __init__(self, root):
        self.root = root
        root.title("ПВК")
        root.geometry("1280x760")
        root.minsize(960, 640)
        self.path = None
        self.dirty = False
        self.view = "plan"
        self._inside = None
        self._loose = {"items": [], "wires": []}
        self._lv_open = False
        self._tool_buttons = {}
        self._ribbon_tiles = {}
        self._active_tool = None
        self._selection_mode = True
        self._history = []
        self._history_index = -1
        self._save_history_index = -1
        self.theme_name = "dark"
        self.colors = palette(self.theme_name)
        self._icon_refs = []
        self._style = ttk.Style(theme="darkly")
        self._configure_theme()

        self._menu()
        self._toolbar()
        self._body()
        self.plan.set_theme(self.colors)
        self.scheme.set_theme(self.colors)
        self._status = tk.StringVar(value="План площадки")
        ttk.Label(root, textvariable=self._status, anchor=tk.W, style="Muted.TLabel", padding=(12, 6)).pack(
            side=tk.BOTTOM, fill=tk.X
        )
        self._show("plan")
        self._reset_history()
        root.protocol("WM_DELETE_WINDOW", self._quit)
        root.bind("<Escape>", lambda e: self._escape())
        root.bind("<Delete>", lambda e: self._delete())
        root.bind("<BackSpace>", lambda e: self._delete())
        root.bind("<Control-s>", lambda e: self._save())
        root.bind("<Command-s>", lambda e: self._save())
        root.bind("<Control-n>", lambda e: self._new())
        root.bind("<Command-n>", lambda e: self._new())
        root.bind("<Control-o>", lambda e: self._open())
        root.bind("<Command-o>", lambda e: self._open())
        root.bind("<Control-z>", lambda e: self._undo())
        root.bind("<Control-y>", lambda e: self._redo())
        root.bind("<Control-d>", lambda e: self._duplicate())
        root.bind("<Control-f>", lambda e: self._find_object())
        root.bind("<Key-r>", lambda e: self._rotate())
        root.bind("<Key-c>", lambda e: self._connect())
        root.bind("<Key-f>", lambda e: self._fit_sheet())
        root.bind("<Key-g>", lambda e: self._grid(not self.plan.show_grid))
        root.bind("<Key-1>", lambda e: self._zoom_reset())
        root.bind("<Key-v>", self._selection_shortcut)
        root.bind("<Key-V>", self._selection_shortcut)

    def _configure_theme(self):
        c = self.colors
        self.root.configure(bg=c["window"])
        self._style.theme_use("darkly")
        self._style.configure(".", background=c["window"], foreground=c["text"], font=(FONT, 10))
        self._style.configure("TFrame", background=c["window"])
        self._style.configure("Surface.TFrame", background=c["surface"])
        self._style.configure("Toolbar.TFrame", background=c["surface"], borderwidth=0)
        self._style.configure("TLabel", background=c["window"], foreground=c["text"])
        self._style.configure("Header.TLabel", background=c["surface"], foreground=c["text"], font=(FONT, 11, "bold"))
        self._style.configure("Section.TLabel", background=c["surface"], foreground=c["muted"], font=(FONT, 9, "bold"))
        self._style.configure("InspectorTitle.TLabel", background=c["surface"], foreground=c["text"], font=(FONT, 12, "bold"))
        self._style.configure("Inspector.TLabel", background=c["surface"], foreground=c["text"], font=(FONT, 9))
        self._style.configure("Muted.TLabel", background=c["surface"], foreground=c["muted"], font=(FONT, 9))
        self._style.configure("TButton", background=c["surface_alt"], foreground=c["text"], bordercolor=c["border"], borderwidth=0, padding=(8, 5))
        self._style.map("TButton", background=[("active", c["accent_soft"]), ("pressed", c["accent_soft"])])
        self._style.configure("Quick.TButton", background=c["surface"], borderwidth=0, padding=(4, 3), font=(FONT, 9))
        self._style.map("Quick.TButton", background=[("active", c["surface_alt"]), ("pressed", c["accent_soft"])])
        self._style.configure("Ribbon.TButton", background=c["surface"], borderwidth=0, padding=(4, 3), font=(FONT, 9))
        self._style.map("Ribbon.TButton", background=[("active", c["surface_alt"]), ("pressed", c["accent_soft"])])
        self._style.configure("Theme.TButton", background=c["accent"], foreground=c["accent_text"], padding=(8, 6), font=(FONT, 13, "bold"))
        self._style.map("Theme.TButton", background=[("active", c["accent"]), ("pressed", c["accent"])])
        self._style.configure("RibbonGroup.TFrame", background=c["surface_alt"], borderwidth=1, relief="solid")
        self._style.configure("Pick.TButton", background=c["accent"], foreground=c["accent_text"], bordercolor=c["accent"], font=(FONT, 10, "bold"), padding=(8, 5))
        self._style.map("Pick.TButton", background=[("active", c["accent_soft"])])
        self._style.configure("Danger.TButton", background=c["surface"], foreground=c["danger"], borderwidth=0, padding=(4, 3), font=(FONT, 9))
        self._style.map("Danger.TButton", background=[("active", c["surface_alt"]), ("pressed", c["accent_soft"])])
        self._style.configure("Tab.TButton", background=c["surface_alt"], foreground=c["muted"], borderwidth=0, padding=(9, 4))
        self._style.configure("ActiveTab.TButton", background=c["accent"], foreground=c["accent_text"], bordercolor=c["accent"], padding=(9, 4), font=(FONT, 9, "bold"))
        self._style.configure("TSeparator", background=c["border"])
        self._style.configure("TLabelframe", background=c["surface"], bordercolor=c["border"], relief="solid")
        self._style.configure("TLabelframe.Label", background=c["surface"], foreground=c["text"], font=(FONT, 10, "bold"))
        self._style.configure("TEntry", fieldbackground=c["surface_alt"], foreground=c["text"], bordercolor=c["border"], lightcolor=c["border"], darkcolor=c["border"], padding=6)
        self._style.map("TEntry", bordercolor=[("focus", c["accent"])], lightcolor=[("focus", c["accent"])], darkcolor=[("focus", c["accent"])])
        self._style.configure("TCombobox", fieldbackground=c["surface_alt"], foreground=c["text"])
        self._style.configure("TScrollbar", background=c["surface_alt"], troughcolor=c["window"])
        self._style.configure("TPanedwindow", background=c["divider"], sashwidth=1, sashrelief="flat")

    def _toggle_theme(self):
        self.theme_name = "dark" if self.theme_name == "light" else "light"
        self.colors = palette(self.theme_name)
        self._icon_refs.clear()
        self._configure_theme()
        self._theme_button.configure(image=self._icon("sun-fill" if self.theme_name == "dark" else "moon-stars-fill", 18, self.colors["accent"]), text="")
        self._menu()
        self._restyle_ribbon_group(self._edit_group)
        if hasattr(self, "_panes"):
            self._panes.configure(bg=self.colors["divider"])
        if hasattr(self, "_palette_canvas"):
            self._palette_canvas.configure(bg=self.colors["surface"])
        self.plan.set_theme(self.colors)
        self.scheme.set_theme(self.colors)
        self._render_ribbon()
        self._set_status("Тема: %s" % ("тёмная" if self.theme_name == "dark" else "светлая"))

    def _menu(self):
        c = self.colors
        if hasattr(self, "_menu_host"):
            self._menu_host.destroy()
        self.root.config(menu="")
        bar = ttk.Frame(self.root, style="Toolbar.TFrame", padding=(8, 3))
        if hasattr(self, "_top_toolbar"):
            bar.pack(fill=tk.X, before=self._top_toolbar)
        else:
            bar.pack(fill=tk.X)
        self._menu_host = bar
        menu_style = {
            "bg": c["surface"], "fg": c["text"], "activebackground": c["accent_soft"],
            "activeforeground": c["text"], "borderwidth": 0,
        }
        file_m = self._menu_button(bar, "Файл", menu_style)
        file_m.add_command(label="Новый", command=self._new)
        file_m.add_command(label="Открыть…", command=self._open)
        file_m.add_command(label="Сохранить", command=self._save)
        file_m.add_command(label="Сохранить как…", command=self._save_as)
        file_m.add_separator()
        file_m.add_command(label="Выход", command=self._quit)

        view_m = self._menu_button(bar, "Вид", menu_style)
        view_m.add_command(label="Схема объекта", command=self._show_loose_scheme)
        view_m.add_command(label="План площадки", command=self._show_plan)
        view_m.add_separator()
        view_m.add_command(label="Показать сетку", command=lambda: self._grid(True))
        view_m.add_command(label="Скрыть сетку", command=lambda: self._grid(False))
        view_m.add_command(label="Масштаб 100%", command=self._zoom_reset)

        edit_m = self._menu_button(bar, "Правка", menu_style)
        edit_m.add_command(label="Соединить", command=self._connect)
        edit_m.add_command(label="Объединить в объект", command=self._merge)
        edit_m.add_command(label="Повернуть", command=self._rotate)
        edit_m.add_separator()
        edit_m.add_command(label="Удалить", command=self._delete)

        help_m = self._menu_button(bar, "Помощь", menu_style)
        help_m.add_command(label="О программе", command=self._about)
        ttk.Separator(bar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=2)
        for icon, command, tip in [
            ("file-earmark-plus", self._new, "Новый лист (Ctrl+N)"),
            ("folder2-open", self._open, "Открыть лист (Ctrl+O)"),
            ("floppy", self._save, "Сохранить (Ctrl+S)"),
            ("diagram-3", self._navigator, "Структура проекта"),
        ]:
            button = self._icon_button(bar, icon, self.colors["accent"], "Quick.TButton", command, tip)
            button.pack(side=tk.LEFT, padx=1)
        ttk.Separator(bar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=2)
        for icon, command, tip in [
            ("grid-3x3-gap", lambda: self._grid(not self.plan.show_grid), "Показать или скрыть сетку (G)"),
            ("aspect-ratio", self._zoom_reset, "Показать участок 200 × 150 м (1)"),
            ("arrows-fullscreen", self._fit_sheet, "Показать всю рабочую область (F)"),
        ]:
            button = self._icon_button(bar, icon, self.colors["accent"], "Quick.TButton", command, tip)
            button.pack(side=tk.LEFT, padx=1)
        cursor = self._icon("cursor-fill", 15, self.colors["accent_text"])
        self._select_button = ttk.Button(bar, image=cursor, text="", style="ActiveTab.TButton", width=3, command=self._select_mode)
        self._select_button.image = cursor
        self._select_button.pack(side=tk.LEFT, padx=(5, 1))
        self._tooltip(self._select_button, "Выбор и перемещение объектов (V)")
        theme_name = "sun-fill" if self.theme_name == "dark" else "moon-stars-fill"
        self._theme_button = self._icon_button(
            bar, theme_name, self.colors["accent"], "Quick.TButton",
            self._toggle_theme, "Сменить цветовую тему", width=4, icon_size=18,
        )
        self._theme_button.pack(side=tk.RIGHT, padx=1)

    @staticmethod
    def _menu_button(parent, text, options):
        button = tk.Menubutton(
            parent, text=text, padx=7, pady=3, indicatoron=False,
            relief=tk.FLAT, cursor="hand2", **options,
        )
        menu = tk.Menu(
            button, tearoff=0,
            bg=options["bg"], fg=options["fg"],
            activebackground=options["activebackground"],
            activeforeground=options["activeforeground"],
            borderwidth=1, relief=tk.SOLID,
        )
        button.configure(menu=menu)
        button.pack(side=tk.LEFT, padx=1)
        return menu

    def _icon(self, name, size=16, color=None):
        icon = ttk.Icon(name, size=size, color=color or self.colors["text"])
        self._icon_refs.append(icon)
        return icon

    def _icon_button(self, parent, name, color, style, command, tip, width=3, icon_size=15):
        image = self._icon(name, icon_size, color)
        button = ttk.Button(parent, image=image, text="", style=style, width=width, command=command)
        button.image = image
        self._tooltip(button, tip)
        return button

    def _toolbar(self):
        bar = ttk.Frame(self.root, style="Toolbar.TFrame", padding=(8, 3), height=58)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)
        self._top_toolbar = bar
        self._mode_buttons = {}
        for key, text, command, tip in [
            ("plan", "План", self._show_plan, "План площадки"),
            ("scheme", "Схема", self._show_loose_scheme, "Схема объекта"),
        ]:
            button = ttk.Button(bar, text=text, style="Tab.TButton", width=11, command=command)
            button.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 2))
            self._tooltip(button, tip)
            self._mode_buttons[key] = button
        ttk.Separator(bar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)
        self._edit_group = self._ribbon_group(bar, "Правка", [])
        for icon, command, tip, style, color in [("bezier2", self._connect, "Соединить (C)", "Ribbon.TButton", self.colors["accent"]), ("arrow-clockwise", self._rotate, "Повернуть (R)", "Ribbon.TButton", self.colors["accent"]), ("trash3", self._delete, "Удалить (Delete)", "Danger.TButton", self.colors["danger"])]:
            button = self._icon_button(self._edit_group._tools, icon, color, style, command, tip)
            button.pack(side=tk.LEFT, padx=1)
        ttk.Separator(bar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)
        self._ribbon_host = ttk.Frame(bar, style="Toolbar.TFrame")
        self._ribbon_host.pack(side=tk.LEFT, fill=tk.Y)
        self._ribbon_tab = "plan"
        self._back = ttk.Button(self._ribbon_host, text="←", style="Ribbon.TButton", command=self._show_plan)
        self._render_ribbon()

    def _ribbon_group(self, parent, title, commands):
        c = self.colors
        group = tk.Frame(
            parent, bg=c["surface"], bd=0,
            highlightbackground=c["divider"], highlightcolor=c["divider"], highlightthickness=1,
        )
        group.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        group._tools = tk.Frame(group, bg=c["surface"])
        group._tools.pack(fill=tk.X)
        for name, command, is_link in commands:
            self._tool_tile(group._tools, name, command, is_link)
        group._caption = tk.Label(
            group, text=title, anchor=tk.CENTER, bg=c["surface"], fg=c["muted"],
            font=(FONT, 9), padx=4, pady=1,
        )
        group._caption.pack(side=tk.BOTTOM, fill=tk.X)
        return group

    def _restyle_ribbon_group(self, group):
        c = self.colors
        group.configure(bg=c["surface"], highlightbackground=c["divider"], highlightcolor=c["divider"])
        group._tools.configure(bg=c["surface"])
        group._caption.configure(bg=c["surface"], fg=c["muted"])

    def _tool_tile(self, parent, name, command, is_link=False):
        c = self.colors
        active = self._active_tool == name
        tile = tk.Canvas(
            parent, width=29, height=29, bg=c["accent_soft"] if active else c["surface"],
            highlightthickness=1,
            highlightbackground=c["accent"] if active else c["surface"],
            highlightcolor=c["accent"], cursor="hand2", takefocus=1,
        )
        tile.pack(side=tk.LEFT, padx=2, pady=1)
        ink = c["accent"] if is_link else c["text"]
        tile.create_rectangle(
            0, 0, 29, 29,
            fill=c["accent_soft"] if active else c["surface"],
            outline="", tags="tile_bg",
        )
        # Small schematic pictograms: intentionally compact, with full name in tooltip.
        material_name = MATERIAL_TOOL_ICONS.get(name)
        if material_name:
            material_icon = MaterialIcon(material_name, size=20, color=ink)
            tile.create_image(14, 14, image=material_icon.image)
            tile._material_icon = material_icon
            self._icon_refs.append(material_icon)
        elif is_link or name in ("КЛ", "ВЛ", "Газопровод", "Технологическая связь", "Прочая связь"):
            tile.create_line(5, 23, 23, 5, fill=ink, width=2, dash=(3, 2) if name == "ВЛ" else ())
        elif "Трансформатор" in name:
            tile.create_oval(4, 7, 14, 20, outline=ink, width=2)
            tile.create_oval(13, 7, 23, 20, outline=ink, width=2)
        elif name in ("Выключатель", "Автоматический выключатель 1P", "Автоматический выключатель 2P", "Автоматический выключатель 3P", "Автоматический выключатель 4P", "Секционный автоматический выключатель", "Рубильник", "Контактор", "УЗО", "Дифференциальный автомат"):
            tile.create_line(4, 11, 10, 11, fill=ink, width=2)
            tile.create_line(10, 11, 19, 5, fill=ink, width=2)
            tile.create_line(19, 11, 24, 11, fill=ink, width=2)
            marker = {
                "Автоматический выключатель 1P": "1P",
                "Автоматический выключатель 2P": "2P",
                "Автоматический выключатель 3P": "3P",
                "Автоматический выключатель 4P": "4P",
                "Секционный автоматический выключатель": "СЕК",
                "Рубильник": "Р",
                "Контактор": "К",
                "УЗО": "УЗО",
                "Дифференциальный автомат": "ДИФ",
            }.get(name, "")
            if marker:
                tile.create_text(14, 22, text=marker, fill=ink, font=(FONT, 6, "bold"))
        elif name in ("Секция шин", "Фазная шина", "Шина N", "Шина PE", "Шина PEN"):
            tile.create_line(4, 10, 24, 10, fill=ink, width=4)
            marker = {"Фазная шина": "L", "Шина N": "N", "Шина PE": "PE", "Шина PEN": "PEN"}.get(name, "")
            if marker:
                tile.create_text(14, 22, text=marker, fill=ink, font=(FONT, 6, "bold"))
        elif name in ("Генератор", "ГПУ", "Энергосистема", "Внешняя энергосистема", "Собственная электростанция", "Мини-ТЭЦ"):
            tile.create_oval(5, 5, 23, 23, outline=ink, width=2)
            tile.create_text(14, 14, text="~", fill=ink, font=(FONT, 14, "bold"))
        elif "Нагрузка" in name:
            tile.create_polygon(14, 4, 24, 23, 4, 23, fill="", outline=ink, width=2)
        elif name in ("ГПП", "ТП", "РП", "ГРЩ", "ЩСУ", "ЩО", "ШР"):
            tile.create_rectangle(5, 4, 23, 23, outline=ink, width=2)
            tile.create_text(14, 14, text=name, fill=ink, font=(FONT, 6, "bold"))
        else:
            tile.create_rectangle(5, 6, 23, 22, outline=ink, width=2)
            tile.create_line(9, 11, 20, 11, fill=ink)
        def enter(_event):
            if self._active_tool != name:
                tile.configure(bg=c["surface_alt"], highlightbackground=c["border"])
                tile.itemconfigure("tile_bg", fill=c["surface_alt"])

        def leave(_event):
            if self._active_tool != name:
                tile.configure(bg=c["surface"], highlightbackground=c["surface"])
                tile.itemconfigure("tile_bg", fill=c["surface"])

        tile.bind("<Enter>", enter)
        tile.bind("<Leave>", leave)
        tile.bind("<Button-1>", lambda _event: command())
        tile.bind("<Return>", lambda _event: command())
        tile.bind("<space>", lambda _event: command())
        self._tooltip(tile, name)
        self._ribbon_tiles[name] = tile

    def _refresh_ribbon_tiles(self):
        c = self.colors
        for name, tile in self._ribbon_tiles.items():
            if not tile.winfo_exists():
                continue
            active = self._active_tool == name
            background = c["accent_soft"] if active else c["surface"]
            tile.configure(
                bg=background,
                highlightbackground=c["accent"] if active else c["surface"],
                highlightcolor=c["accent"],
            )
            tile.itemconfigure("tile_bg", fill=background)

    def _render_ribbon(self, tab=None):
        if tab:
            self._ribbon_tab = tab
        for child in self._ribbon_host.winfo_children():
            child.pack_forget()
            if child is not self._back:
                child.destroy()
        self._ribbon_tiles.clear()
        for key, button in self._mode_buttons.items():
            button.configure(style="ActiveTab.TButton" if key == self.view else "Tab.TButton")
        if self.view == "scheme":
            self._ribbon_group(self._ribbon_host, "Источники", [(n, lambda x=n: self._pick_tool(x, False), False) for n in SCHEME_TOOLS[:3]])
            self._ribbon_group(self._ribbon_host, "Оборудование", [(n, lambda x=n: self._pick_tool(x, False), False) for n in SCHEME_TOOLS[3:6]])
            self._ribbon_group(self._ribbon_host, "Соединения", [(n, lambda x=n: self._pick_tool(x, False), n in ("ВЛ", "КЛ")) for n in SCHEME_TOOLS[6:10]])
            self._ribbon_group(self._ribbon_host, "Нагрузка", [(n, lambda x=n: self._pick_tool(x, False), False) for n in SCHEME_TOOLS[10:]])
            for title, names in LV_GROUPS:
                self._ribbon_group(
                    self._ribbon_host,
                    title,
                    [(n, lambda x=n: self._pick_tool(x, False), n == "Кабельная линия 0,4 кВ") for n in names],
                )
        else:
            self._ribbon_group(self._ribbon_host, "Объекты", [(n, lambda x=n: self._pick_tool(x, False), False) for n in PLAN_GROUPS[0][1][:4]])
            self._ribbon_group(self._ribbon_host, "Энергетика", [(n, lambda x=n: self._pick_tool(x, False), False) for n in PLAN_GROUPS[1][1]])
            self._ribbon_group(self._ribbon_host, "Связи", [(n, lambda x=n: self._pick_tool(x, True), True) for n in PLAN_GROUPS[3][1]])
        if self.view == "scheme" and self._inside is not None:
            self._back.pack(side=tk.RIGHT, padx=(4, 0), pady=4)

    @staticmethod
    def _tooltip(widget, text):
        def show(_event):
            if getattr(widget, "_tip", None):
                return
            def open_tip():
                if not widget.winfo_exists() or getattr(widget, "_tip", None):
                    return
                tip = tk.Toplevel(widget)
                tip.wm_overrideredirect(True)
                tip.configure(bg="#171a1c")
                x = widget.winfo_rootx() + 4
                y = widget.winfo_rooty() + widget.winfo_height() + 6
                tip.geometry("+%d+%d" % (x, y))
                tk.Label(
                    tip, text=text, bg="#171a1c", fg="#f3f5f6",
                    padx=8, pady=5, font=(FONT, 9), bd=0,
                ).pack()
                widget._tip = tip
            widget._tip_after = widget.after(420, open_tip)
        def hide(_event):
            pending = getattr(widget, "_tip_after", None)
            if pending:
                widget.after_cancel(pending)
                widget._tip_after = None
            tip = getattr(widget, "_tip", None)
            if tip:
                tip.destroy()
                widget._tip = None
        widget.bind("<Enter>", show, add=True)
        widget.bind("<Leave>", hide, add=True)

    def _body(self):
        panes = tk.PanedWindow(
            self.root, orient=tk.HORIZONTAL, bg=self.colors["divider"],
            bd=0, relief=tk.FLAT, sashwidth=6, sashpad=0, showhandle=False,
            opaqueresize=True,
        )
        panes.pack(fill=tk.BOTH, expand=True, padx=0, pady=(1, 0))

        center = ttk.Frame(panes)
        right = ttk.Frame(panes, style="Surface.TFrame", width=268)
        panes.add(center, stretch="always")
        panes.add(right, minsize=240, stretch="never")
        self._panes = panes
        self._props_pane = right
        self.scheme = SchemeView(center, self._on_scheme_select, self._set_status, self._touch, self._context_menu)
        self.plan = PlanView(center, self._on_plan_select, self._set_status, self._open_object, self._touch, self._context_menu)

        box = ttk.Frame(right, style="Surface.TFrame", padding=(12, 10))
        box.pack(fill=tk.BOTH, expand=True)
        ttk.Label(box, text="Свойства", style="InspectorTitle.TLabel").pack(anchor=tk.W)
        ttk.Separator(box, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(8, 9))
        self._prop_title = ttk.Label(box, text="Ничего не выбрано", style="Muted.TLabel")
        self._prop_title.pack(anchor=tk.W, pady=(0, 10))

        self._name_var = tk.StringVar()
        self._w_var = tk.StringVar()
        self._h_var = tk.StringVar()
        self._site_l = tk.StringVar(value="200")
        self._site_w = tk.StringVar(value="150")

        self._name_row = ttk.Frame(box, style="Surface.TFrame")
        ttk.Label(self._name_row, text="Название", style="Inspector.TLabel").pack(anchor=tk.W)
        ttk.Entry(self._name_row, textvariable=self._name_var).pack(fill=tk.X, pady=(2, 6))

        self._size_row = ttk.Frame(box, style="Surface.TFrame")
        ttk.Label(self._size_row, text="Размер объекта", style="Section.TLabel").pack(anchor=tk.W, pady=(3, 6))
        ttk.Label(self._size_row, text="Ширина, м", style="Inspector.TLabel").pack(anchor=tk.W)
        ttk.Entry(self._size_row, textvariable=self._w_var).pack(fill=tk.X, pady=(2, 6))
        ttk.Label(self._size_row, text="Высота, м", style="Inspector.TLabel").pack(anchor=tk.W)
        ttk.Entry(self._size_row, textvariable=self._h_var).pack(fill=tk.X, pady=(2, 6))

        self._site_row = ttk.Frame(box, style="Surface.TFrame")
        ttk.Separator(self._site_row, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(4, 9))
        ttk.Label(self._site_row, text="Площадка", style="Section.TLabel").pack(anchor=tk.W, pady=(0, 6))
        ttk.Label(self._site_row, text="Длина, м", style="Inspector.TLabel").pack(anchor=tk.W)
        ttk.Entry(self._site_row, textvariable=self._site_l).pack(fill=tk.X, pady=(2, 6))
        ttk.Label(self._site_row, text="Ширина, м", style="Inspector.TLabel").pack(anchor=tk.W)
        ttk.Entry(self._site_row, textvariable=self._site_w).pack(fill=tk.X, pady=(2, 6))

        ttk.Button(box, text="Применить", style="Pick.TButton", command=self._apply_props).pack(fill=tk.X, pady=(12, 0))
        self._props_visible = True

    def _scroller(self, parent):
        holder = ttk.Frame(parent)
        holder.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(holder, bg=self.colors["surface"], highlightthickness=0, width=220)
        scroll = ttk.Scrollbar(holder, orient=tk.VERTICAL, command=canvas.yview)
        inner = ttk.Frame(canvas)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        win = canvas.create_window((0, 0), window=inner, anchor=tk.NW)
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        def _fit(event):
            canvas.itemconfigure(win, width=event.width)

        canvas.bind("<Configure>", _fit)
        self._palette_canvas = canvas
        return inner

    def _fill_palette(self):
        # The compact icon palette now lives in the top ribbon.
        if not hasattr(self, "_palette_host"):
            return
        for child in self._palette_host.winfo_children():
            child.destroy()
        self._tool_buttons.clear()
        if self.view == "scheme":
            frame = ttk.LabelFrame(self._palette_host, text="Элементы схемы", padding=6)
            frame.pack(fill=tk.X, padx=6, pady=6)
            for name in SCHEME_TOOLS:
                self._tool_btn(frame, name, False)
            toggle = ttk.Button(frame, text="► Элементы до 1 кВ", command=self._toggle_lv)
            toggle.pack(fill=tk.X, pady=(6, 2))
            self._lv_toggle = toggle
            self._lv_frame = ttk.Frame(frame)
            for name in LV_TOOLS:
                self._tool_btn(self._lv_frame, name, True)
            if self._lv_open:
                self._lv_toggle.configure(text="▼ Элементы до 1 кВ")
                self._lv_frame.pack(fill=tk.X)
            return
        for title, names in PLAN_GROUPS:
            frame = ttk.LabelFrame(self._palette_host, text=title, padding=6)
            frame.pack(fill=tk.X, padx=6, pady=(6, 0))
            links = title == "Связи объектов"
            for name in names:
                self._tool_btn(frame, name, links)

    def _tool_btn(self, parent, name, is_link):
        icon = "⌁" if is_link else "◈"
        btn = ttk.Button(parent, text="%s  %s" % (icon, name), command=lambda n=name, link=is_link: self._pick_tool(n, link))
        btn.pack(fill=tk.X, pady=1)
        self._tooltip(btn, "Выбрать инструмент: %s" % name)
        self._tool_buttons[name] = btn
        if name == self._active_tool:
            btn.configure(style="Pick.TButton")

    def _toggle_lv(self):
        self._lv_open = not self._lv_open
        self._fill_palette()

    def _pick_tool(self, name, is_link):
        self._active_tool = name
        self._selection_mode = False
        self._select_button.configure(style="Tab.TButton")
        for key, btn in self._tool_buttons.items():
            btn.configure(style="Pick.TButton" if key == name else "TButton")
        if self.view == "scheme":
            self.scheme.set_tool(name)
        elif is_link:
            self.plan.set_link(name)
        else:
            self.plan.set_tool(name)
        self._refresh_ribbon_tiles()

    def _select_mode(self):
        self._escape()
        self._selection_mode = True
        self._select_button.configure(style="ActiveTab.TButton")
        self._set_status("Выбор: щёлкните объект для выделения, потяните — для перемещения")

    def _selection_shortcut(self, event):
        """Включает режим выбора, не мешая вводу текста в полях свойств."""
        if event.widget.winfo_class() in {"Entry", "TEntry", "Combobox", "TCombobox"}:
            return None
        self._select_mode()
        return "break"

    def _show(self, name):
        self.view = name
        self.scheme.pack_forget()
        self.plan.pack_forget()
        if name == "scheme":
            self.scheme.pack(fill=tk.BOTH, expand=True)
            self._name_row.pack(fill=tk.X)
            self._size_row.pack_forget()
            self._site_row.pack_forget()
            self._set_status(self._scheme_status())
            sheet = self.scheme
        else:
            self.plan.pack(fill=tk.BOTH, expand=True)
            self._name_row.pack(fill=tk.X)
            self._size_row.pack(fill=tk.X)
            self._site_row.pack(fill=tk.X, pady=(8, 0))
            self._set_status("План площадки")
            sheet = self.plan
        self._active_tool = None
        self._selection_mode = True
        self._select_button.configure(style="ActiveTab.TButton")
        self._fill_palette()
        self._show_selection(sheet.current())
        if name == "scheme":
            self.scheme.redraw()
        else:
            self.plan.redraw()
        self._ribbon_tab = name
        self._render_ribbon()

    def _scheme_status(self):
        if self._inside is None:
            return "Схема объекта"
        block = self.plan.block(self._inside)
        if block is None:
            return "Схема объекта"
        return "Схема «%s». Двойной клик по объекту на плане открывает её снова." % block.name

    def _store_sheet(self):
        data = self.scheme.dump()
        if self._inside is None:
            self._loose = data
            return
        block = self.plan.block(self._inside)
        if block is not None:
            block.sheet = data

    def _show_loose_scheme(self):
        if self.view == "scheme":
            self._store_sheet()
        self._inside = None
        self.scheme.load(self._loose or {"items": [], "wires": []})
        self._show("scheme")

    def _show_plan(self):
        if self.view == "scheme":
            self._store_sheet()
        self._inside = None
        self._show("plan")

    def _open_object(self, block):
        if self.view == "scheme":
            self._store_sheet()
        self._inside = block.id
        self.scheme.load(block.sheet or {"items": [], "wires": []})
        self._show("scheme")

    def _merge(self):
        if self.view == "scheme" and self._inside is not None:
            messagebox.showinfo(
                "Объединение",
                "Объединение доступно на общей схеме, не внутри объекта.",
            )
            return
        if self.view == "scheme":
            sheet = self.scheme.dump()
        else:
            sheet = self._loose or {"items": [], "wires": []}
        if not sheet.get("items"):
            messagebox.showwarning("Объединение", "На схеме нет элементов.")
            return
        asked = self._ask_object()
        if not asked:
            return
        block = self.plan.add_object(asked["kind"], asked["name"], sheet)
        self._loose = {"items": [], "wires": []}
        self._inside = None
        self.scheme.load(self._loose)
        self._show("plan")
        self.plan.selected = block.id
        self.plan.redraw()
        self._show_selection(block)
        self._touch()
        self._set_status("На плане объект «%s». Двойной клик — его схема." % block.name)

    def _ask_object(self):
        kinds = []
        for title, names in PLAN_GROUPS:
            if title == "Связи объектов":
                continue
            kinds.extend(names)
        win = tk.Toplevel(self.root)
        win.title("Объединить в объект")
        win.transient(self.root)
        win.resizable(False, False)
        name = tk.StringVar(value="Объект 1")
        kind = tk.StringVar(value="Цех")
        ttk.Label(win, text="Название").grid(row=0, column=0, sticky=tk.W, padx=10, pady=(10, 4))
        ttk.Entry(win, textvariable=name, width=32).grid(row=1, column=0, padx=10, sticky=tk.EW)
        ttk.Label(win, text="Тип").grid(row=2, column=0, sticky=tk.W, padx=10, pady=(8, 4))
        box = ttk.Combobox(win, textvariable=kind, values=kinds, state="readonly", width=30)
        box.grid(row=3, column=0, padx=10, sticky=tk.EW)
        result = {}

        def ok():
            result["name"] = name.get().strip() or "Объект"
            result["kind"] = kind.get().strip() or "Цех"
            win.destroy()

        def cancel():
            win.destroy()

        row = ttk.Frame(win)
        row.grid(row=4, column=0, sticky=tk.E, padx=10, pady=10)
        ttk.Button(row, text="Отмена", command=cancel).pack(side=tk.RIGHT)
        ttk.Button(row, text="Создать", command=ok).pack(side=tk.RIGHT, padx=(0, 6))
        win.protocol("WM_DELETE_WINDOW", cancel)
        win.grab_set()
        self.root.wait_window(win)
        return result or None

    def _grid(self, on):
        self.scheme.show_grid = on
        self.plan.show_grid = on
        self.scheme.redraw()
        self.plan.redraw()

    def _zoom_reset(self):
        self.scheme.zoom_reset()
        self.plan.zoom_reset()

    def _connect(self):
        if self.view != "scheme":
            self._set_status("На плане выберите тип связи в верхней ленте")
            return
        self._active_tool = None
        self._selection_mode = False
        self._select_button.configure(style="Tab.TButton")
        for btn in self._tool_buttons.values():
            btn.configure(style="TButton")
        self.scheme.set_connect(True)

    def _rotate(self):
        if self.view == "scheme":
            self.scheme.rotate_selected()
            self._touch()

    def _delete(self):
        if self.view == "scheme":
            self.scheme.delete_selected()
        else:
            self.plan.delete_selected()
        self._clear_props()
        self._touch()

    def _escape(self):
        self.scheme.set_connect(False)
        self.scheme.tool = None
        self.plan.tool = None
        self.plan.link_kind = None
        self._active_tool = None
        self._selection_mode = True
        self._select_button.configure(style="ActiveTab.TButton")
        for btn in self._tool_buttons.values():
            btn.configure(style="TButton")
        if hasattr(self, "_ribbon_host"):
            self._refresh_ribbon_tiles()
        self._set_status("Готово")

    def _on_scheme_select(self, item):
        if self.view != "scheme":
            return
        if len(self.scheme.selected_ids) > 1:
            self._show_multi_selection(len(self.scheme.selected_ids))
            self._set_status("Выбрано элементов: %d. Перетащите любой из них для совместного перемещения." % len(self.scheme.selected_ids))
            return
        self._show_selection(item)
        if item:
            self._touch()

    def _on_plan_select(self, item):
        if self.view != "plan":
            return
        if len(self.plan.selected_ids) > 1:
            self._show_multi_selection(len(self.plan.selected_ids))
            self._set_status("Выбрано объектов: %d. Перетащите любой из них для совместного перемещения." % len(self.plan.selected_ids))
            return
        self._show_selection(item)
        if item:
            self._touch()

    def _show_selection(self, item):
        if item is None:
            self._clear_props()
            return
        self._set_props_visible(True)
        kind = getattr(item, "kind", "")
        self._prop_title.configure(text=kind)
        self._name_var.set(getattr(item, "name", "") or "")
        if hasattr(item, "w"):
            self._w_var.set("%g" % item.w)
            self._h_var.set("%g" % item.h)
        self._site_l.set("%g" % self.plan.length_m)
        self._site_w.set("%g" % self.plan.width_m)

    def _clear_props(self):
        self._set_props_visible(False)
        self._prop_title.configure(text="Ничего не выбрано")
        self._name_var.set("")
        self._w_var.set("")
        self._h_var.set("")

    def _show_multi_selection(self, count):
        self._set_props_visible(True)
        self._prop_title.configure(text="Выбрано объектов: %d" % count)
        self._name_var.set("")
        self._w_var.set("")
        self._h_var.set("")

    def _set_props_visible(self, visible):
        # Properties are a permanent CAD panel; only their contents change with selection.
        self._props_visible = True

    def _apply_props(self):
        if self.view == "scheme":
            self.scheme.rename(self._name_var.get().strip())
        else:
            self.plan.apply_fields(
                self._name_var.get(),
                self._w_var.get(),
                self._h_var.get(),
                self._site_l.get(),
                self._site_w.get(),
            )
        self._touch()
        self._set_status("Свойства записаны")

    def _set_status(self, text):
        self._status.set(text)

    def _touch(self):
        snapshot = self._snapshot()
        if self._history_index < 0:
            return
        if snapshot != self._history[self._history_index]:
            self._history = self._history[: self._history_index + 1]
            self._history.append(copy.deepcopy(snapshot))
            self._history_index += 1
        self.dirty = self._history_index != self._save_history_index

    def _reset_history(self):
        self._history = [copy.deepcopy(self._snapshot())]
        self._history_index = 0
        self._save_history_index = 0
        self.dirty = False

    def _undo(self):
        if self._history_index <= 0:
            self._set_status("Отмена: больше нет действий")
            return
        self._history_index -= 1
        self._apply_snapshot(copy.deepcopy(self._history[self._history_index]))
        self.dirty = self._history_index != self._save_history_index
        self._set_status("Отменено действие (Ctrl+Z)")

    def _redo(self):
        if self._history_index >= len(self._history) - 1:
            self._set_status("Повтор: больше нет действий")
            return
        self._history_index += 1
        self._apply_snapshot(copy.deepcopy(self._history[self._history_index]))
        self.dirty = self._history_index != self._save_history_index
        self._set_status("Повторено действие (Ctrl+Y)")

    def _fit_sheet(self):
        sheet = self.scheme if self.view == "scheme" else self.plan
        sheet.fit_sheet()
        self._set_status("Лист вписан в окно (F)")

    def _duplicate(self):
        if self.view == "plan":
            originals = [b for b in self.plan.blocks if b.id in self.plan.selected_ids]
            if not originals:
                return
            for source in originals:
                clone = self.plan.add_object(source.kind, source.name + " (копия)", copy.deepcopy(source.sheet))
                clone.x = min(self.plan.length_m - clone.w, source.x + 5)
                clone.y = min(self.plan.width_m - clone.h, source.y + 5)
            self.plan.redraw()
        else:
            originals = [it for it in self.scheme.items if it.id in self.scheme.selected_ids]
            if not originals:
                return
            for source in originals:
                from scheme import Elem
                clone = Elem(self.scheme._seq, source.kind, source.x + 20, source.y + 20)
                clone.name = (source.name or source.kind) + " (копия)"
                self.scheme._seq += 1
                self.scheme.items.append(clone)
                self.scheme.selected = clone.id
                self.scheme.selected_ids = {clone.id}
            self.scheme.redraw()
        self._touch()
        self._set_status("Создана копия выбранного объекта (Ctrl+D)")

    def _find_object(self):
        query = simpledialog.askstring("Поиск объекта", "Имя или тип объекта:", parent=self.root)
        if not query:
            return
        needle = query.casefold()
        for block in self.plan.blocks:
            if needle in (block.name or "").casefold() or needle in block.kind.casefold():
                self._show_plan()
                self.plan.selected = block.id
                self.plan.selected_ids = {block.id}
                self.plan.redraw()
                self._show_selection(block)
                self._set_status("Найдено: %s" % (block.name or block.kind))
                return
        for item in self.scheme.items:
            if needle in (item.name or "").casefold() or needle in item.kind.casefold():
                self._show_loose_scheme()
                self.scheme.selected = item.id
                self.scheme.selected_ids = {item.id}
                self.scheme.redraw()
                self._show_selection(item)
                self._set_status("Найдено: %s" % (item.name or item.kind))
                return
        self._set_status("Объект не найден")

    def _navigator(self):
        win = tk.Toplevel(self.root)
        win.title("Структура проекта")
        win.geometry("330x420")
        win.transient(self.root)
        frame = ttk.Frame(win, padding=8)
        frame.pack(fill=tk.BOTH, expand=True)
        tree = ttk.Treeview(frame, show="tree")
        tree.pack(fill=tk.BOTH, expand=True)
        root_id = tree.insert("", tk.END, text="План площадки", open=True)
        refs = {}
        for block in self.plan.blocks:
            item_id = tree.insert(root_id, tk.END, text="%s — %s" % (block.kind, block.name or block.kind))
            refs[item_id] = block

        def open_selected(_event=None):
            selected = tree.selection()
            if not selected or selected[0] not in refs:
                return
            block = refs[selected[0]]
            self._show_plan()
            self.plan.selected = block.id
            self.plan.selected_ids = {block.id}
            self.plan.redraw()
            self._show_selection(block)
            self._set_status("Выбран объект: %s" % (block.name or block.kind))
            win.destroy()

        tree.bind("<Double-Button-1>", open_selected)
        ttk.Button(frame, text="Перейти к объекту", command=open_selected).pack(anchor=tk.E, pady=(8, 0))

    def _align_selected(self, axis, edge):
        items = self.plan.blocks if self.view == "plan" else self.scheme.items
        selected_ids = self.plan.selected_ids if self.view == "plan" else self.scheme.selected_ids
        selected = [item for item in items if item.id in selected_ids]
        if len(selected) < 2:
            self._set_status("Для выравнивания выберите минимум два объекта")
            return
        key = "x" if axis == "x" else "y"
        values = [getattr(item, key) for item in selected]
        target = min(values) if edge == "min" else max(values)
        for item in selected:
            setattr(item, key, target)
        (self.plan if self.view == "plan" else self.scheme).redraw()
        self._touch()
        self._set_status("Объекты выровнены")

    def _context_menu(self, item, x, y, view):
        menu = tk.Menu(self.root, tearoff=0, bg=self.colors["surface"], fg=self.colors["text"], activebackground=self.colors["accent_soft"])
        if item:
            menu.add_command(label="Повернуть\tR", command=self._rotate)
            menu.add_command(label="Дублировать\tCtrl+D", command=self._duplicate)
            align = tk.Menu(menu, tearoff=0)
            align.add_command(label="По левому краю", command=lambda: self._align_selected("x", "min"))
            align.add_command(label="По правому краю", command=lambda: self._align_selected("x", "max"))
            align.add_command(label="По верхнему краю", command=lambda: self._align_selected("y", "min"))
            align.add_command(label="По нижнему краю", command=lambda: self._align_selected("y", "max"))
            menu.add_cascade(label="Выровнять", menu=align)
            if view == "plan":
                menu.add_command(label="Открыть схему объекта", command=lambda: self._open_object(item))
            menu.add_separator()
            menu.add_command(label="Удалить\tDelete", command=self._delete)
        else:
            menu.add_command(label="Выбор\tEsc", command=self._select_mode)
            menu.add_command(label="Вписать лист\tF", command=self._fit_sheet)
            menu.add_command(label="Сетка\tG", command=lambda: self._grid(not self.plan.show_grid))
        menu.tk_popup(x, y)

    def _snapshot(self):
        if self.view == "scheme":
            self._store_sheet()
        return {
            "scheme": self._loose,
            "plan": self.plan.dump(),
        }

    def _apply_snapshot(self, data):
        self._inside = None
        self._loose = data.get("scheme") or {"items": [], "wires": []}
        self.scheme.load(self._loose)
        self.plan.load(data.get("plan") or {})
        self._site_l.set("%g" % self.plan.length_m)
        self._site_w.set("%g" % self.plan.width_m)
        self._show(self.view)

    def _confirm_drop(self):
        if not self.dirty:
            return True
        answer = messagebox.askyesnocancel("ПВК", "Сохранить текущий лист?")
        if answer is None:
            return False
        if answer:
            return self._save()
        return True

    def _new(self):
        if not self._confirm_drop():
            return
        self.scheme.clear()
        self.plan.clear()
        self._inside = None
        self._loose = {"items": [], "wires": []}
        self.path = None
        self.dirty = False
        self._site_l.set("200")
        self._site_w.set("150")
        self._clear_props()
        self._set_status("Новый лист")
        self._reset_history()

    def _open(self):
        if not self._confirm_drop():
            return
        path = filedialog.askopenfilename(
            parent=self.root,
            filetypes=[("Лист ПВК", "*.json"), ("Все файлы", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError):
            messagebox.showerror("ПВК", "Не удалось открыть файл")
            return
        self._apply_snapshot(data)
        self.path = path
        self._reset_history()
        self._set_status(path)

    def _save(self):
        if not self.path:
            return self._save_as()
        return self._write(self.path)

    def _save_as(self):
        path = filedialog.asksaveasfilename(
            parent=self.root,
            defaultextension=".json",
            filetypes=[("Лист ПВК", "*.json")],
        )
        if not path:
            return False
        return self._write(path)

    def _write(self, path):
        try:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(self._snapshot(), fh, ensure_ascii=False, indent=2)
        except OSError:
            messagebox.showerror("ПВК", "Не удалось сохранить файл")
            return False
        self.path = path
        self._save_history_index = self._history_index
        self.dirty = False
        self._set_status("Сохранено")
        return True

    def _quit(self):
        if not self._confirm_drop():
            return
        self.root.destroy()

    def _about(self):
        messagebox.showinfo("ПВК", "ПВК\nСхема объекта и план площадки.")
