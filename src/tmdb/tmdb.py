#!/usr/bin/env python
# -*- coding: utf-8 -*-
#######################################################################
# maintainer: schomi@vuplus-support.org
# This plugin is free software, you are allowed to
# modify it (if you keep the license),
# but you are not allowed to distribute/publish
# it without source code (this version and your modifications).
# This means you also have to distribute
# source code of your modifications.
#######################################################################

from base64 import b64decode
from os import mkdir, remove
from os.path import basename, exists, isdir
from re import search, sub, I, S
from time import localtime, strptime

from Components.ActionMap import HelpableActionMap
from Components.Label import Label
from Components.config import config
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from Components.ScrollLabel import ScrollLabel
from Components.Sources.StaticText import StaticText

from Screens.ChoiceBox import ChoiceBox
from Screens.HelpMenu import HelpableScreen
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Setup import Setup
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Tools.BoundFunction import boundFunction

from enigma import eServiceReference, eListboxPythonMultiContent, ePicLoad, eTimer, gFont, RT_HALIGN_LEFT, RT_VALIGN_CENTER

from skin import parameters
import shutil
from requests import get, exceptions, Session
from PIL import Image

from twisted.internet.reactor import callInThread

import tmdbsimple as tmdb
from .__init__ import _, ngettext
from .skins import tmdbListParams, tmdbScreenSkin, tmdbScreenMovieSkin, tmdbScreenPeopleSkin, tmdbScreenPersonSkin, tmdbScreenSeasonSkin, tmdbScreenReviewsSkin

from Components.SystemInfo import BoxInfo

TrailerSupport = False
YoutubeDL = None
YoutubeDLP = None

distro = BoxInfo.getItem("distro").lower()
if distro in ("openatv",):
	try:
		from youtube_dl import YoutubeDL
		TrailerSupport = True
	except ImportError:
		YoutubeDL = None

	try:
		from yt_dlp import YoutubeDL as YoutubeDLP
		TrailerSupport = True
	except ImportError:
		YoutubeDLP = None


pname = "TMDB"
pdesc = _("Show movie details from TMDB")
pversion = "1.0.2"
pdate = "20260508"

tmdb.REQUESTS_SESSION = Session()
tmdb.REQUESTS_TIMEOUT = (5, 30)

noCover = "/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/no_cover.png"
noCoverP = "/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/no_cover_p.png"
tempDir = "/tmp/tmdb/"

DEFAULT = 0
CURRENT_MOVIES = 1
UPCOMING_MOVIES = 2
POPULAR_MOVIES = 3
SIMILAR_MOVIES = 4
RECOMENDED_MOVIES = 5
BEST_RATED_MOVIES = 6

colorNormal = "\\c00ffffff"
colorHighlight = "\\c00fff000"


def debug(s, flag="a"):  # pass
	with open("/usr/lib/enigma2/python/Plugins/Extensions/tmdb/debug.txt", flag) as f:
		f.write(f"{s}\n")


def cleanText(text):
	cutlist = ['x264', '720p', '1080p', '1080i', 'PAL', 'GERMAN', 'ENGLiSH', 'WS',
				'DVDRiP', 'UNRATED', 'RETAIL', 'Web-DL', 'DL', 'LD', 'MiC', 'MD', 'DVDR',
				'BDRiP', 'BLURAY', 'DTS', 'UNCUT', 'ANiME', 'AC3MD', 'AC3', 'AC3D', 'TS',
				'DVDSCR', 'COMPLETE', 'INTERNAL', 'DTSD', 'XViD', 'DIVX', 'DUBBED',
				'LINE.DUBBED', 'DD51', 'DVDR9', 'DVDR5', 'h264', 'AVC', 'WEBHDTVRiP',
				'WEBHDRiP', 'WEBRiP', 'WEBHDTV', 'WebHD', 'HDTVRiP', 'HDRiP', 'HDTV',
				'ITUNESHD', 'REPACK', 'SYNC']
	text = cleanEnd(text)

	for word in cutlist:
		text = sub(r'[-_.+]' + word + r'[-_.+]', '+', text, flags=I)
	text = text.replace('.', ' ').replace('-', ' ').replace('_', ' ').replace('+', '')\
			.replace(" Director's Cut", "").replace(" director's cut", "")\
			.replace("[Uncut]", "").replace("Uncut", "").replace("Elokuva: ", "")\
			.replace("Uusi Kino: ", "").replace("Kino Klassikko: ", "")\
			.replace("Kino Suomi: ", "").replace("Kino: ", "")

	text_split = text.split()
	if text_split and text_split[0].lower() in ("new:", "live:", "movie:"):
		text_split.pop(0)  # remove annoying prefixes
	text = " ".join(text_split)

	if search(r'S\d+E\d+', text, flags=I):
		text = sub(r'S\d+E\d+.*\w+', '', text, flags=S | I)
	text = sub(r'\(\d+\)$', '', text).rstrip()  # remove episode number from series, like "series name (234)"

	return text


def cleanEnd(text):
	text = text.replace('.wmv', '').replace('.flv', '').replace('.ts', '')\
			.replace('.m2ts', '').replace('.mkv', '').replace('.avi', '')\
			.replace('.mpeg', '').replace('.mpg', '').replace('.iso', '')\
			.replace('.mp4', '')
	return text


def highlightText(s):
	return colorHighlight + str(s) + colorNormal


def threadDownloadPage(link, file, success, fail=None):
	url = link.encode('ascii', 'xmlcharrefreplace').decode().replace(' ', '%20').replace('\n', '')
	try:
		response = get(url, timeout=(3.05, 6))
		response.raise_for_status()
		with open(file, "wb") as f:
			f.write(response.content)
		success(file, link)
	except exceptions.RequestException as error:
		if fail is not None:
			fail(error, link)


class CoverHelper():
	def __init__(self, backdrop=False, fskLogo=False):
		self['cover'] = Pixmap()
		self.picloadCover = ePicLoad()
		self.picloadCover.PictureData.get().append(self.showCoverCallback)
		if backdrop:
			self['backdrop'] = Pixmap()
			self.picloadBackdrop = ePicLoad()
			self.picloadBackdrop.PictureData.get().append(self.showBackdropCallback)

		if fskLogo:
			self['fsklogo'] = Pixmap()
			self.picloadFsk = ePicLoad()
			self.picloadFsk.PictureData.get().append(self.showFskCallback)

		self.delayTimer = eTimer()

	def imageURL(self, path):
		return f"http://image.tmdb.org/t/p/{config.plugins.tmdb.themoviedb_coversize.value}/{path}"

	def avatarURL(self, path):
		size = [90, 180, 300, 300][config.plugins.tmdb.themoviedb_coversize.index]
		return f"http://image.tmdb.org/t/p/w{size}_and_h{size}_face/{path}"

	def delayDownload(self, url, fileName, onData, onError):
		self.delayTimer.stop()
		if self.delayTimer.callback:
			del self.delayTimer.callback[0]
		self.delayTimer.callback.append(boundFunction(callInThread, threadDownloadPage, url, fileName, onData, onError))
		self.delayTimer.start(500, True)

	def decodeCover(self, coverName):
		size = self['cover'].instance.size()
		self.picloadCover.setPara((size.width(), size.height(), 1, 1, False, 1, ""))
		self.picloadCover.startDecode(coverName)

	def decodeBackdrop(self, coverName):
		size = self['backdrop'].instance.size()
		self.picloadBackdrop.setPara((size.width(), size.height(), 0, 0, False, 1, ""))
		self.picloadBackdrop.startDecode(coverName)

	def decodeFsk(self, coverName):
		size = self['fsklogo'].instance.size()
		self.picloadFsk.setPara((size.width(), size.height(), 1, 1, False, 1, ""))
		self.picloadFsk.startDecode(coverName)

	def showCoverCallback(self, picInfo=None):
		ptr = self.picloadCover.getData()
		if ptr is not None:
			self["cover"].instance.setPixmap(ptr.__deref__())
			self["cover"].show()

	def showBackdropCallback(self, picInfo=None):
		ptr = self.picloadBackdrop.getData()
		if ptr is not None:
			self["backdrop"].instance.setPixmap(ptr.__deref__())
			self["backdrop"].show()

	def showFskCallback(self, picInfo=None):
		ptr = self.picloadFsk.getData()
		if ptr is not None:
			self["fsklogo"].instance.setPixmap(ptr.__deref__())
			self["fsklogo"].show()

	def backdropName(self):
		return f"{tempDir}{self.media}-{self.id}-backdrop.jpg"

	def showBackdrop(self):
		backdropSaved = self.backdropName()
		if exists(backdropSaved):
			self.decodeBackdrop(backdropSaved)


