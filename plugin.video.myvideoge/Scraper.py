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
RTMP_URL = ' app=dvrh264/{0} playpath={1} swfUrl=http://www.myvideo.ge/dvr/dvrAvatar7.swf?v=1.91 pageURL=http://www.myvideo.ge'
    
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
			
			nav.addDir(name, BASE_URL + '/' + href, 'Channel', icon, thumbnail = icon)
	
	def GetTvSchedule(self, url):
		playerParams = self.GetPlayerData(url)
		nav.addDir('Live', '#', 'PlayTV', '', playerParams, isFolder = False)
		
		params = common.getParameters(url)
		scheduleUrl = 'http://www.myvideo.ge/dvr_getfile.php?mode=prog&chan={0}&date={1:%Y-%m-%d}'.format(params['chan'], datetime.now())
		content = net.http_GET(scheduleUrl, { "Cookie": "lang_id=eng"}).content
		
		common.log(scheduleUrl)
		
		progs = common.parseDOM(content, "prog")
		for prog in progs:
			date = common.parseDOM(prog, 'date')
			time = common.parseDOM(prog, 'time')[0]
			mins = common.parseDOM(prog, 'mins')[0]
			name = common.parseDOM(prog, 'name')[0]
			pss = common.parseDOM(prog, 'pass')
			timeUrl = BASE_URL + '/dvr_getfile.php?mode=file&chan={0}&date={1}'.format(params['chan'], urllib.quote_plus(time))
			
			nav.addDir(mins.encode('utf-8') + ' - ' + name.encode('utf-8'), timeUrl, 'PlayByTime', '', playerParams, isFolder = False)
			
	def PlayByTime(self, url, params):		
		content = net.http_GET(url, { "Cookie": "lang_id=eng"}).content
		file = common.parseDOM(content, 'file')[0]
	
		listitem = xbmcgui.ListItem(params['name'])
		listitem.setInfo('video', {'Title': params['name']})
		xbmc.Player().play(params['dvrServer'] + RTMP_URL.format(params['chan'], file), listitem)
		
	def PlayTV(self, url, params):
		listitem = xbmcgui.ListItem(params['name'])
		listitem.setInfo('video', {'Title': params['name']})
		xbmc.Player().play(params['dvrServer'] + RTMP_URL.format(params['chan'], 'mp4:' + params['chan']) + ' live=true', listitem)

	def GetPlayerData(self, url):
		content = net.http_GET(url).content
		flashvars = re.compile("var flashvars = \{(.*?)\}", re.DOTALL).findall(content)[0]			
		chan = re.compile("'chan':'(.*?)'").findall(flashvars)[0]
		dvrServer = re.compile("'dvrServer':'(.*?)'").findall(flashvars)[0]
		name = common.parseDOM(content, "div", attrs = { "class": "mv_user_channel_name[^\"']*" })[0]
		name = common.stripTags(name).encode('utf8')
		common.log(urllib.quote_plus(name))
		return {
			'chan': chan,
			'dvrServer': dvrServer,
			'name': name
		}
 
	def GetVideoChannels(self, params):
		self.GetVideos('http://www.myvideo.ge/TV11&latest=true', params)
 
	def GetVideos(self, url,  params):
		urlWithParams = url
		if params:
			urlWithParams = url + '&per_page=' + params['skip']
		else:
			params = { 'skip': 0 }
	
		content = net.http_GET(urlWithParams, { "Cookie": "lang_id=eng"}).content
		items = common.parseDOM(content, "div", attrs = { "class": "mv_video_item medium[^\"']*" })
		for item in items:
			thumbnail = common.parseDOM(item, "a", attrs = { "class": "vd_go_to_video[^\"']*" }, ret='style')[0]
			thumbnail = re.compile("background-image:url\((.*?)\)").findall(thumbnail)[0]
			href = common.parseDOM(item, "a", ret='href')[0]
			name = common.parseDOM(item, "a", attrs = { "class": "mv_video_title[^\"']*" })[0]
			name = common.stripTags(name).encode('utf-8')
			
			nav.addDir(name, BASE_URL + href, 'PlayVideo', thumbnail, thumbnail = thumbnail, isFolder = False)
			
		nav.addDir("Next", url, 'VideoChannels', 'http://icons.iconarchive.com/icons/rafiqul-hassan/blogger/96/Arrow-Next-icon.png', {'skip':int(params['skip']) + 20})
 
	def PlayVideo(self, url):
		content = net.http_GET(url, { "Cookie": "lang_id=eng"}).content
		common.log(content)
		urlMatch = re.compile('"link":\[(.*?)\]').findall(content)[0]
		urls = urlMatch.replace('"', '').split(',')
		
		xbmc.Player().play(urls[1])
 
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
	    
