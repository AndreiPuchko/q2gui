import gettext
import locale
import os
from importlib.resources import files


class I18n:
    def __init__(self):
        self.lang: str | None = None

        # Ordered from lowest → highest priority
        self._domains: list[tuple[str, str]] = []

        self._translator: gettext.NullTranslations | gettext.GNUTranslations = gettext.NullTranslations()
        self.register_domain("q2gui", "q2gui")

    # ------------------------------------------------------------
    # Language detection
    # ------------------------------------------------------------

    def detect_default_lang(self) -> str:
        if env := os.getenv("Q2GUI_LANG"):
            return env.split("_")[0].split("-")[0]

        loc = locale.getlocale()[0]
        if not loc:
            return "en"

        loc = loc.replace("-", "_")
        if "_" in loc and len(loc.split("_")[0]) == 2:
            return loc.split("_")[0].lower()

        return loc.split("_")[0][:2].lower()

    # ------------------------------------------------------------
    # Domain registration
    # ------------------------------------------------------------

    def register_domain(self, domain: str, package: str):
        """
        Register a translation domain.

        Order matters:
        first registered  -> lowest priority
        last registered   -> highest priority
        """
        self._domains.append((domain, package))

    # ------------------------------------------------------------
    # Build translation chain
    # ------------------------------------------------------------

    def _build_chain(self):
        tr: gettext.NullTranslations | gettext.GNUTranslations = gettext.NullTranslations()

        for domain, package in self._domains:
            t = gettext.translation(
                domain=domain,
                localedir=files(package) / "locale",
                languages=[self.lang],
                fallback=True,
            )
            t.add_fallback(tr)
            tr = t

        self._translator = tr

    # ------------------------------------------------------------
    # Setup / language switch
    # ------------------------------------------------------------

    def setup(self, lang: str | None = None):
        """
        Initialize or reinitialize translations.
        Safe to call multiple times (e.g. when switching language).
        """
        self.lang = lang or self.detect_default_lang()
        self._build_chain()

    # ------------------------------------------------------------
    # Translation API
    # ------------------------------------------------------------

    def tr(self, msg: str) -> str:
        return self._translator.gettext(msg)