class createList(MenuList):
	def __init__(self):
		MenuList.__init__(self, [], content=eListboxPythonMultiContent)
		font = parameters.get("TMDbListFont", ('Regular', tmdbListParams[0]))
		if len(font) == 2:
			font += (tmdbListParams[1],)
		font, size, self.itemHeight = font
		self.l.setFont(0, gFont(font, size))
		self.l.setItemHeight(self.itemHeight)
		self.l.setBuildFunc(self.buildList)

	def applySkin(self, desktop, screen):
		for attrib, value in self.skinAttributes:
			if attrib == "itemHeight":
				self.itemHeight = int(value)
				break
		return MenuList.applySkin(self, desktop, screen)

	def buildList(self, entry):
		# width = self.l.getItemSize().width()
		res = [None]
		x, y, w, h = parameters.get("TMDbListName", (5, 1, 1920, self.itemHeight))
		res.append((eListboxPythonMultiContent.TYPE_TEXT, x, y, w, h, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry and entry[0]))
		return res

	def getCurrent(self):
		cur = self.l.getCurrentSelection()
		return cur and cur[0]


class tmdbConfigScreen(Setup):
	def __init__(self, session):
		Setup.__init__(self, session, "TMDB", plugin="Extensions/tmdb", PluginLanguageDomain="tmdb")
		self.setTitle(f"TMDB - The Movie Database v{pversion}")


