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

BASE_URL = 'http://www.myvideo.ge'
RTMP_URL = ' app=dvrh264/{0} playpath={1} swfUrl=http://www.myvideo.ge/dvr/dvrAvatar7.swf?v=1.91 pageURL=http://www.myvideo.ge'

addon = xbmcaddon.Addon()
addonID = addon.getAddonInfo('id')

channelsFilePath = xbmc.translatePath("special://profile/addon_data/" + addonID + "/channels.json")

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
			
			contextMenuItems = [
				('Jump on time', 'XBMC.RunPlugin(%s?action=JumpOnTime&url=%s&params=%s)' % (sys.argv[0], urllib.quote_plus(BASE_URL + '/' + href), urllib.quote_plus(nav.paramsToUrl({'timestamp':datetime.now().strftime('%Y-%m-%d')})))),
				('Schedule', 'Container.Update(%s?action=GetTvSchedule&url=%s&params=%s)' % (sys.argv[0], urllib.quote_plus(BASE_URL + '/' + href), urllib.quote_plus(nav.paramsToUrl({'timestamp':datetime.now().strftime('%Y-%m-%d')}))))
			]
			nav.addDir(name, BASE_URL + '/' + href, 'PlayLiveTV', icon, thumbnail = icon, isFolder = False, contextMenuItems = contextMenuItems)
	
	def GetTvSchedule(self, url, params):
		playerParams = self.GetPlayerData(url)
		#timestamp = datetime.strptime(params['timestamp'], '%Y-%m-%d')
		timestamp = datetime(*(time.strptime(params['timestamp'], '%Y-%m-%d')[0:6]))
		common.log(timestamp)

		previousDate = timestamp - timedelta(days=1)

		params = common.getParameters(url)
		nav.addDir('{0:%d %B}'.format(previousDate), url, 'GetTvSchedule', '', {'timestamp':previousDate.strftime('%Y-%m-%d')})
		scheduleUrl = 'http://www.myvideo.ge/dvr_getfile.php?mode=prog&chan={0}&date={1:%Y-%m-%d}'.format(params['chan'], timestamp)
		content = net.http_GET(scheduleUrl, { "Cookie": "lang_id=eng"}).content
		
		common.log(scheduleUrl)
		
		progs = common.parseDOM(content, "prog")
		for prog in progs:
			dt = common.parseDOM(prog, 'date')
			tt = common.parseDOM(prog, 'time')[0]
			mins = common.parseDOM(prog, 'mins')[0]
			name = common.parseDOM(prog, 'name')[0]
			pss = common.parseDOM(prog, 'pass')
			timeUrl = BASE_URL + '/dvr_getfile.php?mode=file&chan={0}&date={1}'.format(params['chan'], urllib.quote_plus(tt))
			common.log(playerParams)
			nav.addDir(mins.encode('utf-8') + ' - ' + name.encode('utf-8'), timeUrl, 'PlayByTime', '', playerParams, isFolder = False)
	
	def JumpOnTime(self, url, params):
		dialog = xbmcgui.Dialog()
		d = dialog.numeric(1, 'Enter the date')
		t = dialog.numeric(2, 'Enter the time')
		
		#params = common.getParameters(url)
		playerParams = self.GetPlayerData(url)
		jumpTime = datetime(*(time.strptime(d.replace(' ', '') + ' ' + t, '%d/%m/%Y %H:%M')[0:7]))
		jumpUrl = BASE_URL + '/dvr_getfile.php?mode=file&chan={0}&date={1}'.format(playerParams['chan'], urllib.quote_plus('{0:%Y/%m/%d %H:%M:%S}'.format(jumpTime)))
		self.PlayByTime(jumpUrl, playerParams)
		#common.log(jumpTime)
	
	def PlayLiveTV(self, url): 
		playerParams = self.GetPlayerData(url)
		self.PlayTV(url, playerParams)
	
	def PlayByTime(self, url, params):		
		pDialog = xbmcgui.DialogProgress()
		ret = pDialog.create('Loading Stream', 'Please wait...')
		if ret:
			return
			
		content = net.http_GET(url, { "Cookie": "lang_id=eng"}).content
		file = common.parseDOM(content, 'file')[0]
		seek = common.parseDOM(content, 'seek')[0]
		
		pDialog.update(50)
		if pDialog.iscanceled():
			return
		
		nextUrl = ''
		endTimeString = common.parseDOM(content, 'dvr_end')[0]
		if endTimeString != 'live':
			endTime = datetime(*(time.strptime(common.parseDOM(content, 'dvr_end')[0], '%Y-%m-%d %H:%M:%S')[0:7]))
			nextUrl = BASE_URL + '/dvr_getfile.php?mode=file&chan={0}&date={1}'.format(params['chan'], urllib.quote_plus('{0:%Y/%m/%d %H:%M:%S}'.format(endTime)))
			common.log('nextUrl')
			common.log(nextUrl)
	
		listitem = xbmcgui.ListItem(params['name'])
		listitem.setInfo('video', {'Title': params['name']})
		
		pDialog.update(100)
		if pDialog.iscanceled():
			return
		
		if endTimeString != 'live':
			self.TVPlayer().playByTime(params['dvrServer'] + RTMP_URL.format(params['chan'], file), listitem, int(seek), nextUrl, params)
		else:
			xbmc.Player().play(params['dvrServer'] + RTMP_URL.format(params['chan'], file), listitem)
		
	def PlayTV(self, url, params):
		listitem = xbmcgui.ListItem(params['name'])
		listitem.setInfo('video', {'Title': params['name']})
		wid = xbmcgui.getCurrentWindowId()
		common.log(wid)
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
 
	def GetVideos(self, url,  params):
		common.log(url)
		urlWithParams = url
		if params:
			urlWithParams = url + '&per_page=' + params['skip']
		else:
			params = { 'skip': 0 }
	
		common.log(urlWithParams)
		content = net.http_GET(urlWithParams, { "Cookie": "lang_id=eng"}).content
		items = common.parseDOM(content, "div", attrs = { "class": "mv_video_item medium[^\"']*" })
		for item in items:
			thumbnail = common.parseDOM(item, "a", attrs = { "class": "vd_go_to_video[^\"']*" }, ret='style')[0]
			thumbnail = re.compile("background-image:url\((.*?)\)").findall(thumbnail)[0]
			href = common.parseDOM(item, "a", ret='href')[0]
			name = common.parseDOM(item, "a", attrs = { "class": "mv_video_title[^\"']*" })[0]
			name = common.stripTags(name).encode('utf-8')
			
			nav.addDir(name, BASE_URL + href, 'PlayVideo', thumbnail, thumbnail = thumbnail, isFolder = False)
			
		nav.addDir("Next", url, 'GetVideos', 'http://icons.iconarchive.com/icons/rafiqul-hassan/blogger/96/Arrow-Next-icon.png', {'skip':int(params['skip']) + 40})
 
	def PlayVideo(self, url, name):
		content = net.http_GET(url, { "Cookie": "lang_id=eng"}).content
		common.log(content)
		url = re.compile("'file': '(.*?)'").findall(content)[0]
		#url = urlMatch.replace('"', '') #.split(',')

		listitem = xbmcgui.ListItem(name)
		listitem.setInfo('video', {'Title': name})
		xbmc.Player().play(url, listitem)
 
 
	#Video Channels
	def AddVideoChannel(self):
		dialog = xbmcgui.Dialog()
		name = dialog.input('Enter channel name in url\nExample: http://www.myvideo.ge/[name]')
		
		if len(name) == 0:
			return
		
		url = 'http://www.myvideo.ge/' + name
		self.FetchVideoChannelData(url)
		
	def AddUser(self):
		dialog = xbmcgui.Dialog()
		id = dialog.numeric(0, 'Enter user ID')
		
		if len(id) == 0:
			return
		
		url = 'http://www.myvideo.ge/?CI=1&ci_c=userchan&user_id=' + id
		self.FetchVideoChannelData(url)
		
	def FetchVideoChannelData(self, url):
		try:
			content = net.http_GET(url).content
		except:
			xbmcgui.Dialog().ok('Error', 'Cannot find channel!')
			return
		
		nameBox = common.parseDOM(content, "div", attrs = { "class": "mv_user_channel_name[^\"']*" })
		if len(nameBox) == 0:
			xbmcgui.Dialog().ok('Error', 'Cannot add channel!')
			return
			
		name = common.stripTags(common.parseDOM(nameBox, "a")[0])		
		
		avatarBox = common.parseDOM(content, "div", attrs = { "class": "mv_user_header_avatar[^\"']*" })
		if len(avatarBox) == 0:
			xbmcgui.Dialog().ok('Error', 'Cannot add channel!')
			return
		avatar = common.parseDOM(avatarBox, "img", ret="src")[0]

		if not xbmcgui.Dialog().yesno('Confirm Channel', 'Confirm to add channel: ', name):
			return
		
		data = []
		if os.path.exists(channelsFilePath):
			jsonData = open(channelsFilePath)
			data = json.load(jsonData)
		data.append({
			"name": name,
			"url": url + '&latest=true',
			"thumbnail": avatar
		})
		with open(channelsFilePath, 'w') as outfile:
			json.dump(data, outfile)
	
	def LoadVideoChannels(self):
		if not os.path.exists(channelsFilePath):
			return
		
		jsonData = open(channelsFilePath)
		data = json.load(jsonData)
		for user in data:
			contextMenuItems = [('Remove', 'XBMC.RunPlugin(%s?action=RemoveVideoChannels&url=%s)' % (sys.argv[0], urllib.quote_plus(user["url"])))]
			nav.addDir(user["name"].encode('utf8'), user["url"], 'GetVideos', user["thumbnail"], thumbnail = user["thumbnail"], contextMenuItems = contextMenuItems)
	
	def RemoveVideoChannels(self, url):
		jsonData = open(channelsFilePath)
		data = json.load(jsonData)
		user = filter(lambda user: user['url'] == url, data)[0]
		dialog = xbmcgui.Dialog()
		if not dialog.yesno('Confirm Remove', 'Are you sure you want to remove \'' + user['name'] + '\'?'):
			return
		data.remove(user)
		with open(channelsFilePath, 'w') as outfile:
			json.dump(data, outfile)

 

	class TVPlayer(xbmc.Player):
		def onPlayBackStopped(self):
			print 'opaaa finish'
			#xbmcgui.Dialog().ok('opaa', 'finish')
			    
		def onPlayBackEnded(self):
			common.log('end')
			xbmc.executebuiltin('RunPlugin(%s?action=PlayByTime&url=%s&params=%s)' % (sys.argv[0], urllib.quote_plus(self.nextUrl), urllib.quote_plus(nav.paramsToUrl(self.params))))
    
		def onPlayBackStarted( self ):
			self.seekTime(self.seek)
	   
			
		#def onPlayBackSeek(self, time, offset):
			
		
		def onPlayBackSeekChapter(self, chapter):
			common.log('onPlayBackSeekChapter')
			common.log(chapter)

		def playLive(self, url, listitem):  
			playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
			playlist.clear()
			playlist.add(url=url, listitem=listitem)
			self.play(playlist)            
			while self.isPlaying():
				xbmc.sleep(1000)
				common.log('playLive sleep')
			
		def playByTime(self, url, listitem, seek, nextUrl, params):
			self.seek = seek
			self.nextUrl = nextUrl
			self.params = params
			common.log('nextUrl', nextUrl)
			self.play(url)
			while self.isPlaying():
				xbmc.sleep(1000)
