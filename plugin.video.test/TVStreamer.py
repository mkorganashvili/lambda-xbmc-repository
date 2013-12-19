import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmc,datetime,locale,time,MyVideoNavigation,string,json
from datetime import datetime, date, timedelta

nav = MyVideoNavigation.MyVideoNavigation()
    
class TVStreamer:
    
	def AddTvSeasons(self, url):
		urlMatcher = re.compile('http://adjaranet.com/Movie/main\\?id=([0-9]+)&serie=([0-9]+)', re.DOTALL).findall(url)
		movieId = urlMatcher[0][0]
		season = 1
		while season > 0:
			seasonsUrl = 'http://adjaranet.com/req/series/req.php?reqId=series_list&id=' + movieId + '&season=' + str(season)
			
			req = urllib2.Request(seasonsUrl)
			req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
			u = urllib2.urlopen(req)
			result = json.load(u)
			u.close()
			      
			if len(result) > 0:
				title = 'Season ' + str(season)
				nav.addDir(title, seasonsUrl, 'GetEpisodes', 'http://static.adjaranet.com/moviecontent/' + str(movieId) + '/covers/214x321-' + str(movieId) + '.jpg')
				season = season + 1
			else:
				season = 0
	
	def GetEpisodes(self, url, params):
		req = urllib2.Request(url)
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
		u = urllib2.urlopen(req)
		result = json.load(u)
		u.close()
			
		for row in result:
			nav.addLink(row['name'], 'rtmp://edge2.vod.adjaranet.com/vod playpath=mp4:{0}/{0}_{1}_{2}_English_800'.format(params['id'], params['season'].rjust(2, '0'), row['episode'].rjust(2, '0')), '')
                
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
	    