class tmdbScreen(Screen, HelpableScreen, CoverHelper):
	skin = tmdbScreenSkin

	def __init__(self, session, text, path="", results=None, keepTemp=False):
		Screen.__init__(self, session)
		tmdb.API_KEY = b64decode('ZDQyZTZiODIwYTE1NDFjYzY5Y2U3ODk2NzFmZWJhMzk=')
		if config.plugins.tmdb.apiKey.value != "intern":
			tmdb.API_KEY = config.plugins.tmdb.apiKey.value
		# print(f"[TMDB][tmdbScreen] API Key User: {tmdb.API_KEY}")
		self.cert = config.plugins.tmdb.cert.value
		self.text = cleanText(str(text))
		self.saveFilename = str(path)
		self.results = results
		self.keepTemp = keepTemp
		self.covername = noCover
		self.actcinema = DEFAULT
		self.searchtitle = (_("TMDB: ") + _("Results for %s"))
		self.page = 1
		self.id = 1
		if not isdir(tempDir):
			mkdir(tempDir)

		print(f"[TMDB][tmdbScreen] Search for {self.text}")

		HelpableScreen.__init__(self)
		self["actions"] = HelpableActionMap(self, "TMDbActions",
			{
				"ok": (self.ok, _("Show details")),
				"cancel": (self.cancel, _("Exit")),
				"up": (self.keyUp, _("Selection up")),
				"down": (self.keyDown, _("Selection down")),
				"prevBouquet": (self.chDown, _("Overview down or next list page")),
				"nextBouquet": (self.chUp, _("Overview up or previous list page")),
				"left": (self.keyLeft, _("Page up")),
				"right": (self.keyRight, _("Page down")),
				"red": (self.cancel, _("Exit")),
				"green": (self.ok, _("Show details")),
				"yellow": (self.searchString, _("Edit search")),
				"blue": (self.menu, _("Choose a movie list")),
				"menu": (self.setup, _("Setup")),
				"eventview": (self.searchString, _("Edit search"))
			}, -1)

		self['searchinfo'] = Label(_("TMDB: ") + _("Loading..."))
		self['key_red'] = Label(_("Exit"))
		self['key_green'] = Label(_("Details"))
		self['key_yellow'] = Label(_("Edit search"))
		self['key_blue'] = Label(_("More"))
		self["key_menu"] = StaticText(_("MENU"))  # auto menu button
		self['list'] = createList()
		self['overview'] = ScrollLabel("")
		self['title'] = Label("-")
		self['title_txt'] = Label(_("Original\nTitle:"))
		self['lang'] = Label("-")
		self['lang_txt'] = Label(_("Language:"))
		self['rating'] = Label("-")
		self['rating_txt'] = Label(_("Rating:"))

		CoverHelper.__init__(self)

		self.onLayoutFinish.append(self.onFinish)

	def onFinish(self):
		if self.text:
			self.timer = eTimer()
			self.timer.callback.append(self.ok)
			callInThread(self.tmdbSearch)
		else:
			print("[TMDB][tmdbScreen] no movie found.")
			self['searchinfo'].setText(_("TMDB: ") + _("No results for %s") % self.text)

	def menu(self):
		options = [
			(_("Exit"), DEFAULT),
			(_("Current movies in cinemas"), CURRENT_MOVIES),
			(_("Upcoming movies"), UPCOMING_MOVIES),
			(_("Popular movies"), POPULAR_MOVIES),
			(_("Similar movies"), SIMILAR_MOVIES),
			(_("Recommendations"), RECOMENDED_MOVIES),
			(_("Best rated movies"), BEST_RATED_MOVIES)
		]
		self.session.openWithCallback(self.menuCallback, ChoiceBox, list=options)

	def menuCallback(self, ret):
		self.id = 1
		self.title = ""
		self.page = 1
		self.totalpages = 1
		if ret is not None:
			self.searchtitle = ret[0]
			self.actcinema = ret[1]
		if self.actcinema in (SIMILAR_MOVIES, RECOMENDED_MOVIES):
			self.id = self['list'].getCurrent()[3]
			self.title = self['list'].getCurrent()[0]
		callInThread(self.tmdbSearch)

	def tmdbSearch(self):
		self['searchinfo'].setText(_("TMDB: ") + _("Search for %s ...") % self.text)
		self.lang = config.plugins.tmdb.lang.value
		res = []
		self.count = 0
		json_data = {}
		try:
			if self.results:
				json_data = self.results
			elif self.actcinema == DEFAULT:
				search = tmdb.Search()
				json_data = search.multi(query=self.text, language=self.lang)
			elif self.actcinema == CURRENT_MOVIES:
				json_data = tmdb.Movies().now_playing(page=self.page, language=self.lang)
			elif self.actcinema == UPCOMING_MOVIES:
				json_data = tmdb.Movies().upcoming(page=self.page, language=self.lang)
			elif self.actcinema == POPULAR_MOVIES:
				json_data = tmdb.Movies().popular(page=self.page, language=self.lang)
			elif self.actcinema == SIMILAR_MOVIES:
				json_data = tmdb.Movies(self.id).similar_movies(page=self.page, language=self.lang)
			elif self.actcinema == RECOMENDED_MOVIES:
				json_data = tmdb.Movies(self.id).recommendations(page=self.page, language=self.lang)
			elif self.actcinema == BEST_RATED_MOVIES:
				json_data = tmdb.Movies().top_rated(page=self.page, language=self.lang)
				# print("[TMDB][tmdbSearch] json output\n", json_data)
		except Exception as e:
			print("[TMDB][tmdbScreen] tmdb search fail", e)
			self['searchinfo'].setText(_("TMDB: ") + _("No results found, or does not respond!"))
			return
		if json_data and json_data['results']:
			self.totalpages = json_data['total_pages']
			# print("[TMDB][tmdbSearch] results", json_data)

			for IDs in json_data['results']:
				self.count += 1
				media = fid = title = date = coverPath = backdropPath = ""
				if 'media_type' in IDs:
					media = IDs['media_type']
				else:
					media = "movie"
				if 'id' in IDs:
					fid = str(IDs['id'])
				if 'title' in IDs:
					title = IDs['title']
				if 'name' in IDs:
					title = IDs['name']
				if 'release_date' in IDs:
					date = f", {IDs['release_date'][:4]}"
				if 'first_air_date' in IDs:
					date = f", {IDs['first_air_date'][:4]}"
				if date == ", ":
					date = ""

				mediasubst = _("Movie") if media == "movie" else _("Series")

				title = f"{title} ({mediasubst}{date})"
				if 'poster_path' in IDs:
					coverPath = str(IDs['poster_path'])
				if 'backdrop_path' in IDs:
					backdropPath = str(IDs['backdrop_path'])

				url_cover = self.imageURL(coverPath)
				url_backdrop = self.imageURL(backdropPath)

				otitle = lang = rating = "-"
				overview = ""
				if 'original_title' in IDs:
					otitle = IDs['original_title']
				elif 'original_name' in IDs:
					otitle = IDs['original_name']
				if 'original_language' in IDs:
					lang = str(IDs['original_language'])
				if 'vote_average' in IDs:
					rating = f"{IDs['vote_average']:.1f} ({IDs['vote_count']})"
				if 'overview' in IDs:
					overview = IDs['overview']

				if fid or title or media:
					res.append(((title, url_cover, media, fid, url_backdrop, otitle, lang, rating, overview),))
			# print("[TMDB][tmdbSearch] res", res)
			if res:
				self['list'].setList(res)
				if self.actcinema != DEFAULT:
					self['searchinfo'].setText(f"{_('TMDB: ')}{self.searchtitle} ({_('page ')}{self.page}/{self.totalpages}) {self.title}")
				else:
					self['searchinfo'].setText(f"{_('TMDB: ')}{_('Results for %s') % self.text}")
				self['list'].moveTop()
				self.getInfo()
		else:
			print("[TMDB] data not found")
			self.showCover(noCover)
			self['searchinfo'].setText(f"{_('TMDB: ')}{_('Data not found!')}")
			if self.count == 1:
				self['searchinfo'].setText(_("TMDB: ") + _("Results for %s") % self.text)
			if "total_results" not in json_data or json_data['total_results'] == 0:
				self['searchinfo'].setText(_("TMDB: ") + _("No results for %s") % self.text)

	def getInfo(self):
		current = self['list'].getCurrent()
		url_cover = current[1]
		fid = current[3]
		self['title'].setText(current[5])
		self['lang'].setText(current[6])
		self['rating'].setText(current[7])
		self['overview'].setText(current[8])

		if url_cover.endswith("None"):
			self.showCover(noCover)
		else:
			fileName = f"{tempDir}{current[2]}-{fid}.jpg"
			if not exists(fileName):
				self.delayDownload(url_cover, fileName, self.getData, self.dataError)
			else:
				self.showCover(fileName)

	def getData(self, coverSaved, url_cover):
		if 'list' in self and url_cover == self['list'].getCurrent()[1]:
			self.showCover(coverSaved)

	def dataError(self, error, url_cover):
		print(f"[TMDB] Error: {error}")
		self.getData(noCover, url_cover)

	def showCover(self, coverName):
		if not exists(coverName):
			coverName = noCover

		if exists(coverName):
			self.decodeCover(coverName)
		self.covername = coverName
		# Only one result, launch details
		if config.plugins.tmdb.firsthit.value:
			if self.count == 1:
				self.timer.start(100, False)

	def ok(self):
		self.timer.stop()
		check = self['list'].getCurrent()
		if check is not None:
			# title, url_cover, media, id, url_backdrop
			title = check[0]
			media = check[2]
			fid = check[3]
			self.covername = f"{tempDir}{media}-{fid}.jpg"
			self.url_backdrop = check[4]
			self.session.open(tmdbScreenMovie, title, media, self.covername, fid, self.saveFilename, self.url_backdrop)

	def keyLeft(self):
		check = self['list'].getCurrent()
		if check is not None:
			self['list'].pageUp()
			self.getInfo()

	def keyRight(self):
		check = self['list'].getCurrent()
		if check is not None:
			self['list'].pageDown()
			self.getInfo()

	def keyDown(self):
		check = self['list'].getCurrent()
		if check is not None:
			self['list'].down()
			self.getInfo()

	def keyUp(self):
		check = self['list'].getCurrent()
		if check is not None:
			self['list'].up()
			self.getInfo()

	def chDown(self):
		if self.actcinema != DEFAULT:
			self.page += 1
			if self.page > self.totalpages:
				self.page = 1
			callInThread(self.tmdbSearch)
		else:
			self['overview'].pageDown()

	def chUp(self):
		if self.actcinema != DEFAULT:
			self.page -= 1
			if self.page <= 0:
				self.page = 1
			callInThread(self.tmdbSearch)
		else:
			self['overview'].pageUp()

	def keyYellow(self):
		return

	def setup(self):
		self.session.open(tmdbConfigScreen)

	def searchString(self):
		self.actcinema = DEFAULT
		self.session.openWithCallback(self.goSearch, VirtualKeyBoard, title=(_("Search for Movie:")), text=self.text)

	def goSearch(self, newTitle):
		if newTitle:
			self.text = newTitle
			print(f"[TMDB] Manual search for: {self.text}")
			callInThread(self.tmdbSearch)

	def cancel(self):
		if not self.keepTemp:
			self.delCover()
		self.close()

	def delCover(self):
		if isdir(tempDir):
			shutil.rmtree(tempDir)


