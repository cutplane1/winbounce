import win32gui, win32con, win32api
import time, sys

class PhysicsWindow:
    def __init__(self, hwnd):
        self.hwnd = hwnd
        self.velocity = (0.0, 0.0)
        self.dragging = False
        self.drag_offset = (0, 0)
        self.last_cursor_pos = (0, 0)
        self.update_position()

    def update_position(self):
        rect = win32gui.GetWindowRect(self.hwnd)
        self.x, self.y = rect[0], rect[1]
        self.width, self.height = rect[2]-self.x, rect[3]-self.y

def is_window_maximized(hwnd):
    placement = win32gui.GetWindowPlacement(hwnd)
    return placement[1] == win32con.SW_SHOWMAXIMIZED

class WindowPhysicsEngine:
    def __init__(self):
        self.gravity = 0.8
        self.bounce = 0.65
        self.friction = 0.96
        self.windows = []
        self.temp_windows = []
        self.screen_width = win32api.GetSystemMetrics(0)
        self.screen_height = win32api.GetSystemMetrics(1) - 30

    def add_window(self, hwnd):
        if win32gui.IsWindowVisible(hwnd):
            self.windows.append(PhysicsWindow(hwnd))

    def handle_input(self):
        self.temp_windows = [w for w in self.windows if win32gui.IsWindow(w.hwnd) and not is_window_maximized(w.hwnd)]
        cursor_pos = win32api.GetCursorPos()
        left_down = win32api.GetAsyncKeyState(win32con.VK_LBUTTON) < 0

        if left_down and not any(w.dragging for w in self.temp_windows):
            hwnd = win32gui.WindowFromPoint(cursor_pos)
            top_hwnd = win32gui.GetAncestor(hwnd, win32con.GA_ROOT)
            
            for w in self.temp_windows:
                if w.hwnd == top_hwnd:
                    w.update_position()
                    if w.x <= cursor_pos[0] <= w.x + w.width and w.y <= cursor_pos[1] <= w.y + w.height:
                        w.dragging = True
                        w.drag_offset = (cursor_pos[0] - w.x, cursor_pos[1] - w.y)
                        w.last_cursor_pos = cursor_pos
                    break
        elif left_down:
            for w in self.temp_windows:
                if w.dragging:
                    dx = cursor_pos[0] - w.last_cursor_pos[0]
                    dy = cursor_pos[1] - w.last_cursor_pos[1]
                    w.velocity = (dx * 0.7, dy * 0.7)
                    w.x = cursor_pos[0] - w.drag_offset[0]
                    w.y = cursor_pos[1] - w.drag_offset[1]
                    self._move_window(w)
                    w.last_cursor_pos = cursor_pos
        else:
            for w in self.temp_windows:
                w.dragging = False

    def update_physics(self):
        for w in self.temp_windows:
            if w.dragging:
                continue

            vx, vy = w.velocity
            vy += self.gravity
            new_x = w.x + vx
            new_y = w.y + vy

            if new_x < 0 or new_x + w.width > self.screen_width:
                new_x = max(0, min(self.screen_width - w.width, new_x))
                vx = -vx * self.bounce
            if new_y < 0 or new_y + w.height > self.screen_height:
                new_y = max(0, min(self.screen_height - w.height, new_y))
                vy = -vy * self.bounce

            w.velocity = (vx * self.friction, vy * self.friction)
            w.x, w.y = new_x, new_y
            self._move_window(w)

    def _move_window(self, w):
        try:
            win32gui.MoveWindow(w.hwnd, int(w.x), int(w.y), w.width, w.height, True)
        except Exception as e:
            print(f"Move error: {e}")


def list_all_windows():
    def callback(hwnd, windows):
        text = win32gui.GetWindowText(hwnd)
        # :(((((((((((((((((((((((
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) and text != "Параметры" and text != "Медиаплеер" and text != "Microsoft Text Input Application" and text != "Program Manager":
            windows.append((hwnd, text))
        return True

    windows = []
    win32gui.EnumWindows(callback, windows)
    return windows

def main():
    engine = WindowPhysicsEngine()

    for hwnd, _ in list_all_windows():
        engine.add_window(hwnd)

    try:
        while True:
            engine.handle_input()
            engine.update_physics()
            time.sleep(1/60)
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()
