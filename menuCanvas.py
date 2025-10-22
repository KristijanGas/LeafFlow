
import json
import tkinter as tk

class menuCanvas:
    def __init__(self, root, load_level_callback, freeplay_callback):
        self.root = root
        self.load_level = load_level_callback
        self.freeplay_callback = freeplay_callback
        self.current_level = 1

    def main_menu(self):
        self.clear_window()

        self.root.configure(bg="#e0f2e9")  # Soft forest green theme

        # === TITLE ===
        title = tk.Label(self.root, text="LeafFlow", font=("Georgia", 32, "bold"),
                        bg="#e0f2e9", fg="#2e4d2e")
        title.pack(pady=20)

        # === PLAY NOW BUTTON ===
        play_btn = tk.Button(self.root, text="Play Now", font=("Helvetica", 16),
                            bg="#a8d5ba", fg="black", relief=tk.RAISED, bd=3,
                            command=lambda idx=self.current_level: self.load_level(idx))
        play_btn.pack(pady=10)

        # === HOW TO PLAY BUTTON ===
        how_to_play_btn = tk.Button(self.root, text="How to Play", font=("Helvetica", 14),
                                    bg="#cce3dc", command=self.how_to_play)
        how_to_play_btn.pack(pady=5)

        # === FREEPLAY ===
        freeplay_frame = tk.Frame(self.root, bg="#e0f2e9")
        freeplay_frame.pack(pady=15)

        tk.Label(freeplay_frame, text="Freeplay Size:", bg="#e0f2e9",
                font=("Helvetica", 12)).pack(side=tk.LEFT, padx=5)

        self.freeplay_input = tk.Entry(freeplay_frame, width=5)
        self.freeplay_input.pack(side=tk.LEFT, padx=5)

        freeplay_btn = tk.Button(freeplay_frame, text="Freeplay", bg="#bcd4c1",
                                command=self.freeplay_input_size)
        freeplay_btn.pack(side=tk.LEFT, padx=5)

        # === LEVEL SELECT GRID ===
        level_frame = tk.Frame(self.root, bg="#e0f2e9")
        level_frame.pack(pady=20)
        path = "levels/main_levels/progress_track.json"
        try:
            with open(path, 'r') as f:
                self.progress = json.load(f)
            self.current_level = 1
            for i in range(40):
                if self.progress[i] == 1:
                    self.current_level = i+1
                else:
                    break
        except FileNotFoundError:
            self.current_level = 1
        
        for i in range(40):
            btn = tk.Button(level_frame, text=f"Level {i+1}", width=10, height=2,
                            bg="#e6e3d0" if self.progress[i] != 1 else "#5cc36a",
                             command=lambda idx=i: self.load_level(idx+1))
            btn.grid(row=i // 10, column=i % 10, padx=5, pady=5)

    def how_to_play(self):
        self.clear_window()

        back_btn = tk.Button(self.root, text="Back to Main Menu", font=("Arial", 14), command=self.main_menu)
        back_btn.pack(pady=10)

        #how to play
        instructions = (
            "How to Play:\n" \
            "1. Drag from node to node to direct an edge.\n" \
            "2. Consider each path from leaf to leaf. Edges on that path should all be paired up with each other.\n" \
            "3. Once all paths are satisfied, click check result and see if you win!\n"
        )
        label = tk.Label(self.root, text=instructions, font=("Arial", 18), justify=tk.LEFT)
        label.pack(pady=20)

        # Desired approximate display size
        target_width = 300
        target_height = 300

        # Create a container frame for horizontal layout
        image_frame = tk.Frame(self.root)
        image_frame.pack(pady=10)

        for i in range(3):
            path = f"images/yes{i+1}.png"
            img = tk.PhotoImage(file=path)

            # Calculate subsample factors to fit target size
            subsample_x = max(1, img.width() // target_width)
            subsample_y = max(1, img.height() // target_height)

            # Apply subsample to scale down
            img = img.subsample(subsample_x, subsample_y)

            # Create label and pack left-to-right
            img_label = tk.Label(image_frame, image=img)
            img_label.image = img  # Prevent garbage collection
            img_label.pack(side=tk.LEFT, padx=5)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    def freeplay_input_size(self):
        try:
            num = int(self.freeplay_input.get())
            if not 2 <= num <= 1000:
                raise ValueError
        except ValueError:
            tk.messagebox.showerror("Invalid Input", "Please enter a number between 2 and 100.")
            return
        self.freeplay_callback(num)
        