class tmdbScreenMovie(Screen, HelpableScreen, CoverHelper):
	skin = tmdbScreenMovieSkin

	def __init__(self, session, mname, media, coverName, fid, saveFilename, url_backdrop):
		Screen.__init__(self, session)
		self.mname = mname
		self.media = media
		self.movie = self.media == "movie"
		self.coverName = coverName
		self.url_backdrop = url_backdrop
		self.id = fid
		self.info = self.credits = None
		self.saveFilename = saveFilename

		HelpableScreen.__init__(self)
		self["actions"] = HelpableActionMap(self, "TMDbActions",
			{
				"ok": (self.ok, _("Cast")),
				"cancel": (self.cancel, _("Exit")),
				"up": (self.keyLeft, _("Selection up")),
				"down": (self.keyRight, _("Selection down")),
				"left": (self.keyLeft, _("Page up")),
				"right": (self.keyRight, _("Page down")),
				"red": (self.cancel, _("Exit")),
				"green": (self.keyGreen, _("Cast")),
				"yellow": (self.keyYellow, _("Seasons")),
				"blue": (self.menu, _("File operations")),
				"menu": (self.setup, _("Setup")),
				"eventview": (self.showReviews, _("Reviews")),
				"showMovies": (self.showTrailer, _("Show Trailer"))
			}, -1)

		self['searchinfo'] = Label(_("TMDB: ") + _("Loading..."))
		self['genre'] = Label("-")
		self['genre_txt'] = Label(_("Genre:"))
		self['fulldescription'] = ScrollLabel("")
		self['rating'] = Label("0.0")
		self['votes'] = Label("-")
		self['votes_brackets'] = Label("")
		self['votes_txt'] = Label(_("Votes:"))
		self['fsk'] = Label()
		self['runtime'] = Label("-")
		self['runtime_txt'] = Label(_("Runtime:"))
		self['year'] = Label("-")
		self['year_txt'] = Label(_("Year:"))
		self['country'] = Label("-")
		self['country_txt'] = Label(_("Countries:"))
		self['director'] = Label("-")
		self['director_txt'] = Label(_("Director:"))
		self['author'] = Label("-")
		self['author_txt'] = Label(_("Author:"))
		self['studio'] = Label("-")
		self['studio_txt'] = Label(_("Studio:"))
		self['key_red'] = Label(_("Exit"))
		self['key_green'] = Label(_("Cast"))
		self['key_yellow'] = Label(_("Seasons"))
		self['key_blue'] = Label(_("More"))
		self["key_menu"] = StaticText(_("MENU"))  # auto menu button
		CoverHelper.__init__(self, True, True)
		print("[TMDB][tmdbScreenMovie] entered")
		self.onLayoutFinish.append(self.onFinish)

	def onFinish(self):
		if self.movie:
			self['key_yellow'].setText("")
		if self.saveFilename == "":
			self['key_blue'].setText("")
		# TMDB read
		print(f"[TMDB] Selected: {self.mname}")
		self.showCover(self.coverName)
		self.getBackdrop(self.url_backdrop)
		callInThread(self.tmdbSearch)

	def menu(self):
		if self.saveFilename:
			options = [
				(_("Save movie description"), 1),
				(_("Delete movie EIT file"), 2),
				(_("Save movie cover"), 3),
				(_("Save movie backdrop"), 4),
				("1+2", 5),
				("1+3", 6),
				("1+2+3", 7),
				("1+2+3+4", 8),
				("3+4", 9)
			]
			self.session.openWithCallback(self.menuCallback, ChoiceBox, list=options)

	def menuCallback(self, ret):
		if ret is None:
			return
		if ret[1] in (1, 5, 6, 7, 8):
			self.createTXT()
		if ret[1] in (2, 5, 7, 8):
			self.deleteEIT()
		if ret[1] in (3, 6, 7, 8, 9):
			self.saveCover()
		if ret[1] in (4, 8, 9):
			self.saveBackdrop()

	def keyLeft(self):
		self['fulldescription'].pageUp()

	def keyRight(self):
		self['fulldescription'].pageDown()

	def tmdbSearch(self):
		self.lang = config.plugins.tmdb.lang.value
		self['searchinfo'].setText(_("TMDB: ") + _("Loading..."))
		print("[TMDB][tmdbScreenMovie]1 ID, self.movie: ", self.id, "   ", self.movie)

		videos = None
		try:
			append = "credits,"
			if TrailerSupport:
				append += "videos,"
			if self.movie:
				fsk = "releases"
				api = tmdb.Movies(self.id)
			else:
				fsk = "content_ratings"
				api = tmdb.TV(self.id)
			append += fsk
			self.info = json_data = api.info(language=self.lang, append_to_response=append)
			# print("[TMDB][tmdbScreenMovie] json_data", json_data)
			self.credits = json_data_cast = json_data['credits']
			# print("[TMDB][tmdbScreenMovie] json_data_cast", json_data_cast)
			json_data_fsk = json_data[fsk]
			# print("[TMDB][tmdbScreenMovie] json_fsk", json_data_fsk)
			if TrailerSupport:
				videos = json_data['videos']
				# print("[TMDB][tmdbScreenMovie] videos", videos)
			if json_data['overview'] == "" and self.lang != "en":
				json_data = api.info(language="en")
			self['searchinfo'].setText(self.mname)
		except Exception as e:
			print("[TMDB][tmdbScreenMovie]1 tmdb read fail", e)
			self['searchinfo'].setText(_("TMDB: ") + _("No results found, or does not respond!"))
			return
		year = vote_average = vote_count = runtime = country_string = genre_string = subtitle = cast_string = season = ""
		crew_string = director = author = studio_string = ""

		self.trailer = videos["results"] if TrailerSupport and videos else None

		# Year
		if 'release_date' in json_data:
			year = json_data['release_date'][:4]
			self['year'].setText(year)

		# Rating
		if 'vote_average' in json_data:
			vote_average = json_data['vote_average']
			self['rating'].setText(f"{vote_average:.1f}")

		# Votes
		if 'vote_count' in json_data:
			vote_count = str(json_data['vote_count'])
			self['votes'].setText(vote_count)
			self['votes_brackets'].setText(f"({vote_count})")

		# Runtime
		if 'runtime' in json_data and json_data['runtime']:
			runtime = f"{json_data['runtime']} min."
			self['runtime'].setText(runtime)

		# Country
		if 'production_countries' in json_data:
			for country in json_data['production_countries']:
				country_string += f"{country['iso_3166_1']}/"
			country_string = country_string[:-1]
			self['country'].setText(country_string)

		# Genre"
		if 'genres' in json_data:
			# genre_count = len(json_data['genres'])
			for genre in json_data['genres']:
				genre_string += f"{genre['name']}, "
			genre_string = genre_string[:-2]
			self['genre'].setText(genre_string)

		# Subtitle
		if 'tagline' in json_data:
			subtitle = json_data['tagline']

		# Cast
		if 'cast' in json_data_cast:
			for cast in json_data_cast['cast']:
				castx = cast['name'] if cast['character'] == "" else f"{cast['name']} ({cast['character']})"
				cast_string += f"{castx}\n"
			cast_string = cast_string[:-1]
			if cast_string:
				cast_string = f"{highlightText(_('Cast'))}\n{cast_string}"

		# Crew
		if 'crew' in json_data_cast:
			for crew in json_data_cast['crew']:
				crew_name = crew['name']
				crew_job = crew['job']
				crew_string += f"{crew_name} ({crew_job})\n"

				if crew_job == "Director":
					director += f"{crew_name}, "
				if crew_job == "Screenplay" or crew_job == "Writer":
					author += f"{crew_name}, "
			crew_string = crew_string[:-1]
			if crew_string:
				crew_string = f"{highlightText(_('Crew'))}\n{crew_string}"
			director = director[:-2]
			author = author[:-2]
			self['director'].setText(director)
			self['author'].setText(author)

		# Studio/Production Company
		if 'production_companies' in json_data:
			for studio in json_data['production_companies']:
				studio_string += f"{studio['name']}, "
			studio_string = studio_string[:-2]
			self['studio'].setText(studio_string)

		#
		# modify Data for TV/Series
		#
		if not self.movie:
			year = country_string = director = studio_string = runtime = episodes = ""

			# Year
			if 'first_air_date' in json_data:
				year = json_data['first_air_date'][:4]
				self['year'].setText(year)

			# Country
			if 'origin_country' in json_data:
				for country in json_data['origin_country']:
					country_string += f"{country}/"
				country_string = country_string[:-1]
				self['country'].setText(country_string)

			# Crew Director
			if 'created_by' in json_data:
				for directors in json_data['created_by']:
					director += f"{directors['name']}, "
				director = director[:-2]
				self['director'].setText(_("Various"))
				self['author'].setText(director)

			# Studio/Production Company
			if 'networks' in json_data:
				for studio in json_data['networks']:
					studio_string += f"{studio['name']}, "
				studio_string = studio_string[:-2]
				self['studio'].setText(studio_string)

			# Runtime
			seasons = json_data.get("number_of_seasons", "")
			episodes = json_data.get("number_of_episodes", "")
			runtime = f"{ngettext('{n} Season', '{n} Seasons', seasons).format(n=seasons)} / {ngettext('{n} Episode', '{n} Episodes', episodes).format(n=episodes)}"
			self['runtime'].setText(runtime)

			# Series Description
			if 'seasons' in json_data:
				for seasons in json_data['seasons']:
					if seasons['season_number'] >= 1:
						syear = str(seasons['air_date'])[:7]
						syear = "" if syear == "None" else f" ({syear})"
						season += f"{_('Season')} {seasons['season_number']} / {seasons['episode_count']}{syear}\n"
				if season:
					season = f"{highlightText(_('Seasons'))}\n{season}"

		# Description
		description = json_data['overview']
		description = [info for info in (description, cast_string, crew_string) if info]
		description = "\n\n".join(description)

		movieinfo = [info for info in (genre_string, country_string, year, runtime) if info]
		movieinfo = ", ".join(movieinfo)

		fulldescription = [info for info in (subtitle, movieinfo, description, season) if info]
		fulldescription = "\n\n".join(fulldescription)
		self['fulldescription'].setText(fulldescription)
		self.text = fulldescription

		# FSK
		fsk = None
		aus = None
		ages = []
		fsk_text = None
		if self.movie:
			key1 = 'countries'
			key2 = 'certification'
		else:
			key1 = 'results'
			key2 = 'rating'
		if key1 in json_data_fsk:
			for country in json_data_fsk[key1]:
				c = str(country['iso_3166_1'])
				val = country[key2]
				if c == "DE":
					fsk = val
				elif c == "AU":
					aus = val.lower().replace(" ", "").replace("+", "")
					break
				else:
					try:
						ages.append(int(search(r'\d+', val).group(0)))
					except Exception:
						pass
		if fsk:
			fsk = f"fsk_{fsk}"
		elif aus:
			fsk = f"aus_{aus}"
		elif ages:
			# Take the median age.
			ages.sort()
			fsk = f"age_{ages[len(ages) // 2]}"
		else:
			if 'origin_country' in json_data and json_data['origin_country']:
				origin = json_data['origin_country'][0]
				for country in json_data_fsk[key1]:
					c = str(country['iso_3166_1'])
					val = country[key2]
					if val and (not fsk_text or c == origin or c == "US"):
						fsk_text = f"{val}\n({c})"
						if c == origin:
							break
				if fsk_text:
					self['fsk'].setText(fsk_text)
				else:
					fsk = "fsk_100"
		if fsk:
			self.showFSK(fsk)

	def playTrailer(self, url):
		if url:
			if YoutubeDLP:
				try:
					ydl = YoutubeDLP({"format": "b", "no_color": True, "usenetrc": True})
					result = ydl.extract_info(url, download=False)
					result = ydl.sanitize_info(result)
					if result and result.get("url"):
						url = result["url"]
				except Exception as e:
					print(f"[TMDB] YoutubeDLP Error: {e}")
			elif YoutubeDL:
				try:
					ydl = YoutubeDL({'format': 'best'})
					result = ydl.extract_info(url, download=False)
					if result and hasattr(result, "url"):
						url = result['url']
				except Exception as e:
					print(f"[TMDB] YoutubeDL Error: {e}")
			if url:
				from Screens.InfoBar import MoviePlayer
				sref = eServiceReference(4097, 0, url)
				sref.setName(self.mname)
				self.session.open(MoviePlayer, sref, fromMovieSelection=False)

	def showTrailer(self):
		if self.trailer:
			choiceList = []
			for video in self.trailer:
				if video.get("site") == "YouTube":
					name = video.get("name")
					type = video.get("type")
					if type:
						name = f"{name} ({type})"
					link = f"https://www.youtube.com/watch?v={video['key']}"
					choiceList.append((name, link))
			self.session.openWithCallback(self.playTrailer, MessageBox, text="", list=choiceList, windowTitle=_("Select Video"))

	def showCover(self, coverName):
		if not exists(coverName):
			coverName = noCover

		if exists(coverName):
			self.decodeCover(coverName)

	def getBackdrop(self, url_backdrop):
		backdropSaved = self.backdropName()
		if exists(backdropSaved):
			self.decodeBackdrop(backdropSaved)
		elif url_backdrop.endswith("None"):
			print("[TMDB] No backdrop found")
		else:
			callInThread(threadDownloadPage, url_backdrop, backdropSaved, self.gotBackdrop, self.dataError)

	def gotBackdrop(self, backdrop, url_backdrop):
		# print("Backdrop download returned", backdrop)
		self.showBackdrop()

	def dataError(self, error, url_backdrop):
		print(f"[TMDB] Error: {error}")

	def showFSK(self, fsk):
		self.fsklogo = f"/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/{fsk}.png"
		self.decodeFsk(self.fsklogo)

	def ok(self):
		self.keyGreen()

	def setup(self):
		self.session.open(tmdbConfigScreen)

	def keyYellow(self):
		if not self.movie:
			self.session.open(tmdbScreenSeason, self.mname, self.id, self.media, self.info)

	def keyGreen(self):
		self.session.open(tmdbScreenPeople, self.mname, self.id, self.media, self.credits, self.info)

	def showReviews(self):
		self.session.open(tmdbScreenReviews, self.mname, self.id, self.media)

	def cancel(self):
		self.close(True)

	def saveCover(self):
		saveFile = cleanEnd(self.saveFilename)
		if exists(self.saveFilename):
			try:
				if config.plugins.tmdb.coverQuality.value != "original":
					width, height = config.plugins.tmdb.coverQuality.value.split("x", 1)
					img = Image.open(self.coverName)
					img = img.convert('RGBA', colors=256)
					img = img.resize((int(width), int(height)), Image.LANCZOS)
					img.save(self.coverName)  # img.save(f, quality=75)

				shutil.copy(self.coverName, f"{saveFile}.jpg")
				self.session.open(MessageBox, _("Cover saved!"), type=1, timeout=3)
				print(f"[TMDB] Cover {saveFile}.jpg created")
			except Exception:
				print("[TMDB] Error saving cover!")

	def saveBackdrop(self):
		saveFile = cleanEnd(self.saveFilename)
		if exists(self.saveFilename):
			try:
				backdropName = self.backdropName()
				if config.plugins.tmdb.backdropQuality.value != "original":
					width, height = config.plugins.tmdb.backdropQuality.value.split("x", 1)
					img = Image.open(backdropName)
					img = img.convert('RGBA', colors=256)
					img = img.resize((int(width), int(height)), Image.LANCZOS)
					img.save(backdropName)  # img.save(f, quality=75)

				shutil.copy(backdropName, f"{saveFile}.bdp.jpg")
				self.session.open(MessageBox, _("Backdrop saved!"), type=1, timeout=3)
				print(f"[TMDB] Backdrop {saveFile}.bdp.jpg created")
			except Exception:
				print("[TMDB] Error saving backdrop!")

	def createTXT(self):
		saveFile = cleanEnd(self.saveFilename)
		if exists(self.saveFilename):
			try:
				with open(f"{saveFile}.txt", "w") as fd:
					fd.write(self.text)
				print(f"[TMDB] {saveFile}.txt created")
				self.session.open(MessageBox, _("Movie description saved!"), type=1, timeout=3)
			except OSError:
				print("[TMDB] Error saving TXT file!")

	def deleteEIT(self):
		eitFile = f"{cleanEnd(self.saveFilename)}.eit"
		try:
			remove(eitFile)
			print(f"[TMDB] {eitFile} deleted")
			self.session.open(MessageBox, _("EIT file deleted!"), type=1, timeout=3)
		except OSError:
			print("[TMDB] Error deleting EIT file!")


