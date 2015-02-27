import urllib,urllib2,re,locale,string,ast, sys, os, time
import xbmcplugin, xbmcgui, xbmc, xbmcaddon
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

BASE_URL = 'http://www.rustavi2.com'
RTMP_URL = ' app=dvrh264/{0} playpath={1} swfUrl=http://www.myvideo.ge/dvr/dvrAvatar7.swf?v=1.91 pageURL=http://www.myvideo.ge'

addon = xbmcaddon.Addon()
addonID = addon.getAddonInfo('id')

channelsFilePath = xbmc.translatePath("special://profile/addon_data/" + addonID + "/channels.json")

class Scraper:
    
	def GetShows(self):
		content = net.http_GET(BASE_URL + '/ka/shows').content
		items = common.parseDOM(content, "div", attrs = { "class": "bl" })
		for item in items:
			icon = common.parseDOM(item, "div", attrs = { "class": "ph" }, ret='style')[0]
			href = common.parseDOM(item, "a", attrs = { "class": "lnk link" }, ret='href')[0]
			name = common.parseDOM(item, "a", attrs = { "class": "lnk link" })[0]
			
			icon = BASE_URL + re.compile("background-image:url\((.*?)\)").findall(icon)[0].replace('..', '')
			name = common.stripTags(name).encode('utf-8')
			id = re.compile("([0-9]+).jpg").findall(icon)[0]

			nav.addDir(name, id, 'Show', icon, thumbnail = icon)
	
	def GetVideos(self, id):
		url = "http://rustavi2.com/includes/shows_sub_ajax.php?l=ka&id={0}&pos={1}"
		url = url.format(id, 0)
		content = net.http_GET(url).content
		
		items = common.parseDOM(content, "div", attrs = { "class": "ireport_bl[^\"']*" })
		
		for item in items:
			icon = common.parseDOM(item, "div", attrs = { "class": "ph" }, ret='style')[0]
			href = common.parseDOM(item, "a", attrs = { "class": "link[^\"']*" }, ret='href')[0]
			name = common.parseDOM(item, "a", attrs = { "class": "link[^\"']*" })[0]

			icon = BASE_URL + re.compile("background-image:url\((.*?)\)").findall(icon)[0].replace('..', '')
			name = common.stripTags(name).encode('utf-8')
			id = re.compile("([0-9]+).jpg").findall(icon)[0]
			
			nav.addDir(name, id, 'PlayVideo', icon, thumbnail = icon, isFolder = False)
	
	def PlayVideo(self, id):
		url = "http://rustavi2.com/includes/player_video.php?id=" + id		
		content = net.http_GET(url).content
		src = common.parseDOM(content, "iframe", ret = "src")[0]	
		#common.log(urllib.urlencode(src))
		content = net.http_GET(src.replace(' ', '%20')).content
		common.log(content)

		#js = common.extractJS(content, function='setup', values=True, evaluate=True)[0]
		m = re.findall('file: "(.+?)"', content)
		
		xbmc.Player().play(m[0].replace(' ', '%20'))