class Debouncer:
    def __init__(self, widget, callback, delay=300):
        self.widget = widget
        self.callback = callback
        self.delay = delay
        self._timer_id = None

    def trigger(self):
        if self._timer_id:
            self.widget.after_cancel(self._timer_id)
        self._timer_id = self.widget.after(self.delay, self.callback)