class tmdbScreenPeople(Screen, HelpableScreen, CoverHelper):
	skin = tmdbScreenPeopleSkin

	def __init__(self, session, mname, fid, media, credits=None, info=None):
		Screen.__init__(self, session)
		self.mname = mname
		self.id = fid
		self.media = media
		self.movie = self.media == "movie"
		self.credits = credits
		self.info = info
		self.covername = noCoverP

		HelpableScreen.__init__(self)
		self["actions"] = HelpableActionMap(self, "TMDbActions",
			{
				"ok": (self.ok, _("Show details")),
				"cancel": (self.cancel, _("Exit")),
				"down": (self.keyDown, _("Selection down")),
				"up": (self.keyUp, _("Selection up")),
				"right": (self.keyRight, _("Page down")),
				"left": (self.keyLeft, _("Page up")),
				"red": (self.cancel, _("Exit")),
				"green": (self.ok, _("Show details")),
				"blue": (self.keyBlue, _("Setup")),
				"menu": (self.keyBlue, _("Setup"))
			}, -1)

		self['searchinfo'] = Label(_("TMDB: ") + _("Loading..."))
		self['key_red'] = Label(_("Exit"))
		self['key_green'] = Label(_("Details"))
		self['key_blue'] = Label(_("Setup"))
		self["key_menu"] = StaticText(_("MENU"))  # auto menu button
		self['list'] = createList()
		CoverHelper.__init__(self, True)

		self.onLayoutFinish.append(self.onFinish)

	def onFinish(self):
		# TMDB read
		print("[TMDB] Selected: {self.mname}")
		self.showBackdrop()
		callInThread(self.tmdbSearch)

	def tmdbSearch(self):
		self.list = []
		self.seasons_cast = []
		json_data_cast = []
		json_data_seasons = []
		json_data_season = []
		self.lang = config.plugins.tmdb.lang.value
		self['searchinfo'].setText(_("TMDB: ") + _("Loading..."))
		try:
			if self.credits:
				json_data_cast = self.credits
			elif self.movie:
				json_data_cast = tmdb.Movies(self.id).credits(language=self.lang)
			else:
				json_data_cast = tmdb.TV(self.id).credits(language=self.lang)
		except Exception as e:
			print("[TMDB][tmdbScreenMovie]2 tmdb read fail", e)
			self['searchinfo'].setText(_("TMDB: ") + _("No results found, or does not respond!"))
			return
		if "cast" in json_data_cast and json_data_cast["cast"] is not None:
			# print("json_data_cast", json_data_cast)
			for casts in json_data_cast['cast']:
				title = date = ""
				# print("json_data_cast - casts", casts)
				fid = str(casts['id'])
				title = casts['name'] if casts['character'] == "" else f"{casts['name']} ({casts['character']})"
				coverPath = casts['profile_path']
				url_cover = self.imageURL(coverPath)

				if fid != "" or title != "":
					self.list.append([None, ((title, url_cover, fid, None),)])

			if not self.movie:
				try:
					json_data_seasons = self.info if self.info else tmdb.TV(self.id).info(language=self.lang)
				except Exception as e:
					print("[TMDB][tmdbScreenMovie]3 tmdb json_data_seasons = tmdb.TV(self.id).info", e)
					self['searchinfo'].setText(_("TMDB: ") + _("No results found, or does not respond!"))
					return
				if json_data_seasons:
					total = len(json_data_seasons['seasons'])
					progress = total > 1
					if progress:
						count = 1
						loading = _("TMDB: ") + _("Loading...")
					self.list.append([None, (None,)])
					for season in json_data_seasons['seasons']:
						if progress:
							self['searchinfo'].setText(f"{loading} ({count}/{total})")
							count += 1
						date = ""
						# print"######", season
						seasoncnt = season['season_number']
						# print"#########", str(season['season_number'])
						# fid = str(season['id'])
						title = season['name']
						if season['air_date'] is not None:
							date = f" ({season['air_date'][:7]})"
						season_cast = []
						json_data_season = tmdb.TV_Seasons(self.id, seasoncnt).credits(language=self.lang)
						if json_data_season:
							title += f" / {len(json_data_season['cast'])}"
							for casts in json_data_season['cast']:
								fid = str(casts['id'])
								name = casts['name'] if casts['character'] == "" else f"{casts['name']} ({casts['character']})"
								coverPath = casts['profile_path']
								url_cover = self.imageURL(coverPath)
								season_cast.append(((f"    {name}", url_cover, fid, None),))
						coverPath = season['poster_path']
						url_cover = self.imageURL(coverPath)
						fid = str(season['id'])
						self.list.append([False, ((title + date, url_cover, fid, len(self.list)),)])
						self.seasons_cast.append(season_cast)
			if self.list:
				self.setList()
				self['searchinfo'].setText(self.mname)
			else:
				self['searchinfo'].setText(_("TMDB: ") + _("No results found"))
		else:
			self['searchinfo'].setText(_("TMDB: ") + _("No results found, or does not respond!"))

	def setList(self):
		res = []
		season = 0
		for expanded, entry in self.list:
			res.append(entry)
			if expanded is not None:
				if expanded:
					res += self.seasons_cast[season]
				season += 1
		self['list'].setList(res)
		self.getInfo()

	def getInfo(self):
		check = self['list'].getCurrent()
		url_cover = check[1]
		if url_cover.endswith("None"):
			self.showCover(noCoverP)
		else:
			fid = check[2]
			if check[3] is None:
				fileName = f"{tempDir}person-{fid}.jpg"
			else:
				fileName = f"{tempDir}{self.media}-{self.id}-{fid}.jpg"
			if not exists(fileName):
				self.delayDownload(url_cover, fileName, self.getData, self.dataError)
			else:
				self.showCover(fileName)
		if check[3] is None:
			state = _("Details")
		else:
			state = self.list[check[3]][0] and _("Collapse") or _("Expand")
		self['key_green'].setText(state)

	def getData(self, coverSaved, url_cover):
		if 'list' in self and url_cover == self['list'].getCurrent()[1]:
			self.showCover(coverSaved)

	def dataError(self, error, url_cover):
		print(f"[TMDB] Error: {error}")
		self.getData(noCoverP, url_cover)

	def showCover(self, coverName):
		if not exists(coverName):
			coverName = noCoverP

		if exists(coverName):
			self.decodeCover(coverName)
		self.covername = coverName

	def ok(self):
		check = self['list'].getCurrent()
		if check is not None:
			if check[3] is None:
				fid = check[2]
				self.session.open(tmdbScreenPerson, self.covername, fid, self.id, self.media)
			else:
				self.list[check[3]][0] ^= True
				self.setList()

	def keyLeft(self):
		check = self['list'].getCurrent()
		if check is not None:
			self['list'].pageUp()
			self.getInfo()

	def keyRight(self):
		check = self['list'].getCurrent()
		if check is not None:
			self['list'].pageDown()
			self.getInfo()

	def keyDown(self):
		check = self['list'].getCurrent()
		if check is not None:
			self['list'].down()
			self.getInfo()

	def keyUp(self):
		check = self['list'].getCurrent()
		if check is not None:
			self['list'].up()
			self.getInfo()

	def keyBlue(self):
		self.session.open(tmdbConfigScreen)

	def cancel(self):
		self.close()


