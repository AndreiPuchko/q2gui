import gettext
from importlib.resources import files
import locale
import os


class I18n:
    def __init__(self):
        self._translator = gettext.NullTranslations()
        self.lang = None

    def detect_default_lang(self) -> str:
        if env := os.getenv("Q2GUI_LANG"):
            return env.split("_")[0].split("-")[0]

        loc = locale.getlocale()[0]
        if not loc:
            return "en"

        loc = loc.replace("-", "_")
        if "_" in loc and len(loc.split("_")[0]) == 2:
            return loc.split("_")[0].lower()

        # Windows-style fallback
        return loc.split("_")[0][:2].lower()

    def setup(self, lang: str | None = None):
        self.lang = lang or self.detect_default_lang()
        localedir = files("q2gui") / "locale"

        self._translator = gettext.translation(
            domain="q2gui",
            localedir=localedir,
            languages=[self.lang],
            fallback=True,
        )

    def tr(self, msg: str) -> str:
        return self._translator.gettext(msg)
