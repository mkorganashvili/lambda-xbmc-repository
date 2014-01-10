import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmc,datetime,locale,time,string,ast
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

BASE_URL = 'http://www.myvideo.ge'
RTMP_URL = ' app=dvrh264/{0} playpath=mp4:{0} swfUrl=http://www.myvideo.ge/dvr/dvrAvatar7.swf?v=1.91 pageURL=http://www.myvideo.ge live=true'
    
class Scraper:
    
	def GetChannels(self, url):
		content = net.http_GET(url, { "Cookie": "lang_id=eng"}).content
		items = common.parseDOM(content, "div", attrs = { "class": "livetv_grid_item_holder[^\"']*" })
		for item in items:
			icon = common.parseDOM(item, "div", attrs = { "class": "tv_logo" }, ret='style')[0]
			href = common.parseDOM(item, "a", ret='href')[0]
			name = common.parseDOM(item, "div", attrs = { "class": "tv_title" })[0]
			channel = common.parseDOM(item, "div", attrs = { "class": "tv_logo" }, ret='alt')[0]
			
			icon = BASE_URL + re.compile("background-image:url\('(.*?)'\)").findall(icon)[0]
			name = common.stripTags(name).encode('utf-8')
			
			nav.addDir(name, BASE_URL + '/' + href, 'PlayTV', icon, thumbnail = icon, isFolder = False)
	
	
	def PlayTV(self, url):
			content = net.http_GET(url).content
			flashvars = re.compile("var flashvars = \{(.*?)\}", re.DOTALL).findall(content)[0]			
			chan = re.compile("'chan':'(.*?)'").findall(flashvars)[0]
			dvrServer = re.compile("'dvrServer':'(.*?)'").findall(flashvars)[0]
			name = common.parseDOM(content, "div", attrs = { "class": "mv_user_channel_name[^\"']*" })[0]
			name = common.stripTags(name)
			
			listitem = xbmcgui.ListItem(name)
			listitem.setInfo('video', {'Title': name})
			xbmc.Player().play(dvrServer + RTMP_URL.format(chan), listitem)

		
	
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
	    