class tmdbScreenPerson(Screen, HelpableScreen, CoverHelper):
	skin = tmdbScreenPersonSkin

	def __init__(self, session, coverName, fid, tid, media):
		Screen.__init__(self, session)
		self.coverName = coverName
		self.pid = fid
		self.id = tid
		self.media = media

		HelpableScreen.__init__(self)
		self["actions"] = HelpableActionMap(self, "TMDbActions",
			{
				"cancel": (self.cancel, _("Exit")),
				"up": (self.keyLeft, _("Selection up")),
				"down": (self.keyRight, _("Selection down")),
				"left": (self.keyLeft, _("Page up")),
				"right": (self.keyRight, _("Page down")),
				"red": (self.cancel, _("Exit")),
				"yellow": (self.keyYellow, _("List shows as search results")),
			}, -1)

		self['searchinfo'] = Label(_("TMDB: ") + _("Loading..."))
		self['fulldescription'] = ScrollLabel("")
		self['key_red'] = Label(_("Exit"))
		self['key_yellow'] = Label(_("List"))
		CoverHelper.__init__(self, True)

		self.onLayoutFinish.append(self.onFinish)

	def onFinish(self):
		self.showBackdrop()
		self.showCover(self.coverName)
		callInThread(self.tmdbSearch)

	def keyLeft(self):
		self['fulldescription'].pageUp()

	def keyRight(self):
		self['fulldescription'].pageDown()

	def tmdbSearch(self):
		self.list = {}
		self.lang = config.plugins.tmdb.lang.value
		print(f"[TMDB] ID: {self.pid}")
		self['searchinfo'].setText(_("TMDB: ") + _("Loading..."))
		try:		# may be invalid id
			json_data_person = tmdb.People(self.pid).info(language=self.lang, append_to_response="combined_credits")
		except Exception as e:
			print(f"[TMDB] 4 tmdb.People(self.pid).info {e}")
			self['searchinfo'].setText(_("TMDB: ") + _("No results found, or does not respond!"))
			self['key_yellow'].setText("")
			return
		if json_data_person:
			# print("[TMDB]", json_data_person)
			self.mname = json_data_person['name']

			# Personal data
			birthday = deathday = birthplace = gender = altname = rank = biography = ""
			if "birthday" in json_data_person and json_data_person['birthday'] is not None:
				birthday = json_data_person['birthday']
			if "deathday" in json_data_person and json_data_person['deathday'] is not None:
				deathday = json_data_person['deathday']
			if "place_of_birth" in json_data_person and json_data_person['place_of_birth'] is not None:
				birthplace = json_data_person['place_of_birth']
			if "gender" in json_data_person:
				gender = json_data_person['gender']
				gender = ["", _("Female"), _("Male"), _("Non-binary")][gender]
			# print("[TMDB]", json_data_person["also_known_as"])
			if "also_known_as" in json_data_person and json_data_person["also_known_as"]:
				altname = f"{_('Known as: ')}{json_data_person['also_known_as'][0]}"
				if len(json_data_person['also_known_as']) > 1:
					altname += f", {json_data_person['also_known_as'][1]}"

			if "biography" in json_data_person:
				biography = json_data_person['biography']
			if biography == "" and self.lang != "en":
				json_data_person = tmdb.People(self.pid).info(language="en")
			if "biography" in json_data_person:
				biography = json_data_person['biography']
			info = []
			age = ""
			if birthday:
				born = strptime(birthday, "%Y-%m-%d")
				stop = strptime(deathday, "%Y-%m-%d") if deathday else localtime()
				age = stop.tm_year - born.tm_year
				if stop.tm_mon < born.tm_mon or (stop.tm_mon == born.tm_mon and stop.tm_mday < born.tm_mday):
					age -= 1
				age = f" ({age})"
				info.append(f"{_('Born')}: {birthday}{'' if deathday else age}")
			if birthplace:
				info.append(f"{_('Birthplace')}: {birthplace}")
			if deathday:
				info.append(f"{_('Died')}: {deathday}{age}")
			if gender:
				info.append(f"{_('Gender')}: {gender}")
			if altname:
				info.append(altname)
			if "popularity" in json_data_person:
				info.append(f"{_('Popularity')}: {json_data_person['popularity']}")
			data = "\n".join(info)
			# print(f"[TMDB] cast person details 1 {data})
			if data and biography:
				data += "\n\n"
			data += biography
			# Participated data
			json_data_person = json_data_person['combined_credits']
			data_movies = []
			if "cast" in json_data_person:
				for cast in json_data_person['cast']:
					if cast['media_type'] == "movie":
						if "release_date" in cast and cast['release_date']:
							date = cast['release_date']
						else:
							date = "????-??-??"
						title = cast['title']
						char = "character" in cast and cast['character']
						character = f" ({char})" if char else ""
					else:
						if "first_credit_air_date" in cast and cast['first_credit_air_date']:
							date = cast['first_credit_air_date']
						elif "first_air_date" in cast and cast['first_air_date']:
							date = cast['first_air_date']
						else:
							date = "????-??-??"
						title = cast['name']
						extra = []
						character = "character" in cast and cast['character']
						if character:
							extra.append(character)
						episodes = "episode_count" in cast and cast['episode_count']
						if episodes:
							extra.append(ngettext("{n} episode", "{n} episodes", episodes).format(n=episodes))
						character = f" ({'; '.join(extra)})" if extra else ""
					datac = f"{date} {title}{character}"
					data_movies.append((datac, cast))

			data_movies.sort(reverse=True)
			data_movies, results = map(list, zip(*data_movies))
			cast_movies = "\n".join(data_movies)
			if cast_movies:
				if data:
					data += "\n\n"
				data += f"{highlightText(_('Known acting credits'))}\n{cast_movies}"
			self['fulldescription'].setText(data)
			self['searchinfo'].setText(self.mname)
			if len(results) == 1:
				self['key_yellow'].setText("")
			else:
				self.list = {
					'results': results,
					'total_pages': 1
				}
		else:
			self['searchinfo'].setText(_("TMDB: ") + _("No results found, or does not respond!"))
			self['key_yellow'].setText("")

	def showCover(self, coverName):
		self.decodeCover(coverName)

	def ok(self):
		self.cancel()

	def keyYellow(self):
		if self.list:
			self.session.open(tmdbScreen, text=self.mname, results=self.list, keepTemp=True)

	def cancel(self):
		self.close(True)


