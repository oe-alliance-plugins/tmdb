from enigma import getDesktop

if getDesktop(0).size().width() >= 1920:
	tmdbListParams = (32, 40)
	tmdbScreenSkin = """
		<screen position="30,90" size="1860,970" title="TMDB - The Movie Database">
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/backdrop_dark.png" position="0,0" size="e,e" zPosition="-4" alphatest="blend"/>
			<widget name="searchinfo" position="20,30" size="1800,40" font="Regular;32" foregroundColor="#00fff000" transparent="1"/>
			<widget name="list" position="20,90" size="1250,680" scrollbarMode="showOnDemand" transparent="1"/>
			<widget name="cover" position="1500,90" size="320,480" alphatest="blend"/>
			<widget name="title_txt" position="1330,600" size="170,62" font="Regular;27" valign="bottom" transparent="1"/>
			<widget name="title" position="1500,600" size="320,62" font="Regular;27" valign="bottom" transparent="1"/>
			<widget name="lang_txt" position="1330,670" size="170,31" font="Regular;27" transparent="1"/>
			<widget name="lang" position="1500,670" size="320,31" noWrap="1" font="Regular;27" transparent="1"/>
			<widget name="rating_txt" position="1330,711" size="170,31" font="Regular;27" transparent="1"/>
			<widget name="rating" position="1500,711" size="320,31" noWrap="1" font="Regular;27" transparent="1"/>
			<widget name="overview" position="20,775" size="1250,120" font="Regular;25" transparent="1"/>
			<widget name="key_red" position="325,922" size="280,31" font="Regular;25" transparent="1"/>
			<widget name="key_green" position="665,922" size="280,31" font="Regular;25" transparent="1"/>
			<widget name="key_yellow" position="1005,922" size="280,31" font="Regular;25" transparent="1"/>
			<widget name="key_blue" position="1345,922" size="280,31" font="Regular;25" transparent="1"/>
			<ePixmap position="290,925" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_red.png" transparent="1" alphatest="on"/>
			<ePixmap position="630,925" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_green.png" transparent="1" alphatest="on"/>
			<ePixmap position="970,925" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_yellow.png" transparent="1" alphatest="on"/>
			<ePixmap position="1310,925" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_blue.png" transparent="1" alphatest="on"/>
		</screen>"""

	tmdbScreenMovieSkin = """
		<screen position="30,90" size="1860,970" title="TMDB - The Movie Database">
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/backdrop_dark.png" position="0,0" size="e,e" zPosition="-4" alphatest="blend"/>
			<widget name="backdrop" position="0,0" size="e,e" zPosition="-5" alphatest="blend"/>
			<widget name="searchinfo" position="20,30" size="1800,40" font="Regular;32" foregroundColor="#00fff000" transparent="1"/>
			<widget name="fulldescription" position="20,90" size="950,800" font="Regular;28" transparent="1"/>
			<ePixmap position="1025,90" size="150,150" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/star.png" transparent="1" scale="1" alphatest="blend"/>
			<widget name="rating" position="1025,150" size="150,37" zPosition="2" font="Regular;33" halign="center" foregroundColor="black" backgroundColor="#00ffba00" transparent="1"/>
			<widget name="votes_brackets" position="1025,240" size="150,30" font="Regular;27" halign="center" transparent="1"/>
			<widget name="fsk" position="1250,90" size="150,150" font="Regular;33" halign="center" valign="center" transparent="1"/>
			<widget name="fsklogo" position="1250,90" size="150,150" alphatest="blend"/>
			<widget name="cover" position="1500,90" size="320,480" alphatest="blend"/>
			<widget name="year_txt" position="1000,430" size="130,33" font="Regular;27" transparent="1"/>
			<widget name="year" position="1130,430" size="370,33" noWrap="1" font="Regular;27" transparent="1"/>
			<widget name="country_txt" position="1000,465" size="130,33" font="Regular;27" transparent="1"/>
			<widget name="country" position="1130,465" size="370,33" noWrap="1" font="Regular;27" transparent="1"/>
			<widget name="runtime_txt" position="1000,500" size="130,33" font="Regular;27" transparent="1"/>
			<widget name="runtime" position="1130,500" size="370,33" noWrap="1" font="Regular;27" transparent="1"/>
			<widget name="votes_txt" position="1000,535" size="130,33" font="Regular;27" transparent="1"/>
			<widget name="votes" position="1130,535" size="370,33" noWrap="1" font="Regular;27" transparent="1"/>
			<widget name="director_txt" position="1000,570" size="130,33" font="Regular;27" transparent="1"/>
			<widget name="director" position="1130,570" size="690,33" noWrap="1" font="Regular;27" transparent="1"/>
			<widget name="author_txt" position="1000,605" size="130,33" font="Regular;27" transparent="1"/>
			<widget name="author" position="1130,605" size="690,33" noWrap="1" font="Regular;27" transparent="1"/>
			<widget name="genre_txt" position="1000,640" size="130,33" font="Regular;27" transparent="1"/>
			<widget name="genre" position="1130,640" size="690,33" noWrap="1" font="Regular;27" transparent="1"/>
			<widget name="studio_txt" position="1000,675" size="130,33" font="Regular;27" transparent="1"/>
			<widget name="studio" position="1130,675" size="690,66" valign="top" font="Regular;27" transparent="1"/>
			<widget name="key_red" position="325,922" size="280,31" font="Regular;25" transparent="1"/>
			<widget name="key_green" position="665,922" size="280,31" font="Regular;25" transparent="1"/>
			<widget name="key_yellow" position="1005,922" size="280,31" font="Regular;25" transparent="1"/>
			<widget name="key_blue" position="1345,922" size="280,31" font="Regular;25" transparent="1"/>
			<ePixmap position="290,925" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_red.png" transparent="1" alphatest="on"/>
			<ePixmap position="630,925" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_green.png" transparent="1" alphatest="on"/>
			<ePixmap position="970,925" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_yellow.png" transparent="1" alphatest="on"/>
			<ePixmap position="1310,925" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_blue.png" transparent="1" alphatest="on"/>
		</screen>"""

	tmdbScreenPeopleSkin = """
		<screen position="30,90" size="1860,970" title="TMDB - The Movie Database">
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/backdrop_dark.png" position="0,0" size="e,e" zPosition="-4" alphatest="blend"/>
			<widget name="backdrop" position="0,0" size="e,e" zPosition="-5" alphatest="blend"/>
			<widget name="searchinfo" position="20,30" size="1800,40" font="Regular;32" foregroundColor="#00fff000" transparent="1"/>
			<widget name="list" position="20,90" size="1350,800" scrollbarMode="showOnDemand" transparent="1"/>
			<widget name="cover" position="1500,90" size="320,480" alphatest="blend"/>
			<widget name="key_red" position="325,922" size="280,31" font="Regular;25" transparent="1"/>
			<widget name="key_green" position="665,922" size="280,31" font="Regular;25" transparent="1"/>
			<widget name="key_blue" position="1345,922" size="280,31" font="Regular;25" transparent="1"/>
			<ePixmap position="290,925" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_red.png" transparent="1" alphatest="on"/>
			<ePixmap position="630,925" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_green.png" transparent="1" alphatest="on"/>
			<ePixmap position="970,925" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_yellow.png" transparent="1" alphatest="on"/>
			<ePixmap position="1310,925" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_blue.png" transparent="1" alphatest="on"/>
		</screen>"""

	tmdbScreenPersonSkin = """
		<screen position="30,90" size="1860,970" title="TMDB - The Movie Database">
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/backdrop_dark.png" position="0,0" size="e,e" zPosition="-4" alphatest="blend"/>
			<widget name="backdrop" position="0,0" size="e,e" zPosition="-5" alphatest="blend"/>
			<widget name="searchinfo" position="20,30" size="1800,40" font="Regular;32" foregroundColor="#00fff000" transparent="1"/>
			<widget name="fulldescription" position="20,90" size="1350,800" font="Regular;28" transparent="1"/>
			<widget name="cover" position="1500,90" size="320,480" alphatest="blend"/>
			<widget name="key_red" position="325,922" size="280,31" font="Regular;25" transparent="1"/>
			<widget name="key_yellow" position="1005,922" size="280,31" font="Regular;25" transparent="1"/>
			<ePixmap position="290,925" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_red.png" transparent="1" alphatest="on"/>
			<ePixmap position="630,925" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_green.png" transparent="1" alphatest="on"/>
			<ePixmap position="970,925" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_yellow.png" transparent="1" alphatest="on"/>
			<ePixmap position="1310,925" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_blue.png" transparent="1" alphatest="on"/>
		</screen>"""

	tmdbScreenSeasonSkin = """
		<screen position="30,90" size="1860,970" title="TMDB - The Movie Database">
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/backdrop_dark.png" position="0,0" size="e,e" zPosition="-4" alphatest="blend"/>
			<widget name="backdrop" position="0,0" size="e,e" zPosition="-5" alphatest="blend"/>
			<widget name="searchinfo" position="20,30" size="1800,40" font="Regular;32" foregroundColor="#00fff000" transparent="1"/>
			<widget name="list" position="20,90" size="920,480" scrollbarMode="showOnDemand" transparent="1"/>
			<widget name="cover" position="966,90" size="854,480" alphatest="blend"/>
			<widget name="data" position="20,590" size="1250,300" font="Regular;28" transparent="1"/>
			<widget name="key_red" position="325,922" size="280,31" font="Regular;25" transparent="1"/>
			<widget name="key_green" position="665,922" size="280,31" font="Regular;25" transparent="1"/>
			<widget name="key_blue" position="1345,922" size="280,31" font="Regular;25" transparent="1"/>
			<ePixmap position="290,925" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_red.png" transparent="1" alphatest="on"/>
			<ePixmap position="630,925" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_green.png" transparent="1" alphatest="on"/>
			<ePixmap position="970,925" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_yellow.png" transparent="1" alphatest="on"/>
			<ePixmap position="1310,925" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_blue.png" transparent="1" alphatest="on"/>
		</screen>"""

	tmdbScreenReviewsSkin = """
		<screen position="30,90" size="1860,970" title="TMDB - The Movie Database">
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/backdrop_dark.png" position="0,0" size="e,e" zPosition="-4" alphatest="blend"/>
			<widget name="backdrop" position="0,0" size="e,e" zPosition="-5" alphatest="blend"/>
			<widget name="searchinfo" position="20,30" size="1800,40" font="Regular;32" foregroundColor="#00fff000" transparent="1"/>
			<widget name="list" position="20,90" size="620,480" scrollbarMode="showAlways" transparent="1"/>
			<widget name="cover" position="180,590" size="300,300" alphatest="blend"/>
			<widget name="data" position="660,90" size="1180,800" font="Regular;28" transparent="1"/>
			<widget name="key_red" position="325,922" size="280,31" font="Regular;25" transparent="1"/>
			<ePixmap position="290,925" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_red.png" transparent="1" alphatest="on"/>
			<ePixmap position="630,925" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_green.png" transparent="1" alphatest="on"/>
			<ePixmap position="970,925" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_yellow.png" transparent="1" alphatest="on"/>
			<ePixmap position="1310,925" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_blue.png" transparent="1" alphatest="on"/>
		</screen>"""

