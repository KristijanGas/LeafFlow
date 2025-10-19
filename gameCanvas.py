import tkinter as tk
import math

class gameCanvas(tk.Frame):
    def __init__(self, parent, main_menu_callback, **kwargs):
        super().__init__(parent, **kwargs)

        self.main_menu_callback = main_menu_callback
        self.edges = []  # (from_id, to_id, direction, color)

        self.canvas = tk.Canvas(self, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.back_button = tk.Button(self, text="Back to Main Menu", command=self.main_menu_callback)
        self.back_button.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=10)

        self.default_radius = 15
        self.nodes = {}  # node_id: (norm_x, norm_y, scale)

        self.node_id_by_item = {}
        self.node_item_by_id = {}

        self.start_node = None
        self.edge_callback = None
        self.empty_click_callback = None

        self.zoom = 1.0
        self.pan_offset = [0.0, 0.0]  # Normalized offset
        self.is_panning = False
        self.last_drag_pos = None
        self.reset_button = tk.Button(self, text="Reset View", command=self.resetView)
        self.reset_button.place(relx=0.0, rely=0.0, anchor='nw', x=10, y=10)
        # Right-click drag-to-pan bindings
        self.canvas.bind("<ButtonPress-3>", self._on_pan_start)
        self.canvas.bind("<B3-Motion>", self._on_pan_move)
        self.canvas.bind("<ButtonRelease-3>", self._on_pan_end)

        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<ButtonRelease-1>", self._on_canvas_release)
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)  # Windows/macOS
        self.canvas.bind("<Button-4>", self._on_mouse_wheel)    # Linux scroll up
        self.canvas.bind("<Button-5>", self._on_mouse_wheel)    # Linux scroll down

    def _on_pan_start(self, event):
        self.is_panning = True
        self.last_drag_pos = (event.x, event.y)

    def _on_pan_move(self, event):
        if self.is_panning and self.last_drag_pos:
            dx = event.x - self.last_drag_pos[0]
            dy = event.y - self.last_drag_pos[1]

            canvas_w = self.canvas.winfo_width()
            canvas_h = self.canvas.winfo_height()
            size = min(canvas_w, canvas_h) * self.zoom

            self.pan_offset[0] -= dx / size
            self.pan_offset[1] -= dy / size

            self.last_drag_pos = (event.x, event.y)
            self._redraw()

    def _on_pan_end(self, event):
        self.is_panning = False
        self.last_drag_pos = None

    def resetView(self):
        """Reset zoom and pan to default view (1x zoom, centered)."""
        self.zoom = 1.0
        self.pan_offset = [0.0, 0.0]
        self._redraw()

    def add_node(self, node_id, norm_x, norm_y, scale=1.0):
        self.nodes[node_id] = (norm_x, norm_y, scale)
        self._redraw()

    def add_edge(self, from_id, to_id, direction=0, color="gray"):
        if from_id not in self.nodes or to_id not in self.nodes:
            return
        for i, (f, t, d, c) in enumerate(self.edges):
            if (f == from_id and t == to_id) or (f == to_id and t == from_id):
                self.edges[i] = (from_id, to_id, direction, color)
                self._redraw()
                return
        self.edges.append((from_id, to_id, direction, color))
        self._redraw()

    def on_empty_click(self, callback):
        self.empty_click_callback = callback

    def on_edge_draw(self, callback):
        self.edge_callback = callback

    def _on_resize(self, event):
        self._redraw()

    def _on_mouse_wheel(self, event):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        mx = (event.x - w) / w + 0.5
        my = (event.y - h) / h + 0.5
        mx*=1.2
        my*=1.2
        old_zoom = self.zoom
        if event.num == 5 or event.delta < 0:
            self.zoom = max(0.75, self.zoom - 0.1)
        elif event.num == 4 or event.delta > 0:
            self.zoom = min(10.0, self.zoom + 0.1)
        new_zoom = self.zoom

        # Adjust pan offset so that the point under the mouse stays fixed
        scale_change = 1 / old_zoom - 1 / new_zoom
        self.pan_offset[0] += mx * scale_change
        self.pan_offset[1] += my * scale_change

        self._redraw()

    def _redraw(self):
        self.canvas.delete("all")
        self.node_id_by_item.clear()

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        size = min(w, h) * self.zoom
        offset_x = (w - size) / 2 - self.pan_offset[0] * size
        offset_y = (h - size) / 2 - self.pan_offset[1] * size

        def to_pixel(norm_x, norm_y):
            x = offset_x + norm_x * size
            y = offset_y + norm_y * size
            return x, y

        for from_id, to_id, direction, color in self.edges:
            x1, y1, _ = self.nodes[from_id]
            x2, y2, _ = self.nodes[to_id]
            px1, py1 = to_pixel(x1, y1)
            px2, py2 = to_pixel(x2, y2)
            self._draw_edge(px1, py1, px2, py2, direction, color)

        for node_id, (nx, ny, scale) in self.nodes.items():
            x, y = to_pixel(nx, ny)
            self._draw_node(node_id, x, y, scale)

    def _draw_node(self, node_id, x, y, scale):
        size = min(self.canvas.winfo_width(), self.canvas.winfo_height()) * self.zoom
        r = self.default_radius * scale * (size / 400)

        oval = self.canvas.create_oval(
            x - r, y - r, x + r, y + r,
            fill="skyblue", outline="black"
        )
        self.canvas.tag_bind(oval, "<Button-1>", lambda e, nid=node_id: self._on_node_press(e, nid))
        self.canvas.tag_bind(oval, "<ButtonRelease-1>", lambda e, nid=node_id: self._on_node_release(nid))
        self.node_id_by_item[oval] = node_id
        self.node_item_by_id[node_id] = oval

    def _draw_edge(self, x1, y1, x2, y2, direction, color):
        self.canvas.create_line(x1, y1, x2, y2, fill=color, width=2)
        if direction == 0:
            return
        if direction == -1:
            x1, y1, x2, y2 = x2, y2, x1, y1
        num_arrows = 3
        for i in range(1, num_arrows + 1):
            t = i / (num_arrows + 1)
            ax = x1 + (x2 - x1) * t
            ay = y1 + (y2 - y1) * t
            self._draw_arrowhead(ax, ay, x2 - x1, y2 - y1, color)

    def _draw_arrowhead(self, x, y, dx, dy, color):
        length = math.hypot(dx, dy)
        if length == 0:
            return
        dx /= length
        dy /= length

        size = 8
        angle = math.radians(30)

        sin_a = math.sin(angle)
        cos_a = math.cos(angle)

        x1 = x - (dx * cos_a - dy * sin_a) * size
        y1 = y - (dx * sin_a + dy * cos_a) * size

        x2 = x - (dx * cos_a + dy * sin_a) * size
        y2 = y - (-dx * sin_a + dy * cos_a) * size

        self.canvas.create_line(x, y, x1, y1, fill=color, width=2)
        self.canvas.create_line(x, y, x2, y2, fill=color, width=2)

    def _on_canvas_click(self, event):
        clicked_items = self.canvas.find_withtag("current")
        if not clicked_items and self.empty_click_callback:
            self.empty_click_callback()

    def _on_canvas_release(self, event):
        if not self.start_node:
            return

        released_node = self._get_node_at_position(event.x, event.y)
        if released_node and released_node != self.start_node:
            self.add_edge(self.start_node, released_node, 1, color="royalblue")
            if self.edge_callback:
                self.edge_callback(self.start_node, released_node)

        self._on_node_release(self.start_node)
        self.start_node = None

    def _get_node_at_position(self, x, y):
        """Return the node_id whose center is closest to (x, y), among those under the point."""
        items = self.canvas.find_overlapping(x, y, x, y)
        closest_node = None
        closest_dist_sq = float('inf')

        for item in items:
            if item in self.node_id_by_item:
                node_id = self.node_id_by_item[item]
                # Get the bounding box of the oval
                bbox = self.canvas.bbox(item)
                if bbox:
                    cx = (bbox[0] + bbox[2]) / 2
                    cy = (bbox[1] + bbox[3]) / 2
                    dist_sq = (x - cx) ** 2 + (y - cy) ** 2
                    if dist_sq < closest_dist_sq:
                        closest_dist_sq = dist_sq
                        closest_node = node_id

        return closest_node

    def _on_node_press(self, event, node_id):
        self.start_node = node_id
        if node_id in self.node_item_by_id:
            oval = self.node_item_by_id[node_id]
            self.canvas.itemconfig(oval, fill="yellow")
        return "break"

    def _on_node_release(self, node_id):
        if node_id in self.node_item_by_id:
            oval = self.node_item_by_id[node_id]
            self.canvas.itemconfig(oval, fill="skyblue")
        return "break"
