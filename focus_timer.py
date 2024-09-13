import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import cairo
from pynput import keyboard
import math

class FocusTimer(Gtk.Window):
    def set_icon(self):
        try:
            self.set_icon_from_file("/home/john/Nextcloud/AIExperiment/pomoslide/focus_timer_icon.ico")
        except GLib.Error:
            print("Failed to set the icon")
            
    def __init__(self):
        Gtk.Window.__init__(self, title="Focus Timer")
        self.set_default_size(100, 1400)  # 100 pixels wide, 1400 pixels tall
        self.set_keep_above(True)
        self.set_decorated(True)
        self.set_icon()  # Add this line to use an icon

        # Create a vertical box for layout
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(self.box)

        # Create a drawing area for the color block
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.connect('draw', self.on_draw)
        self.box.pack_start(self.drawing_area, True, True, 0)

        # Create a container for the time label
        self.label_container = Gtk.Alignment()
        self.label_container.set(0.5, 1, 0, 0)  # Center horizontally, align to bottom

        self.time_label = Gtk.Label()
        self.time_label.set_markup('<span font="20" foreground="#333333">30:00</span>')
        self.label_container.add(self.time_label)

        self.box.pack_end(self.label_container, False, False, 10)

        self.total_time = 30 * 60  # 30 minutes in seconds
        self.time_left = self.total_time
        self.timer_running = False
        self.timer_id = None

        # Color definitions
        self.deep_green = (0.0, 0.5, 0.0)     # RGB(0, 128, 0)
        self.vivid_yellow = (1.0, 0.84, 0.0)  # RGB(255, 215, 0)
        self.pure_red = (1.0, 0.0, 0.0)       # RGB(255, 0, 0)
        self.black = (0, 0, 0)                # RGB(0, 0, 0)
        self.turquoise = (0.25, 0.88, 0.82)   # RGB(64, 224, 208)

        self.current_color = self.turquoise
        self.next_color = self.deep_green

        # Set up global hotkeys
        self.listener = keyboard.GlobalHotKeys({
            '<ctrl>+<alt>+s': self.start_timer,
            '<ctrl>+<alt>+p': self.pause_timer,
            '<ctrl>+<alt>+r': self.restart_timer
        })
        self.listener.start()

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.timer_id = GLib.timeout_add(1000, self.update_timer)

    def pause_timer(self):
        if self.timer_running:
            self.timer_running = False
            if self.timer_id:
                GLib.source_remove(self.timer_id)
            self.current_color = self.turquoise
            self.next_color = self.get_color_for_time(self.time_left)
        self.queue_draw()

    def restart_timer(self):
        self.time_left = self.total_time
        self.current_color = self.turquoise
        self.next_color = self.deep_green
        self.update_time_label()
        self.pause_timer()

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.current_color = self.next_color
            self.next_color = self.get_color_for_time(self.time_left - 1)
            self.update_time_label()
            self.queue_draw()
            return True
        else:
            self.timer_running = False
            self.current_color = self.turquoise
            self.next_color = self.deep_green
            self.time_left = self.total_time  # Reset the timer
            self.update_time_label()
            self.queue_draw()
            return False

    def on_draw(self, widget, cr):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()

        # Draw the current color
        cr.set_source_rgb(*self.current_color)
        cr.rectangle(0, 0, width, height)
        cr.fill()

        # Draw the next color transitioning from right to left
        if self.timer_running:
            transition_progress = (self.time_left % 60) / 60
            transition_width = width * (1 - self.ease_out_quad(transition_progress))
            cr.set_source_rgb(*self.next_color)
            cr.rectangle(width - transition_width, 0, transition_width, height)
            cr.fill()

    def get_color_for_time(self, time_left):
        if time_left > 15 * 60:  # First 15 minutes: deep green to vivid yellow
            t = 1 - (time_left - 15 * 60) / (15 * 60)
            return self.interpolate_color(self.deep_green, self.vivid_yellow, self.ease_in_out_cubic(t))
        elif time_left > 5 * 60:  # Next 10 minutes: vivid yellow to pure red
            t = 1 - (time_left - 5 * 60) / (10 * 60)
            return self.interpolate_color(self.vivid_yellow, self.pure_red, self.ease_in_out_cubic(t))
        else:  # Last 5 minutes: pure red to black
            t = 1 - time_left / (5 * 60)
            return self.interpolate_color(self.pure_red, self.black, t)  # Linear transition

    def interpolate_color(self, color1, color2, t):
        return tuple(c1 + (c2 - c1) * t for c1, c2 in zip(color1, color2))

    def ease_in_out_cubic(self, t):
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - math.pow(-2 * t + 2, 3) / 2

    def ease_out_quad(self, t):
        return 1 - (1 - t) * (1 - t)

    def update_time_label(self):
        minutes, seconds = divmod(self.time_left, 60)
        self.time_label.set_markup(f'<span font="20" foreground="#333333">{minutes:02d}:{seconds:02d}</span>')

win = FocusTimer()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()