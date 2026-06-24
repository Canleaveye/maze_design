# 交互式迷宫可视化 —— Tkinter GUI
# 支持：算法切换 / 逐帧回放 / DP 路径 / 悬停查看 / 缩放

import tkinter as tk
from tkinter import ttk
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from maze import Maze, WALL, PATH, START, END, COIN, TRAP, BOSS
from generators.backtrack_dfs import generate_maze_backtrack_dfs
from generators.divide_conquer import generate_maze_divide_conquer
from generators.greedy import generate_maze_greedy
from generators.branch_bound_bfs import generate_maze_branch_bound_bfs
from dp_collector import collect_resources
from utils import analyze_maze


class InteractiveMaze:
    """交互式迷宫可视化应用"""

    COLORS = {
        WALL: '#2d2d5e', PATH: '#e8e8e8', START: '#00e676',
        END: '#ff1744', COIN: '#ffd600', TRAP: '#9c27b0', BOSS: '#ff6d00',
    }
    NAMES = {
        WALL: 'WALL', PATH: 'PATH', START: 'START', END: 'END',
        COIN: 'COIN(+50)', TRAP: 'TRAP(-30)', BOSS: 'BOSS',
    }

    ALGOS = [
        ("DFS Backtracking", "dfs", generate_maze_backtrack_dfs),
        ("Divide & Conquer", "dc", generate_maze_divide_conquer),
        ("Greedy Kruskal", "kruskal", generate_maze_greedy),
        ("Branch & Bound BFS", "bfs", generate_maze_branch_bound_bfs),
    ]

    def __init__(self, root):
        self.root = root
        self.root.title("Maze Interactive — 迷宫交互式可视化")
        self.root.configure(bg='#16213e')

        self.n = 15
        self.cell_size = 28
        self.current_algo = 0
        self.current_frame = 0
        self.playing = False
        self.show_dp = True
        self.datasets = []

        self._build_ui()
        self._load_data()

    # ────── 数据加载 ──────────────────────────────────

    def _capture_states(self, gen_func):
        maze = Maze(self.n)
        states = []

        def on_step(m, cx, cy):
            grid_copy = [row[:] for row in m.maze]
            states.append({"grid": grid_copy, "current": (cx, cy)})

        gen_func(maze, on_step=on_step)
        states.append({"grid": [row[:] for row in maze.maze], "current": None})
        return maze, states

    def _load_data(self):
        for label, key, gen_func in self.ALGOS:
            maze, states = self._capture_states(gen_func)
            max_gold, path_walk = collect_resources(maze)
            analysis = analyze_maze(maze)
            self.datasets.append({
                "label": label,
                "states": states,
                "dpGold": max_gold,
                "dpPath": path_walk,
                "analysis": analysis,
                "start": maze.start,
                "end": maze.end,
            })
        self._update_view()

    # ────── UI 构建 ───────────────────────────────────

    def _build_ui(self):
        # 顶部工具栏
        toolbar = tk.Frame(self.root, bg='#0f3460', pady=6)
        toolbar.pack(fill=tk.X)

        tk.Label(toolbar, text="Algorithm:", bg='#0f3460', fg='#ccc',
                 font=('Microsoft YaHei', 11)).pack(side=tk.LEFT, padx=(12, 6))

        self.algo_var = tk.StringVar(value=self.ALGOS[0][0])
        self.algo_menu = ttk.Combobox(toolbar, textvariable=self.algo_var,
                                       values=[a[0] for a in self.ALGOS],
                                       state='readonly', width=22)
        self.algo_menu.pack(side=tk.LEFT, padx=4)
        self.algo_menu.bind('<<ComboboxSelected>>', self._on_algo_change)

        # 信息面板
        self.info_frame = tk.Frame(self.root, bg='#1a1a2e', pady=4)
        self.info_frame.pack(fill=tk.X)
        self.info_labels = {}
        for i, key in enumerate(['deadEnds', 'avgBranching', 'pathLength', 'maxDepth', 'dpGold']):
            tk.Label(self.info_frame, text=key + ':', bg='#1a1a2e', fg='#888',
                     font=('Consolas', 10)).grid(row=0, column=i * 2, padx=(12, 2))
            lb = tk.Label(self.info_frame, text='-', bg='#1a1a2e', fg='#00bcd4',
                          font=('Consolas', 11, 'bold'))
            lb.grid(row=0, column=i * 2 + 1, padx=(0, 12))
            self.info_labels[key] = lb

        # Canvas
        self.canvas_frame = tk.Frame(self.root, bg='#1a1a2e')
        self.canvas_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=6)
        canvas_size = self.n * self.cell_size
        self.canvas = tk.Canvas(self.canvas_frame, width=canvas_size, height=canvas_size,
                                bg='#111', highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind('<Motion>', self._on_hover)

        # 控制栏
        ctrl = tk.Frame(self.root, bg='#0f3460', pady=6)
        ctrl.pack(fill=tk.X)

        btn_style = {'bg': '#1a1a2e', 'fg': '#ccc', 'font': ('Microsoft YaHei', 10),
                     'relief': 'flat', 'padx': 12, 'pady': 4, 'bd': 0,
                     'activebackground': '#e94560', 'activeforeground': '#fff'}

        tk.Button(ctrl, text='Play', command=self._play, **btn_style).pack(side=tk.LEFT, padx=(12, 4))
        tk.Button(ctrl, text='Pause', command=self._pause, **btn_style).pack(side=tk.LEFT, padx=4)
        tk.Button(ctrl, text='Reset', command=self._reset, **btn_style).pack(side=tk.LEFT, padx=4)
        tk.Button(ctrl, text='Step', command=self._step, **btn_style).pack(side=tk.LEFT, padx=4)
        tk.Button(ctrl, text='Final', command=self._goto_final, **btn_style).pack(side=tk.LEFT, padx=4)

        # 帧滑块
        self.frame_var = tk.IntVar(value=0)
        self.frame_slider = tk.Scale(ctrl, from_=0, to=0, orient=tk.HORIZONTAL,
                                      variable=self.frame_var, command=self._on_slider,
                                      bg='#0f3460', fg='#ccc', troughcolor='#1a1a2e',
                                      length=350, showvalue=False)
        self.frame_slider.pack(side=tk.LEFT, padx=10)

        self.frame_label = tk.Label(ctrl, text='0/0', bg='#0f3460', fg='#00bcd4',
                                     font=('Consolas', 11))
        self.frame_label.pack(side=tk.LEFT)

        # DP 切换
        self.dp_var = tk.BooleanVar(value=True)
        tk.Checkbutton(ctrl, text='DP Path', variable=self.dp_var,
                       command=self._draw, bg='#0f3460', fg='#ccc',
                       selectcolor='#1a1a2e',
                       activebackground='#0f3460', activeforeground='#fff',
                       font=('Microsoft YaHei', 10)).pack(side=tk.RIGHT, padx=12)

        # 缩放
        tk.Button(ctrl, text='+', command=self._zoom_in, **btn_style).pack(side=tk.RIGHT, padx=2)
        tk.Button(ctrl, text='-', command=self._zoom_out, **btn_style).pack(side=tk.RIGHT, padx=2)

        # 图例
        legend = tk.Frame(self.root, bg='#1a1a2e', pady=4)
        legend.pack(fill=tk.X)
        for val, color in [(WALL, '#2d2d5e'), (PATH, '#e8e8e8'), (START, '#00e676'),
                            (END, '#ff1744'), (COIN, '#ffd600'), (TRAP, '#9c27b0'),
                            (BOSS, '#ff6d00')]:
            f = tk.Frame(legend, bg='#1a1a2e')
            f.pack(side=tk.LEFT, padx=8)
            tk.Label(f, text='  ', bg=color, width=2).pack(side=tk.LEFT)
            tk.Label(f, text=self.NAMES[val], bg='#1a1a2e', fg='#aaa',
                     font=('Microsoft YaHei', 9)).pack(side=tk.LEFT, padx=2)

    # ────── 绘制 ──────────────────────────────────────

    def _draw(self, *_):
        self.show_dp = self.dp_var.get()
        d = self.datasets[self.current_algo]
        state = d["states"][self.current_frame]
        grid = state["grid"]
        cs = self.cell_size

        self.canvas.delete('all')
        n = len(grid)

        # 批量画矩形（快于逐个 fill_rect）
        for i in range(n):
            for j in range(n):
                val = grid[i][j]
                color = self.COLORS.get(val, '#000')
                x1, y1 = j * cs, i * cs
                self.canvas.create_rectangle(x1, y1, x1 + cs, y1 + cs,
                                              fill=color, outline='#444', width=1)

        # 当前位置高亮
        if state["current"]:
            cx, cy = state["current"]
            x1, y1 = cy * cs + 3, cx * cs + 3
            self.canvas.create_rectangle(x1, y1, x1 + cs - 6, y1 + cs - 6,
                                          fill='#00b0ff', outline='', stipple='gray50')

        # DP 路径
        if self.show_dp and d["dpPath"]:
            path = d["dpPath"]
            pts = [(p[1] * cs + cs / 2, p[0] * cs + cs / 2) for p in path]
            for k in range(len(pts) - 1):
                self.canvas.create_line(pts[k][0], pts[k][1], pts[k + 1][0], pts[k + 1][1],
                                         fill='#00bcd4', width=2, capstyle=tk.ROUND)

    def _update_view(self):
        d = self.datasets[self.current_algo]
        a = d["analysis"]
        self.info_labels['deadEnds'].config(text=str(a['deadEnds']))
        self.info_labels['avgBranching'].config(text=str(a['avgBranching']))
        self.info_labels['pathLength'].config(text=str(a['pathLength']))
        self.info_labels['maxDepth'].config(text=str(a['maxDepth']))
        self.info_labels['dpGold'].config(text=str(d['dpGold']))

        total = len(d["states"]) - 1
        self.frame_slider.configure(to=total)
        self.frame_var.set(min(self.current_frame, total))
        self.frame_label.config(text=f'{self.current_frame}/{total}')
        self._draw()

    # ────── 事件处理 ──────────────────────────────────

    def _on_algo_change(self, *_):
        idx = self.algo_menu.current()
        if idx >= 0:
            self.current_algo = idx
            self.current_frame = 0
            self._update_view()

    def _play(self):
        if not self.playing:
            self.playing = True
            self._tick()

    def _tick(self):
        if not self.playing:
            return
        d = self.datasets[self.current_algo]
        self.current_frame = (self.current_frame + 1) % len(d["states"])
        self.frame_var.set(self.current_frame)
        self.frame_label.config(text=f'{self.current_frame}/{len(d["states"]) - 1}')
        self._draw()
        self.root.after(50, self._tick)

    def _pause(self):
        self.playing = False

    def _reset(self):
        self.playing = False
        self.current_frame = 0
        self.frame_var.set(0)
        self._update_view()

    def _step(self):
        d = self.datasets[self.current_algo]
        self.current_frame = min(self.current_frame + 1, len(d["states"]) - 1)
        self.frame_var.set(self.current_frame)
        self._update_view()

    def _goto_final(self):
        d = self.datasets[self.current_algo]
        self.current_frame = len(d["states"]) - 1
        self.frame_var.set(self.current_frame)
        self._update_view()

    def _on_slider(self, *_):
        self.current_frame = self.frame_var.get()
        self.frame_label.config(text=f'{self.current_frame}/{len(self.datasets[self.current_algo]["states"]) - 1}')
        self._draw()

    def _on_hover(self, event):
        cs = self.cell_size
        d = self.datasets[self.current_algo]
        state = d["states"][self.current_frame]
        grid = state["grid"]
        n = len(grid)
        j = event.x // cs
        i = event.y // cs
        if 0 <= i < n and 0 <= j < n:
            val = grid[i][j]
            name = self.NAMES.get(val, '?')
            self.canvas_frame.master.title(
                f"Maze Interactive — ({i},{j}) {name}")
        else:
            self.canvas_frame.master.title("Maze Interactive")

    def _zoom_in(self):
        self.cell_size = min(50, self.cell_size + 2)
        sz = self.n * self.cell_size
        self.canvas.config(width=sz, height=sz)
        self._draw()

    def _zoom_out(self):
        self.cell_size = max(10, self.cell_size - 2)
        sz = self.n * self.cell_size
        self.canvas.config(width=sz, height=sz)
        self._draw()


def run_interactive():
    root = tk.Tk()
    root.geometry("600x700")
    app = InteractiveMaze(root)
    root.mainloop()


if __name__ == '__main__':
    run_interactive()
