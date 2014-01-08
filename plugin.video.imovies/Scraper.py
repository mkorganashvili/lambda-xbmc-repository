import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmc,datetime,locale,time,Navigation,string
from datetime import datetime, date, timedelta
from xml.dom import minidom
from Lib.net import Net
import CommonFunctions

common = CommonFunctions
common.plugin = "plugin.video.imovies"
nav = Navigation.Navigation()
net = Net()
    
class Scraper:
    
	def GetSeasons(self, url):
		urlMatcher = re.compile('http://www.imovies.ge/movies/([0-9]+)', re.DOTALL).findall(url)
		movieId = urlMatcher[0]
		
                req = urllib2.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                response = urllib2.urlopen(req)
                link = response.read()
                response.close()
                match = re.compile('<li><a data-group="(.+?)" href="#episodes-list-season-[0-9]+" class=".+?">([0-9]+)</a></li>').findall(link)
                for name, season in match:
                        nav.addDir('Season %s' % (season), 'http://www.imovies.ge/get_playlist_jwQ.php?movie_id=%s&activeseria=0&group=sezoni %s' % (movieId, season), 'GetEpisodes', '')
	
	def GetEpisodes(self, url, params):
		req = urllib2.Request(url)
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
		u = urllib2.urlopen(req)
		xmldoc = minidom.parse(u)
		u.close()
		itemlist = xmldoc.getElementsByTagName('item') 
			
		for item in itemlist:
			name = re.sub('<[^<]+?>', '', item.getElementsByTagName('description')[0].firstChild.nodeValue)
			url = item.getElementsByTagName('jwplayer:source')[0].attributes['file'].value + '/ENG'	
			thumbnail = item.getElementsByTagName('jwplayer:image')[0].firstChild.nodeValue
			nav.addLink(name, url, '', thumbnail = thumbnail)
                
	def GetUser(self, url):
		content = net.http_GET(url).content
		userBox = common.parseDOM(content, "div", attrs = { "class": "userbox" })[0]
		name = common.parseDOM(userBox, "div", attrs = { "class": "firstname" })[0] + ' ' + common.parseDOM(userBox, "div", attrs = { "class": "lastname" })[0]
		avatar = common.parseDOM(userBox, "img", ret="src")[0]
		nav.addDir(name, url, 'WatchList', avatar, thumbnail = avatar)
	
	def GetWatchlist(self, url):
		content = net.http_GET(url + '/watchlist').content
		items = common.parseDOM(content, "div", attrs = { "class": "item[^\"']*" })
		
		for item in items:
			title_ge = re.sub('<[^<]+?>', '', common.parseDOM(item, "h2", attrs = { "class": "film_title[^\"']*" })[0])
			title_en = re.sub('<[^<]+?>', '', common.parseDOM(item, "h2", attrs = { "class": "film_title[^\"']*" })[1])
			imageDiv = common.parseDOM(item, "div", attrs = { "class": "cropped_image" })[0]
			movieUrl = common.parseDOM(item, "a", ret="href")[0]
			thumbnail = common.parseDOM(item, "img", ret="src")[0]
			
			movieId = common.parseDOM(item, "a", attrs = { "class": "wishlist[^\"']*" }, ret="film_id")[0]
			movieInfo = net.http_GET('http://www.imovies.ge/get_playlist_temp.php?activeseria=0&group=&language=ENG&movie_id=' + movieId).content
			movieItems = common.parseDOM(movieInfo, "item")
			if movieItems:
				fileUrl = common.parseDOM(movieInfo, "implayer:hd.file")[0]
				nav.addLink(title_en, fileUrl, 'movie', thumbnail)
			else:
				nav.addDir(title_en, 'http://www.imovies.ge' + movieUrl, 'TVSeries', '', thumbnail = thumbnail)
	
	def GETTVLINKS(self, url, name):
		req = urllib2.Request(url)
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
		response = urllib2.urlopen(req)
		link=response.read()
		response.close()
		match=re.compile("'chan':'(.+?)','dvrServer':'(.+?)myvideo.ge/(.+?)'").findall(link)
		mp4prefix = re.compile("'mp4Prefix':'(.+?)'").findall(link)
		chan = url.split('&chan=')[1]
		playpath = chan
		
		if len(match) < 1:
			dvr = 'rtmp://orig3.grt.myvideo.ge/dvrm/' + chan
			app = 'dvrm/' + chan
		else:
			dvr = match[0][1] + 'myvideo.ge/' + match[0][2]
			app = match[0][2]
			chan = match[0][0]
			playpath = chan
			if len(mp4prefix) > 0:
			    playpath = mp4prefix[0] + chan
			    
		videourl = dvr + ' swfUrl=http://www.myvideo.ge/dvr/dvrH.swf?v=1.04b pageURL=http://www.myvideo.ge/?act=dvr&chan= app=' + app + ' playpath='# + playpath
		#xbmcgui.Dialog().ok('opaa', dvr, app, chan)
		nav.addLink(name + ' on air', videourl + ' live=true', '')
		nav.addDir('გადახვევა', videourl, 'getdaytable', '', { 'name' : name, 'chan' : chan })            
	
	
	def GETDAYTABLE(self, url, params, daycount = 20):        
		for i in range(daycount):
			d = date.today() - timedelta(i)
			nav.addDir(d.strftime("%d %B, %A"), url, 'choosetime', '', { 'seekdate' : d, 'name' : params['name'], 'chan' : params['chan'] }, False) #.strftime("%d-%m-%Y")
			
	
	def CHOOSETIME(self, videourl, params):
		#http://myvideo.ge/dvr_getfile.php?mode=file&date=05-04-2011%2011:21&chan=rustavi2
		t = xbmcgui.Dialog().numeric(2, 'შეიყვანეთ სასურველი დრო')
		t = t.replace(' ', '')
		if len(t) == 4:
			t = '0' + t
		params['seektime'] = datetime(*(time.strptime(params['seekdate'] + ' ' + t, '%Y-%m-%d %H:%M')[0:6]))
		params['videourl'] = videourl
		self.PLAYVIDEO(params)
	
	def PLAYVIDEO(self, params, doSeek = True):
		seektime = params['seektime']
	
		url = 'http://myvideo.ge/dvr_getfile.php?mode=file&date=%s&chan=%s' % (seektime.strftime("%Y-%m-%d") + '%20' + seektime.strftime("%H:%M"), params['chan'])
		req = urllib2.Request(url)
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
		response = urllib2.urlopen(req)
		link=response.read()
		response.close()
    
		filename = re.compile('<file>(.+?)</file>').findall(link)
		dvrstart = re.compile('<dvr_start>(.+?)</dvr_start>').findall(link)
		dvrend = re.compile('<dvr_end>(.+?)</dvr_end>').findall(link)
		#xbmcgui.Dialog().ok('t', len(re.compile('<file>(.+?)</file>').findall(link)));
		if (not len(filename)):
			xbmcgui.Dialog().ok('შეცდომა', 'სამწუხაროდ ფაილი არ მოიძებნა')
			return
	
		dvrstart = datetime(*(time.strptime(dvrstart[0], '%Y-%m-%d %H:%M:%S')[0:6]))
		print 'response: ' + link
		#dvrend = datetime(*(time.strptime(dvrend[0], '%Y-%m-%d %H:%M:%S')[0:6]))
	
		player = TVPlayer() #xbmc.Player()
		player.currentParams = params
		player.play(params['videourl'] + filename[0])
		if doSeek:
			seek = seektime - dvrstart + timedelta(minutes = 1)
			player.seekTime(seek.seconds)
	
		while player.isPlaying() and player.getPlayingFile().find(filename[0]) > -1:
			xbmc.sleep(500)
		print 'sleep end ' + filename[0]
	
	def VIDEOLINKS(self, url, name):
		req = urllib2.Request(url)
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
		response = urllib2.urlopen(req)
		link=response.read()
		response.close()
		match=re.compile('').findall(link)
		for url in match:
			nav.addLink(name,'','')
    
	class TVPlayer(xbmc.Player):
		def onPlayBackStopped(self):
			print 'opaaa finish'
			#xbmcgui.Dialog().ok('opaa', 'finish')
			    
		def onPlayBackEnded(self):
			#xbmcgui.Dialog().ok('opaa', 'end', self.currentParams['videourl'])
			self.currentParams['seektime'] += timedelta(hours = 3)
			PLAYVIDEO(self.currentParams, False)                
    
		def onPlayBackStarted(self):
			print 'opaa start'
			#xbmcgui.Dialog().ok('opaa', 'start')
	    
