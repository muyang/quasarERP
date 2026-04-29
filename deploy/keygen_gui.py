#!/usr/bin/env python3
"""
Quasar ERP — 授权注册机 (图形界面)
- 从已有授权池中随机抽取可用授权码
- 输入 1-10 生成对应数量
- 一码一机，生成后即标记为已分配
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import sys
import random
from datetime import datetime

LICENSE_DIR = os.path.dirname(os.path.abspath(__file__))
LICENSE_FILE = os.path.join(LICENSE_DIR, "licenses.txt")

# ── data helpers ──────────────────────────────────


def get_pool():
    """返回 (available_keys_list, used_keys_list)"""
    available = []
    used = []
    if not os.path.exists(LICENSE_FILE):
        return available, used
    with open(LICENSE_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) >= 2 and parts[1] == "available":
                available.append(parts[0])
            else:
                used.append(line)
    return available, used


def save_pool(available_keys, used_keys):
    """写回授权文件"""
    with open(LICENSE_FILE, "w") as f:
        for k in available_keys:
            f.write(f"{k},available\n")
        for entry in used_keys:
            f.write(f"{entry}\n")


def generate_keys(n):
    """从可用池中随机取 n 个，标记为 assigned 并返回"""
    available, used = get_pool()
    if n > len(available):
        return None, len(available)

    chosen = random.sample(available, n)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    remain = [k for k in available if k not in chosen]
    for key in chosen:
        used.append(f"{key},assigned,{timestamp},generator")

    save_pool(remain, used)
    return chosen, len(remain)


# ── GUI ───────────────────────────────────────────


class KeygenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quasar ERP — 授权注册机 / License Keygen")
        self.root.geometry("620x560")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a2e")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self._setup_styles()

        self._build_ui()
        self._refresh_stats()

    def _setup_styles(self):
        c = {
            "bg": "#1a1a2e",
            "fg": "#e0e0e0",
            "card": "#16213e",
            "accent": "#0f3460",
            "green": "#00c853",
            "gold": "#ffd600",
            "red": "#ff1744",
        }
        self.c = c

        self.style.configure("TFrame", background=c["bg"])
        self.style.configure("TLabelframe", background=c["bg"], foreground=c["fg"])
        self.style.configure("TLabelframe.Label",
                             background=c["bg"], foreground=c["fg"], font=("Segoe UI", 11, "bold"))
        self.style.configure("TButton",
                             font=("Segoe UI", 10), padding=6)
        self.style.configure("TLabel", background=c["bg"], foreground=c["fg"])
        self.style.configure("Card.TFrame", background=c["card"])

    def _build_ui(self):
        c = self.c

        # ── Title Bar ──
        title_frame = tk.Frame(self.root, bg=c["accent"], height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        tk.Label(title_frame, text="Quasar ERP — 授权注册机",
                 bg=c["accent"], fg="white", font=("Segoe UI", 18, "bold")).pack(expand=True)

        # ── Stats Cards ──
        stats_frame = ttk.Frame(self.root)
        stats_frame.pack(fill=tk.X, padx=16, pady=(12, 6))

        self.card_total = self._make_card(stats_frame, "总授权数", "5,000", c["fg"])
        self.card_total.pack(side=tk.LEFT, expand=True, padx=4)
        self.card_avail = self._make_card(stats_frame, "可用 / Available", "0", c["green"])
        self.card_avail.pack(side=tk.LEFT, expand=True, padx=4)
        self.card_used = self._make_card(stats_frame, "已用 / Used", "0", c["gold"])
        self.card_used.pack(side=tk.LEFT, expand=True, padx=4)

        # ── Generate Controls ──
        ctrl_frame = ttk.Frame(self.root)
        ctrl_frame.pack(fill=tk.X, padx=16, pady=(10, 6))

        ttk.Label(ctrl_frame, text="生成数量 (1-10):",
                  font=("Segoe UI", 12)).pack(side=tk.LEFT, padx=(0, 8))

        self.spin_var = tk.StringVar(value="1")
        self.spin = ttk.Spinbox(ctrl_frame, from_=1, to=10, width=5,
                                textvariable=self.spin_var, font=("Segoe UI", 14))
        self.spin.pack(side=tk.LEFT, padx=4)

        self.btn_gen = tk.Button(ctrl_frame, text="生成 / Generate",
                                 bg=c["green"], fg="white",
                                 font=("Segoe UI", 12, "bold"),
                                 padx=16, pady=4, border=0, cursor="hand2",
                                 command=self.do_generate)
        self.btn_gen.pack(side=tk.LEFT, padx=12)

        self.btn_export = tk.Button(ctrl_frame, text="导出全部 / Export All",
                                    bg=c["accent"], fg="white",
                                    font=("Segoe UI", 10),
                                    padx=10, pady=4, border=0, cursor="hand2",
                                    command=self.do_export)
        self.btn_export.pack(side=tk.RIGHT, padx=4)

        # ── Result Area ──
        result_frame = ttk.LabelFrame(self.root, text=" 生成结果 / Generated Keys ",
                                      padding=8)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(4, 10))

        self.output = scrolledtext.ScrolledText(
            result_frame, height=12, font=("Consolas", 12),
            bg="#0d1117", fg="#58a6ff", insertbackground="white",
            relief=tk.FLAT, borderwidth=0, padx=10, pady=10
        )
        self.output.pack(fill=tk.BOTH, expand=True)

        # ── Status Bar ──
        self.status_var = tk.StringVar(value="就绪 / Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var,
                              anchor=tk.W, bg=c["accent"], fg="white",
                              font=("Segoe UI", 9), padx=10, pady=3)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def _make_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg=self.c["card"], padx=12, pady=10,
                        highlightbackground=self.c["accent"], highlightthickness=1)
        tk.Label(card, text=title, bg=self.c["card"], fg=self.c["fg"],
                 font=("Segoe UI", 9)).pack()
        lbl = tk.Label(card, text=value, bg=self.c["card"], fg=color,
                       font=("Segoe UI", 22, "bold"))
        lbl.pack()
        card.lbl_value = lbl
        return card

    def _refresh_stats(self):
        available, used_keys = get_pool()
        total = len(available) + len(used_keys)
        self.card_total.lbl_value.config(text=f"{total:,}")
        self.card_avail.lbl_value.config(text=f"{len(available):,}")
        self.card_used.lbl_value.config(text=f"{len(used_keys):,}")

    def do_generate(self):
        try:
            n = int(self.spin_var.get())
        except ValueError:
            messagebox.showwarning("输入错误", "请输入 1 到 10 的数字。")
            return
        if n < 1 or n > 10:
            messagebox.showwarning("输入错误", "请输入 1 到 10 的数字。")
            return

        keys, remaining = generate_keys(n)
        if keys is None:
            messagebox.showerror("授权不足",
                                 f"可用授权码仅剩 {remaining} 个，无法生成 {n} 个。")
            return

        self.output.delete(1.0, tk.END)
        self.output.insert(tk.END, f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.output.insert(tk.END, f"生成数量: {n}\n")
        self.output.insert(tk.END, "─" * 45 + "\n\n")
        for i, key in enumerate(keys, 1):
            self.output.insert(tk.END, f"  [{i:02d}]  {key}\n")
        self.output.insert(tk.END, "\n" + "─" * 45 + "\n")
        self.output.insert(tk.END, f"剩余可用: {remaining:,} 个\n")

        self._refresh_stats()
        self.status_var.set(f"已生成 {n} 个授权码 | 剩余 {remaining} 个可用")

    def do_export(self):
        available, used = get_pool()
        export_path = os.path.join(LICENSE_DIR, "available_keys.txt")
        with open(export_path, "w") as f:
            for k in available:
                f.write(k + "\n")
        messagebox.showinfo("导出完成",
                            f"已导出 {len(available)} 个可用授权码至:\n{export_path}")


def main():
    root = tk.Tk()
    app = KeygenApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
