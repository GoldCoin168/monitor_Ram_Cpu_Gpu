import tkinter as tk
import psutil
import subprocess

# ---------------- SETTINGS ----------------
UPDATE_MS = 1000
FONT = ("Segoe UI", 12, "bold")

BG = "#181818"
FG = "#FFFFFF"

WINDOW_X = 30
WINDOW_Y = 30
# ------------------------------------------


class PerformanceMonitor:
    def __init__(self):
        self.root = tk.Tk()

        self.root.title("Performance Monitor")
        self.root.configure(bg=BG)

        # Remove Windows title bar
        self.root.overrideredirect(True)

        # Always on top
        self.root.attributes("-topmost", True)

        # Slight transparency
        self.root.attributes("-alpha", 0.92)

        # Starting position
        self.root.geometry(f"+{WINDOW_X}+{WINDOW_Y}")

        self.label = tk.Label(
            self.root,
            text="Loading...",
            font=FONT,
            bg=BG,
            fg=FG,
            justify="left",
            padx=14,
            pady=8
        )

        self.label.pack()

        # Drag window with left mouse button
        self.label.bind("<Button-1>", self.start_drag)
        self.label.bind("<B1-Motion>", self.drag)

        # Right click = exit
        self.label.bind("<Button-3>", lambda event: self.root.destroy())

        # Initialize CPU measurement
        psutil.cpu_percent(interval=None)

        self.update_stats()

    # --------------------------------------------------
    # GPU
    # --------------------------------------------------

    def get_gpu_stats(self):
        try:
            command = [
                "nvidia-smi",
                "--query-gpu=utilization.gpu,memory.used,memory.total",
                "--format=csv,noheader,nounits"
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=2
            )

            if result.returncode != 0:
                return None

            # Use first GPU
            line = result.stdout.strip().splitlines()[0]

            gpu_usage, memory_used, memory_total = [
                float(x.strip()) for x in line.split(",")
            ]

            return {
                "usage": gpu_usage,
                "memory_used": memory_used / 1024,
                "memory_total": memory_total / 1024
            }

        except Exception:
            return None

    # --------------------------------------------------
    # Update display
    # --------------------------------------------------

    def update_stats(self):

        # RAM
        ram = psutil.virtual_memory()

        ram_total = ram.total / (1024 ** 3)
        ram_used = ram.used / (1024 ** 3)
        ram_percent = ram.percent

        # CPU
        cpu_percent = psutil.cpu_percent(interval=None)

        # GPU
        gpu = self.get_gpu_stats()

        if gpu:
            gpu_text = (
                f"GPU   {gpu['usage']:.0f}%"
                f"   •   VRAM {gpu['memory_used']:.1f} / "
                f"{gpu['memory_total']:.1f} GB"
            )
        else:
            gpu_text = "GPU   N/A"

        # Final display
        text = (
            f"RAM   {ram_used:.1f} / {ram_total:.1f} GB"
            f"   •   {ram_percent:.0f}%\n"
            f"CPU   {cpu_percent:.0f}%\n"
            f"{gpu_text}"
        )

        self.label.config(text=text)

        self.root.after(UPDATE_MS, self.update_stats)

    # --------------------------------------------------
    # Window dragging
    # --------------------------------------------------

    def start_drag(self, event):
        self.drag_x = event.x
        self.drag_y = event.y

    def drag(self, event):
        x = self.root.winfo_pointerx() - self.drag_x
        y = self.root.winfo_pointery() - self.drag_y

        self.root.geometry(f"+{x}+{y}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    PerformanceMonitor().run()