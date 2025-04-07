import win32gui, win32con, win32api
import time

class PhysicsWindow:
    def __init__(self, hwnd):
        self.hwnd = hwnd
        self.velocity = (0.0, 0.0)
        self.dragging = False
        self.drag_offset = (0, 0)
        self.last_cursor_pos = (0, 0)
        rect = win32gui.GetWindowRect(hwnd)
        self.x, self.y = rect[0], rect[1]
        self.width, self.height = rect[2]-self.x, rect[3]-self.y

class WindowPhysicsEngine:
    def __init__(self):
        self.gravity = 0.8
        self.bounce = 0.65
        self.friction = 0.96
        self.windows = []
        self.screen_width = win32api.GetSystemMetrics(0)
        self.screen_height = win32api.GetSystemMetrics(1) - 30

    def add_window(self, hwnd):
        if win32gui.IsWindowVisible(hwnd):
            self.windows.append(PhysicsWindow(hwnd))

    def handle_input(self):
        self.windows = [w for w in self.windows if win32gui.IsWindow(w.hwnd)]
        cursor_pos = win32api.GetCursorPos()
        left_down = win32api.GetAsyncKeyState(win32con.VK_LBUTTON) < 0

        if left_down and not any(w.dragging for w in self.windows):
            for w in reversed(self.windows):
                rect = win32gui.GetWindowRect(w.hwnd)
                w.x, w.y = rect[0], rect[1]
                if w.x <= cursor_pos[0] <= w.x + w.width and w.y <= cursor_pos[1] <= w.y + w.height:
                    w.dragging = True
                    w.drag_offset = (cursor_pos[0] - w.x, cursor_pos[1] - w.y)
                    w.last_cursor_pos = cursor_pos
                    break
        elif left_down:
            for w in self.windows:
                if w.dragging:
                    dx = cursor_pos[0] - w.last_cursor_pos[0]
                    dy = cursor_pos[1] - w.last_cursor_pos[1]
                    w.velocity = (dx * 0.7, dy * 0.7)
                    w.x = cursor_pos[0] - w.drag_offset[0]
                    w.y = cursor_pos[1] - w.drag_offset[1]
                    self._move_window(w)
                    w.last_cursor_pos = cursor_pos
        else:
            for w in self.windows:
                w.dragging = False

    def update_physics(self):
        for w in self.windows:
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

def main():
    engine = WindowPhysicsEngine()
    engine.add_window(win32gui.FindWindow(None, "Безымянный – Блокнот"))
    engine.add_window(win32gui.FindWindow(None, "qBittorrent v4.6.4"))
    engine.add_window(win32gui.FindWindow(None, "Командная строка"))

    while True:
        engine.handle_input()
        engine.update_physics()
        time.sleep(1/60)

if __name__ == "__main__":
    main()