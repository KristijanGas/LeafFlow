import tkinter as tk
import math

class gameCanvas(tk.Frame):
    def __init__(self, parent, main_menu_callback,reset_edges_callback,player_edge_assign,check_result,next_level,current_level, **kwargs):
        super().__init__(parent, **kwargs)

        self.main_menu_callback = main_menu_callback
        self.edges = []  # (from_id, to_id, direction, color)
        self.current_level = current_level
        self.canvas = tk.Canvas(self, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.back_button = tk.Button(self, text="Back to Main Menu", command=self.main_menu_callback)
        self.back_button.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=10)

        self.default_radius = 15
        self.nodes = {}  # node_id: (norm_x, norm_y, scale)

        self.node_id_by_item = {}
        self.node_item_by_id = {}
        self.node_number_text = {}   # node_id → canvas text item id
        self.node_number_value = {}  # node_id → number to display
        self.start_node = None


        self.edge_callback = player_edge_assign
        self.next_level = next_level
        self.check_result_callback = check_result
        self.reset_edges_callback = reset_edges_callback

        self.zoom = 1.0
        self.pan_offset = [0.0, 0.0]  # Normalized offset
        self.is_panning = False
        self.last_drag_pos = None

        self.level_display = tk.Label(self, text=f"Level: {self.current_level}", font=("Arial", 12))
        self.level_display.place(relx=0.0, rely=0.0, anchor='nw', x=10, y=80)

        self.reset_button = tk.Button(self, text="Reset View", command=self.resetView)
        self.reset_button.place(relx=0.0, rely=0.0, anchor='nw', x=10, y=10)
        # Reset Edges button (to the left of Back button)
        self.reset_edges_button = tk.Button(self, text="Restart", command=self._on_reset_edges)
        self.reset_edges_button.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=50)

        # Check Result button (to the left of Reset Edges button)
        self.check_result_button = tk.Button(self, text="Check Result", command=self._on_check_result)
        self.check_result_button.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=90)
        self.attempts = 0
        self.attempts_label = tk.Label(self, text="Attempts: 0", font=("Arial", 10))
        self.attempts_label.place(relx=0.0, rely=0.0, anchor='nw', x=10, y=45)  # adjust y as needed
        # Right-click drag-to-pan bindings
        self.canvas.bind("<ButtonPress-3>", self._on_pan_start)
        self.canvas.bind("<B3-Motion>", self._on_pan_move)
        self.canvas.bind("<ButtonRelease-3>", self._on_pan_end)

        self.canvas.bind("<Configure>", self._on_resize)
        #self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<ButtonRelease-1>", self._on_canvas_release)
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)  # Windows/macOS
        self.canvas.bind("<Button-4>", self._on_mouse_wheel)    # Linux scroll up
        self.canvas.bind("<Button-5>", self._on_mouse_wheel)    # Linux scroll down

    def solved_correctly(self):
        """Show a centered popup with success message and action buttons."""
        popup = tk.Toplevel(self)
        popup.transient(self)
        popup.grab_set()
        popup.title("Level Complete")

        # Define popup size
        width = 600
        height = 200

        # Center the popup in the parent window
        x = self.winfo_rootx() + (self.winfo_width() - width) // 2
        y = self.winfo_rooty() + (self.winfo_height() - height) // 2
        popup.geometry(f"{width}x{height}+{x}+{y}")

        # Optional: prevent resizing
        popup.resizable(False, False)

        # Label
        label = tk.Label(popup, text="🎉 Tree Solved! 🎉", font=("Arial", 18, "bold"))
        label.pack(pady=20)

        # Buttons Frame
        button_frame = tk.Frame(popup)
        button_frame.pack(pady=10)

        # Buttons
        tk.Button(button_frame, text="Main Menu", width=12,
                command=lambda: [popup.destroy(), self.main_menu_callback()]).grid(row=0, column=0, padx=5)

        tk.Button(button_frame, text="Restart", width=12,
                command=lambda: [popup.destroy(), self.reset_edges_callback() if self.reset_edges_callback else None]).grid(row=0, column=1, padx=5)

        tk.Button(button_frame, text="Next Level", width=12,
                command=lambda: [popup.destroy(), self.next_level() if self.next_level else None]).grid(row=0, column=2, padx=5)

    def solved_incorrectly(self, node_list):
        """Show a failure message and color specified nodes red."""
        self.attempts += 1
        self.attempts_label.config(text=f"Attempts: {self.attempts}")

        # Display "Tree Failed" at the top
        self.canvas.create_text(
            self.canvas.winfo_width() // 2, 20,
            text="Tree Failed", fill="red",
            font=("Arial", 16, "bold")
        )

        # Color the specified nodes red
        for node_id in node_list:
            if node_id in self.node_item_by_id:
                self.canvas.itemconfig(self.node_item_by_id[node_id], fill="red")

    def _on_check_result(self):
        if self.check_result_callback:
            self.check_result_callback()

    def _on_reset_edges(self):
        if self.reset_edges_callback:
            self.reset_edges_callback()

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
            # Redraw number if it exists
            if node_id in self.node_number_value:
                self._add_number_to_node(self.node_number_value[node_id], node_id)

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
        self.node_item_by_id[node_id] = int(oval)
        

    def _draw_edge(self, x1, y1, x2, y2, direction, color):
        self.canvas.create_line(x1, y1, x2, y2, fill=color, width=4)
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

        size = 14
        angle = math.radians(30)

        sin_a = math.sin(angle)
        cos_a = math.cos(angle)

        x1 = x - (dx * cos_a - dy * sin_a) * size
        y1 = y - (dx * sin_a + dy * cos_a) * size

        x2 = x - (dx * cos_a + dy * sin_a) * size
        y2 = y - (-dx * sin_a + dy * cos_a) * size

        self.canvas.create_line(x, y, x1, y1, fill=color, width=3)
        self.canvas.create_line(x, y, x2, y2, fill=color, width=3)


    def _on_canvas_release(self, event):
        if not self.start_node:
            return

        released_node = self._get_node_at_position(event.x, event.y)
        if released_node and released_node != self.start_node:
            #self.add_edge(self.start_node, released_node, 1, color="royalblue")
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
    def _add_number_to_node(self, number, node_id):
        """Add or update a number displayed on top of the given node."""
        #print(self.node_item_by_id)
        if node_id not in self.node_item_by_id:
            return  # Node doesn't exist

        self.node_number_value[node_id] = number  # Save for future redraws

        # Remove old number (if exists)
        if node_id in self.node_number_text:
            self.canvas.delete(self.node_number_text[node_id])

        # Get the node's center position
        oval_id = self.node_item_by_id[node_id]
        bbox = self.canvas.bbox(oval_id)
        if not bbox:
            return

        cx = (bbox[0] + bbox[2]) / 2
        cy = (bbox[1] + bbox[3]) / 2

        # Scale font size based on zoom and canvas size
        canvas_size = min(self.canvas.winfo_width(), self.canvas.winfo_height())
        font_size = int(14 * self.zoom * (canvas_size / 400)*self.nodes[node_id][2])
        #font_size = max(6, font_size)  # minimum readable size

        # Create the number text
        text_id = self.canvas.create_text(
            cx, cy, text=str(number),
            fill="black", font=("Arial", font_size, "bold"),
            state="disabled"  # <- makes the text ignore mouse events
        )

        self.node_number_text[node_id] = text_id

    def _remove_number_from_node(self, node_id):
        """Remove the number displayed on the given node, if any."""
        # Remove canvas text item
        if node_id in self.node_number_text:
            self.canvas.delete(self.node_number_text[node_id])
            del self.node_number_text[node_id]

        # Remove stored number value
        if node_id in self.node_number_value:
            del self.node_number_value[node_id]