from PySide6.QtCore import QObject, QTimer, Signal

class TypingStateManager(QObject):
    """Manages typing state with debounce and timeout logic."""
    state_changed = Signal(bool) # True if typing, False if stopped

    def __init__(self, debounce_ms=500, timeout_ms=3000):
        super().__init__()
        self.is_typing = False
        
        # Debounce: don't flood server with typing_start on every keystroke
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.setInterval(debounce_ms)
        self.debounce_timer.timeout.connect(self._on_debounce_timeout)
        
        # Inactivity: auto-send typing_stop if user stops typing
        self.inactivity_timer = QTimer()
        self.inactivity_timer.setSingleShot(True)
        self.inactivity_timer.setInterval(timeout_ms)
        self.inactivity_timer.timeout.connect(self.stop_typing)

    def on_keystroke(self):
        if not self.is_typing:
            if not self.debounce_timer.isActive():
                self.debounce_timer.start()
        
        # Reset inactivity timer on every keystroke
        self.inactivity_timer.start()

    def _on_debounce_timeout(self):
        self.is_typing = True
        self.state_changed.emit(True)

    def stop_typing(self):
        if self.is_typing:
            self.is_typing = False
            self.debounce_timer.stop()
            self.state_changed.emit(False)
        self.inactivity_timer.stop()
