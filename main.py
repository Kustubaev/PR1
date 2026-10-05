import tkinter as tk

from window import App


def main():
    root = tk.Tk()
    try:
        App(root)
    except Exception:
        import traceback
        from tkinter import messagebox

        messagebox.showerror("ПВК", traceback.format_exc())
        return
    root.geometry("1280x760+80+60")
    root.update_idletasks()
    root.deiconify()
    root.lift()
    try:
        root.attributes("-topmost", True)
        root.after(800, lambda: root.attributes("-topmost", False))
    except tk.TclError:
        pass
    try:
        root.focus_force()
    except tk.TclError:
        pass
    root.mainloop()


if __name__ == "__main__":
    main()
