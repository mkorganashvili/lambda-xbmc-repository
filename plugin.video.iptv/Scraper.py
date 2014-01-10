import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmc,datetime,locale,time,string
from datetime import datetime, date, timedelta
from xml.dom import minidom
from Lib.net import Net
import CommonFunctions
from Lib.Navigation import Navigation
import json

common = CommonFunctions
common.plugin = "plugin.video.iptv"
common.dbg = True
#common.dbglevel = 5

nav = Navigation()
net = Net()

BASE_URL = 'http://iptv.ge'
RTMP_URL = ' swfUrl=http://www.iptv.ge/plugins/content/jw_allvideos/players/mediaplayer.swf'
    
class Scraper:
    
	def _GetChannels(self, url):
		content = net.http_GET(url).content
		items = common.parseDOM(content, "a", attrs = { "class": "thumbnail" }, ret=True)
		for item in items:
			href = common.parseDOM(item, "a", attrs = { "class": "thumbnail" }, ret='href')[0]
			name = common.parseDOM(item, "img", ret='alt')[0]
			thumbnail = common.parseDOM(item, "img", ret='src')[0]
			
			channelContent = net.http_GET(BASE_URL + href).content
			scripts = common.parseDOM(channelContent, "script", attrs = { "type": "text/javascript" })
			
			for script in scripts:
				tmp_lst = re.compile('jwplayer\("IPTVLiveStream"\).setup.*?', re.M | re.S).findall(script)
				if len(tmp_lst) > 0:
					fileName = re.compile('file: "(.*?)"').findall(script)[0]
					nav.addLink(name, fileName + RTMP_URL, '', thumbnail = thumbnail)
					break
	
	def GetChannels(self, url):
		content = net.http_GET(url).content
		items = common.parseDOM(content, "div", attrs = { "style": "width: 256px; margin: 2px 0px;position:relative;float:left" })
		for item in items:
			href = common.parseDOM(item, "a", attrs = { "class": "thumbnail" }, ret='href')[0]
			name = common.parseDOM(item, "img", ret='alt')[0]
			icon = common.parseDOM(item, "img", ret='src')[1]
			thumbnail = common.parseDOM(item, "img", ret='src')[0]
			
			channelContent = net.http_GET(BASE_URL + href).content
			scripts = common.parseDOM(channelContent, "script", attrs = { "type": "text/javascript" })
			
			for script in scripts:
				tmp_lst = re.compile('jwplayer\("IPTVLiveStream"\).setup.*?', re.M | re.S).findall(script)
				if len(tmp_lst) > 0:
					fileName = re.compile('file: "(.*?)"').findall(script)[0]
					nav.addLink(name, fileName + RTMP_URL, icon, thumbnail = thumbnail)
					break
	
			
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
	    
