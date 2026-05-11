# -*- coding: utf-8 -*-
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
import gettext

PluginLanguageDomain = "tmdb"
PluginLanguagePath = "Extensions/tmdb/locale"


def localeInit():
	gettext.bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, PluginLanguagePath))


def _(txt):
	t = gettext.dgettext(PluginLanguageDomain, txt)
	if t == txt:
		# print("[TMDB] fallback to default Enigma2 Translation for %s" % txt)
		t = gettext.gettext(txt)
	return t


def _s(singular, plural, n):
	t = gettext.dngettext(PluginLanguageDomain, singular, plural, n)
	if t in (singular, plural):
		# print("[TMDB] fallback to default Enigma2 Translation for %s, %s, %d" % (singular, plural, n)
		t = gettext.ngettext(singular, plural, n)
	return t


localeInit()
language.addCallback(localeInit)

__version__ = "1.0.2"
