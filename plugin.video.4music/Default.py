import xbmc

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
			
			
LoopPlayer().playLoop('http://csm-e.tm.yospace.com/csm/live/78581126.m3u8')