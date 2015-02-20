import xbmc
import json
from Lib.net import Net

net = Net()

def run():
	#first for php session
	content = net.http_POST('http://filmon.tv/ajax/getChannelInfo', {"channel_id": "95", "quality": "low"}, {"X-Requested-With": "XMLHttpRequest"}).content
	content = net.http_POST('http://filmon.tv/ajax/getChannelInfo', {"channel_id": "95", "quality": "low"}, {"X-Requested-With": "XMLHttpRequest"}).content

	data = json.loads(content)
	LoopPlayer().playLoop(data["streams"][0]["url"])

#xbmc.Player().play(data["streams"][0]["url"])


class LoopPlayer(xbmc.Player):
	def onPlayBackStopped(self):
		print 'opaaa finish'
		#xbmcgui.Dialog().ok('opaa', 'finish')
			
	def onPlayBackEnded(self):
		self.playLoop(self.url)
		#xbmc.executebuiltin('RunPlugin(%s?action=PlayByTime&url=%s&params=%s)' % (sys.argv[0], urllib.quote_plus(self.nextUrl), urllib.quote_plus(nav.paramsToUrl(self.params))))

	#def onPlayBackStarted( self ):
		#self.seekTime(self.seek)
   
		
	#def onPlayBackSeek(self, time, offset):
		
	
	#def onPlayBackSeekChapter(self, chapter):

	def playLoop(self, url, listitem = None):  
		self.url = url
		#playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		#playlist.clear()
		#playlist.add(url=url, listitem=listitem)
		#self.play(playlist)            
		self.play(url)
		while self.isPlaying():
			xbmc.sleep(1000)
			#common.log('playLive sleep')
			
#LoopPlayer().playLoop(data["streams"][0]["url"])
			
#LoopPlayer().playLoop('http://csm-e.tm.yospace.com/csm/live/78581126.m3u8')
#http://www.satandpcguy.com/Site/online_tv_internet_tv_4music.php
#http://filmon.tv/tv/4-music
#http://filmon.tv/ajax/getChannelInfo


#channel_id=95&quality=low
run()