# mynah/ui/menubar.py
"""
macOS menu bar status app for Mynah.
Shows today's spend, mute status, and quick access to quit,
using rumps.
"""

try:
    import rumps
    HAS_RUMPS = True
except ImportError:
    HAS_RUMPS = False

from mynah.log.metrics import check_daily_budget


class MynahMenuBarApp(rumps.App if HAS_RUMPS else object):
    def __init__(self):
        if not HAS_RUMPS:
            raise RuntimeError("rumps is required for the menu bar app")
        super().__init__("Mynah", title="Mynah", quit_button="Quit")
        self.muted = False
        self.spend_item = rumps.MenuItem("Today's spend: checking...")
        self.mute_item = rumps.MenuItem("Mute", callback=self.toggle_mute)
        self.menu = [self.spend_item, self.mute_item]
        self.update_spend()

    def toggle_mute(self, sender):
        self.muted = not self.muted
        sender.title = "Unmute" if self.muted else "Mute"

    def update_spend(self):
        within_budget, spend = check_daily_budget()
        status = "OK" if within_budget else "OVER LIMIT"
        self.spend_item.title = f"Today's spend: ${spend:.2f} ({status})"

    @rumps.timer(30)
    def refresh(self, _):
        self.update_spend()


if __name__ == "__main__":
    MynahMenuBarApp().run()