class tmdbScreenSeason(Screen, HelpableScreen, CoverHelper):
	skin = tmdbScreenSeasonSkin

	def __init__(self, session, mname, fid, media, info):
		Screen.__init__(self, session)
		self.mname = mname
		self.id = fid
		self.media = media
		self.movie = self.media == "movie"
		self.info = info

		HelpableScreen.__init__(self)
		self["actions"] = HelpableActionMap(self, "TMDbActions",
			{
				"ok": (self.ok, _("Expand/collapse season")),
				"cancel": (self.cancel, _("Exit")),
				"up": (self.keyUp, _("Selection up")),
				"down": (self.keyDown, _("Selection down")),
				"prevBouquet": (self.chDown, _("Details down")),
				"nextBouquet": (self.chUp, _("Details up")),
				"right": (self.keyRight, _("Page down")),
				"left": (self.keyLeft, _("Page up")),
				"red": (self.cancel, _("Exit")),
				"green": (self.ok, _("Expand/collapse season")),
				"blue": (self.keyBlue, _("Setup")),
				"menu": (self.keyBlue, _("Setup"))
			}, -1)

		self['searchinfo'] = Label(_("TMDB: ") + _("Loading..."))
		self['data'] = ScrollLabel("")
		self['key_red'] = Label(_("Exit"))
		self['key_green'] = Label(_("Expand"))
		self['key_blue'] = Label(_("Setup"))
		self['list'] = createList()

		CoverHelper.__init__(self, True)

		self.onLayoutFinish.append(self.onFinish)

	def onFinish(self):
		# TMDB read
		print(f"[TMDB] Selected: {self.mname}")
		self.showBackdrop()
		callInThread(self.tmdbSearch)

	def tmdbSearch(self):
		self.lang = config.plugins.tmdb.lang.value
		self['searchinfo'].setText(_("TMDB: ") + _("Loading..."))
		self.list = []
		self.season_eps = []
		# Seasons
		try:
			json_data_seasons = self.info if self.info else tmdb.TV(self.id).info(language=self.lang)
		except Exception as e:
			print(f"[TMDB] 5 tmdb.TV(self.id).info {e}")
			self['searchinfo'].setText(_("TMDB: ") + _("No results found, or does not respond!"))
			return
		if json_data_seasons:
			total = len(json_data_seasons['seasons'])
			progress = total > 1
			if progress:
				count = 1
				loading = _("TMDB: ") + _("Loading...")
			for seasons in json_data_seasons['seasons']:
				if progress:
					self['searchinfo'].setText(f"{loading} ({count}/{total})")
					count += 1
				print(f"[TMDB] Season: {seasons['season_number']}")
				fid = str(seasons['id'])
				season = seasons['season_number']

				# Episodes
				json_data_episodes = tmdb.TV_Seasons(self.id, season).info(language=self.lang)
				titledate = str(json_data_episodes['air_date'])[:7]
				titledate = "" if titledate == "None" else f" ({titledate})"
				title = f"{json_data_episodes['name']} / {len(json_data_episodes['episodes'])}{titledate}"
				overview = json_data_episodes['overview']
				coverPath = json_data_episodes['poster_path']
				url_cover = self.imageURL(coverPath)
				self.list.append([False, ((title, url_cover, overview, fid, len(self.list)),)])

				eps = []
				for names in json_data_episodes['episodes']:
					fid = str(names['id'])
					title = str(names['episode_number'])
					name = names['name']
					title = f"{title:>6} {name}"
					overview = names['overview']
					coverPath = names['still_path']
					url_cover = self.imageURL(coverPath)
					if fid != "" or title != "":
						eps.append(((title, url_cover, overview, fid, None),))
				self.season_eps.append(eps)
			self.setList()
			self['searchinfo'].setText(self.mname)
		else:
			self['searchinfo'].setText(_("TMDB: ") + _("No results found, or does not respond!"))

	def setList(self):
		res = []
		season = 0
		for expanded, entry in self.list:
			res.append(entry)
			if expanded is not None:
				if expanded:
					res += self.season_eps[season]
				season += 1
		self['list'].setList(res)
		self.getInfo()

	def getInfo(self):
		check = self['list'].getCurrent()
		try:
			url_cover = check[1]
		except Exception:
			self.showCover(noCover)
			return
		self['data'].setText(check[2])
		if check[4] is None:
			state = ""
		else:
			state = self.list[check[4]][0] and _("Collapse") or _("Expand")
		self['key_green'].setText(state)
		if url_cover.endswith("None"):
			self.showCover(noCover)
		else:
			fid = check[3]
			fileName = f"{tempDir}{self.media}-{self.id}-{fid}.jpg"
			if not exists(fileName):
				self.delayDownload(url_cover, fileName, self.getData, self.dataError)
			else:
				self.showCover(fileName)

	def getData(self, coverSaved, url_cover):
		if 'list' in self and url_cover == self['list'].getCurrent()[1]:
			self.showCover(coverSaved)

	def dataError(self, error, url_cover):
		print(f"[TMDB] Error: {error}")
		self.getData(noCover, url_cover)

	def showCover(self, coverName):
		if not exists(coverName):
			coverName = noCover
		if exists(coverName):
			self.decodeCover(coverName)

	def ok(self):
		check = self['list'].getCurrent()
		if check is not None and check[4] is not None:
			self.list[check[4]][0] ^= True
			self.setList()

	def keyLeft(self):
		check = self['list'].getCurrent()
		if check is not None:
			self['list'].pageUp()
			self.getInfo()

	def keyRight(self):
		check = self['list'].getCurrent()
		if check is not None:
			self['list'].pageDown()
			self.getInfo()

	def keyDown(self):
		check = self['list'].getCurrent()
		if check is not None:
			self['list'].down()
			self.getInfo()

	def keyUp(self):
		check = self['list'].getCurrent()
		if check is not None:
			self['list'].up()
			self.getInfo()

	def chDown(self):
		self['data'].pageDown()

	def chUp(self):
		self['data'].pageUp()

	def keyBlue(self):
		self.session.open(tmdbConfigScreen)

	def cancel(self):
		self.close()