else:
	tmdbListParams = (24, 32)
	tmdbScreenSkin = """
		<screen position="40,80" size="1200,600" title="TMDB - The Movie Database">
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/backdrop_dark.png" position="0,0" size="e,e" zPosition="-4" alphatest="blend"/>
			<widget name="searchinfo" position="10,10" size="1180,30" font="Regular;24" foregroundColor="#00fff000" transparent="1"/>
			<widget name="list" position="10,60" size="700,384" scrollbarMode="showOnDemand" transparent="1"/>
			<widget name="cover" position="850,60" size="250,375" alphatest="blend"/>
			<widget name="title_txt" position="730,445" size="110,50" font="Regular;22" valign="bottom" transparent="1"/>
			<widget name="title" position="850,445" size="340,50" font="Regular;22" valign="bottom" transparent="1"/>
			<widget name="lang_txt" position="730,495" size="110,25" font="Regular;22" transparent="1"/>
			<widget name="lang" position="850,495" size="340,25" noWrap="1" font="Regular;22" transparent="1"/>
			<widget name="rating_txt" position="730,525" size="110,25" font="Regular;22" transparent="1"/>
			<widget name="rating" position="850,525" size="340,25" noWrap="1" font="Regular;22" transparent="1"/>
			<widget name="overview" position="10,450" size="700,100" font="Regular;20" transparent="1"/>
			<widget name="key_red" position="100,570" size="260,25" font="Regular;20" transparent="1"/>
			<widget name="key_green" position="395,570" size="260,25" font="Regular;20" transparent="1"/>
			<widget name="key_yellow" position="690,570" size="260,25" font="Regular;20" transparent="1"/>
			<widget name="key_blue" position="985,570" size="205,25" font="Regular;20" transparent="1"/>
			<ePixmap position="70,570" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_red.png" transparent="1" alphatest="on"/>
			<ePixmap position="365,570" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_green.png" transparent="1" alphatest="on"/>
			<ePixmap position="660,570" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_yellow.png" transparent="1" alphatest="on"/>
			<ePixmap position="955,570" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_blue.png" transparent="1" alphatest="on"/>
		</screen>"""

	tmdbScreenMovieSkin = """
		<screen position="40,80" size="1200,600" title="TMDB - The Movie Database">
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/backdrop_dark.png" position="0,0" size="e,e" zPosition="-4" alphatest="blend"/>
			<widget name="backdrop" position="0,0" size="e,e" zPosition="-5" alphatest="blend"/>
			<widget name="searchinfo" position="10,10" size="1180,30" font="Regular;24" foregroundColor="#00fff000" transparent="1"/>
			<widget name="fulldescription" position="10,60" size="620,490" font="Regular;24" transparent="1"/>
			<ePixmap position="665,60" size="100,100" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/star.png" transparent="1" scale="1" alphatest="blend"/>
			<widget name="rating" position="640,100" size="150,25" zPosition="2" font="Regular;22" halign="center" foregroundColor="black" backgroundColor="#00ffba00" transparent="1"/>
			<widget name="votes_brackets" position="640,160" size="150,25" font="Regular;22" halign="center" transparent="1"/>
			<widget name="fsk" position="805,60" size="100,100" font="Regular;22" halign="center" valign="center" transparent="1"/>
			<widget name="fsklogo" position="805,60" size="100,100" alphatest="blend"/>
			<widget name="cover" position="950,60" size="200,300" alphatest="blend"/>
			<widget name="year_txt" position="650,310" size="130,25" font="Regular;22" transparent="1"/>
			<widget name="year" position="780,310" size="170,25" noWrap="1" font="Regular;22" transparent="1"/>
			<widget name="country_txt" position="650,340" size="130,25" font="Regular;22" transparent="1"/>
			<widget name="country" position="780,340" size="170,25" noWrap="1" font="Regular;22" transparent="1"/>
			<widget name="runtime_txt" position="650,370" size="130,25" font="Regular;22" transparent="1"/>
			<widget name="runtime" position="780,370" size="410,25" noWrap="1" font="Regular;22" transparent="1"/>
			<widget name="votes_txt" position="650,400" size="0,0" font="Regular;22" transparent="1"/>
			<widget name="votes" position="780,400" size="0,0" noWrap="1" font="Regular;22" transparent="1"/>
			<widget name="director_txt" position="650,400" size="130,25" font="Regular;22" transparent="1"/>
			<widget name="director" position="780,400" size="410,25" noWrap="1" font="Regular;22" transparent="1"/>
			<widget name="author_txt" position="650,430" size="130,25" font="Regular;22" transparent="1"/>
			<widget name="author" position="780,430" size="410,25" noWrap="1" font="Regular;22" transparent="1"/>
			<widget name="genre_txt" position="650,460" size="130,25" font="Regular;22" transparent="1"/>
			<widget name="genre" position="780,460" size="410,25" noWrap="1" font="Regular;22" transparent="1"/>
			<widget name="studio_txt" position="650,490" size="130,25" font="Regular;22" transparent="1"/>
			<widget name="studio" position="780,490" size="410,50" valign="top" font="Regular;22" transparent="1"/>
			<widget name="key_red" position="100,570" size="260,25" font="Regular;20" transparent="1"/>
			<widget name="key_green" position="395,570" size="260,25" font="Regular;20" transparent="1"/>
			<widget name="key_yellow" position="690,570" size="260,25" font="Regular;20" transparent="1"/>
			<widget name="key_blue" position="985,570" size="205,25" font="Regular;20" transparent="1"/>
			<ePixmap position="70,570" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_red.png" transparent="1" alphatest="on"/>
			<ePixmap position="365,570" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_green.png" transparent="1" alphatest="on"/>
			<ePixmap position="660,570" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_yellow.png" transparent="1" alphatest="on"/>
			<ePixmap position="955,570" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_blue.png" transparent="1" alphatest="on"/>
		</screen>"""

	tmdbScreenPeopleSkin = """
		<screen position="40,80" size="1200,600" title="TMDB - The Movie Database">
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/backdrop_dark.png" position="0,0" size="e,e" zPosition="-4" alphatest="blend"/>
			<widget name="backdrop" position="0,0" size="e,e" zPosition="-5" alphatest="blend"/>
			<widget name="searchinfo" position="10,10" size="1180,30" font="Regular;24" foregroundColor="#00fff000" transparent="1"/>
			<widget name="list" position="10,60" size="900,480" scrollbarMode="showOnDemand" transparent="1"/>
			<widget name="cover" position="950,60" size="200,300" alphatest="blend"/>
			<widget name="key_red" position="100,570" size="260,25" font="Regular;20" transparent="1"/>
			<widget name="key_green" position="395,570" size="260,25" font="Regular;20" transparent="1"/>
			<widget name="key_blue" position="985,570" size="205,25" font="Regular;20" transparent="1"/>
			<ePixmap position="70,570" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_red.png" transparent="1" alphatest="on"/>
			<ePixmap position="365,570" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_green.png" transparent="1" alphatest="on"/>
			<ePixmap position="660,570" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_yellow.png" transparent="1" alphatest="on"/>
			<ePixmap position="955,570" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_blue.png" transparent="1" alphatest="on"/>
		</screen>"""

	tmdbScreenPersonSkin = """
		<screen position="40,80" size="1200,600" title="TMDB - The Movie Database">
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/backdrop_dark.png" position="0,0" size="e,e" zPosition="-4" alphatest="blend"/>
			<widget name="backdrop" position="0,0" size="e,e" zPosition="-5" alphatest="blend"/>
			<widget name="searchinfo" position="10,10" size="1180,30" font="Regular;24" foregroundColor="#00fff000" transparent="1"/>
			<widget name="fulldescription" position="10,60" size="900,490" font="Regular;24" transparent="1"/>
			<widget name="cover" position="950,60" size="200,300" alphatest="blend"/>
			<widget name="key_red" position="100,570" size="260,25" font="Regular;20" transparent="1"/>
			<widget name="key_yellow" position="690,570" size="260,25" font="Regular;20" transparent="1"/>
			<ePixmap position="70,570" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_red.png" transparent="1" alphatest="on"/>
			<ePixmap position="365,570" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_green.png" transparent="1" alphatest="on"/>
			<ePixmap position="660,570" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_yellow.png" transparent="1" alphatest="on"/>
			<ePixmap position="955,570" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_blue.png" transparent="1" alphatest="on"/>
		</screen>"""

	tmdbScreenSeasonSkin = """
		<screen position="40,80" size="1200,600" title="TMDB - The Movie Database">
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/backdrop_dark.png" position="0,0" size="e,e" zPosition="-4" alphatest="blend"/>
			<widget name="backdrop" position="0,0" size="e,e" zPosition="-5" alphatest="blend"/>
			<widget name="searchinfo" position="10,10" size="1180,30" font="Regular;24" foregroundColor="#00fff000" transparent="1"/>
			<widget name="list" position="10,60" size="480,360" scrollbarMode="showOnDemand" transparent="1"/>
			<widget name="cover" position="525,60" size="640,360" alphatest="blend"/>
			<widget name="data" position="10,430" size="1180,120" font="Regular;23" transparent="1"/>
			<widget name="key_red" position="100,570" size="260,25" font="Regular;20" transparent="1"/>
			<widget name="key_green" position="395,570" size="260,25" font="Regular;20" transparent="1"/>
			<widget name="key_blue" position="985,570" size="205,25" font="Regular;20" transparent="1"/>
			<ePixmap position="70,570" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_red.png" transparent="1" alphatest="on"/>
			<ePixmap position="365,570" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_green.png" transparent="1" alphatest="on"/>
			<ePixmap position="660,570" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_yellow.png" transparent="1" alphatest="on"/>
			<ePixmap position="955,570" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_blue.png" transparent="1" alphatest="on"/>
		</screen>"""

	tmdbScreenReviewsSkin = """
		<screen position="40,80" size="1200,600" title="TMDB - The Movie Database">
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/backdrop_dark.png" position="0,0" size="e,e" zPosition="-4" alphatest="blend"/>
			<widget name="backdrop" position="0,0" size="e,e" zPosition="-5" alphatest="blend"/>
			<widget name="searchinfo" position="10,10" size="1180,30" font="Regular;24" foregroundColor="#00fff000" transparent="1"/>
			<widget name="list" position="10,60" size="400,224" scrollbarMode="showAlways" transparent="1"/>
			<widget name="cover" position="85,300" size="250,250" alphatest="blend"/>
			<widget name="data" position="420,60" size="770,490" font="Regular;23" transparent="1"/>
			<widget name="key_red" position="100,570" size="260,25" font="Regular;20" transparent="1"/>
			<ePixmap position="70,570" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_red.png" transparent="1" alphatest="on"/>
			<ePixmap position="365,570" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_green.png" transparent="1" alphatest="on"/>
			<ePixmap position="660,570" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_yellow.png" transparent="1" alphatest="on"/>
			<ePixmap position="955,570" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tmdb/pic/button_blue.png" transparent="1" alphatest="on"/>
		</screen>"""