class tmdbScreenReviews(Screen, HelpableScreen, CoverHelper):
	skin = tmdbScreenReviewsSkin

	def __init__(self, session, mname, fid, media):
		Screen.__init__(self, session)
		self.mname = mname
		self.id = fid
		self.media = media
		self.movie = self.media == "movie"

		HelpableScreen.__init__(self)
		self["actions"] = HelpableActionMap(self, "TMDbActions",
			{
				"cancel": (self.cancel, _("Exit")),
				"up": (self.keyUp, _("Selection up")),
				"down": (self.keyDown, _("Selection down")),
				"prevBouquet": (self.chDown, _("Review down")),
				"nextBouquet": (self.chUp, _("Review up")),
				"right": (self.keyRight, _("Page down")),
				"left": (self.keyLeft, _("Page up")),
				"red": (self.cancel, _("Exit"))
			}, -1)

		self['searchinfo'] = Label(_("TMDB: ") + _("Loading..."))
		self['data'] = ScrollLabel("")
		self['key_red'] = Label(_("Exit"))
		self['list'] = createList()

		CoverHelper.__init__(self, True)

		self.onLayoutFinish.append(self.onFinish)

	def onFinish(self):
		# TMDB read
		print(f"[TMDB] Selected: {self.mname}")
		self.showBackdrop()
		callInThread(self.tmdbSearch)

	def tmdbSearch(self):
		self.lang = config.plugins.tmdb.lang.value
		self['searchinfo'].setText(_("TMDB: ") + _("Loading..."))
		# Reviews
		try:
			api = tmdb.Movies(self.id) if self.movie else tmdb.TV(self.id)
			json_data_reviews = api.reviews(language=self.lang)
			if json_data_reviews['total_results'] == 0 and self.lang != "en":
				json_data_reviews = api.reviews(language="en")
		except Exception as e:
			print("[TMDB] 6 api.reviews", e)
			self['searchinfo'].setText(_("TMDB: ") + _("No results found, or does not respond!"))
			return
		if json_data_reviews:
			res = []
			for review in json_data_reviews['results']:
				author = review['author']
				rating = review['author_details']['rating']
				if rating:
					rating = str(int(rating))
					if len(rating) == 1:
						rating = f"  {rating}"
				else:
					rating = "    "
				date = review['created_at'][:10]
				avatar = review['author_details']['avatar_path']
				content = review['content']
				# Strip supposed HTML tags.
				content = sub(r'</?[^>]+>', '', content)
				title = f"{rating}  {date} {author}"
				url_cover = self.avatarURL(avatar)
				res.append(((title, url_cover, content),))
			self['list'].setList(res)
			self.getInfo()
			self['searchinfo'].setText(self.mname)
			if not res:
				self['data'].setText(_("No reviews."))
		else:
			self['searchinfo'].setText(_("TMDB: ") + _("No results found, or does not respond!"))

	def getInfo(self):
		check = self['list'].getCurrent()
		try:
			url_cover = check[1]
		except Exception:
			self.showCover(noCoverP)
			return
		self['data'].setText(check[2])
		if url_cover.endswith("None"):
			self.showCover(noCoverP)
		else:
			fileName = f"{tempDir}avatar-{basename(url_cover)}"
			if not exists(fileName):
				self.delayDownload(url_cover, fileName, self.getData, self.dataError)
			else:
				self.showCover(fileName)

	def getData(self, coverSaved, url_cover):
		if 'list' in self and url_cover == self['list'].getCurrent()[1]:
			self.showCover(coverSaved)

	def dataError(self, error, url_cover):
		print(f"[TMDB] Error: {error}")
		self.getData(noCoverP, url_cover)

	def showCover(self, coverName):
		if not exists(coverName):
			coverName = noCoverP
		if exists(coverName):
			self.decodeCover(coverName)

	def keyLeft(self):
		check = self['list'].getCurrent()
		if check is not None:
			self['list'].pageUp()
			self.getInfo()

	def keyRight(self):
		check = self['list'].getCurrent()
		if check is not None:
			self['list'].pageDown()
			self.getInfo()

	def keyDown(self):
		check = self['list'].getCurrent()
		if check is not None:
			self['list'].down()
			self.getInfo()

	def keyUp(self):
		check = self['list'].getCurrent()
		if check is not None:
			self['list'].up()
			self.getInfo()

	def chDown(self):
		self['data'].pageDown()

	def chUp(self):
		self['data'].pageUp()

	def cancel(self):
		self.close()
