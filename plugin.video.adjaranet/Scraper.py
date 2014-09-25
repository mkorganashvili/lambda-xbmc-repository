import urllib,urllib2,re,datetime,locale,time,Navigation,string,json
from datetime import datetime, date, timedelta
from Lib.net import Net
import CommonFunctions
import xbmcplugin, xbmcgui, xbmc, xbmcaddon
import os, sys

nav = Navigation.Navigation()
net = Net()
addon = xbmcaddon.Addon()
addonID = addon.getAddonInfo('id')

common = CommonFunctions
common.plugin = "plugin.video.imovies"
common.dbg = True
common.dbglevel = 5

moviesFilePath = xbmc.translatePath("special://profile/addon_data/" + addonID + "/movies.json")
tvshowFilePath = xbmc.translatePath("special://profile/addon_data/" + addonID + "/tvshows.json")
_preferredLanguage = addon.getSetting('preferredLanguage')
_preferredVideoQuality = addon.getSetting('preferredVideoQuality')

class Scraper:
    
	def GetTvShows(self, url):
		content = net.http_GET(url).content
		data = json.loads(content)
		
		for row in data["data"]:
			nav.addDir(row["title_en"], row["link"], 'TVShow', row["poster"], {"title": row["title_en"].encode('utf8')})
	
	def GetSeasons(self, url, params):
		urlMatcher = re.compile('http://adjaranet.com/Movie/main\\?id=([0-9]+)&serie=([0-9]+)', re.DOTALL).findall(url)
		movieId = urlMatcher[0][0]
		season = 1
		while season > 0:
			seasonsUrl = 'http://adjaranet.com/req/series/req.php?reqId=series_list_new&id=' + movieId + '&season=' + str(season)
			
			req = urllib2.Request(seasonsUrl)
			req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
			u = urllib2.urlopen(req)
			result = json.load(u)
			u.close()
			      
			if len(result) > 0:
				title = 'Season ' + str(season)
				nav.addDir(title, seasonsUrl, 'GetEpisodes', 'http://static.adjaranet.com/moviecontent/' + str(movieId) + '/covers/214x321-' + str(movieId) + '.jpg', {"title": params["title"]})
				season = season + 1
			else:
				season = 0
	
	def GetEpisodes(self, url, url_params, params):
		content = net.http_GET(url).content
		result = json.loads(content)
			
		url = 'http://adjaranet.com/test/newPlayer.php?id=' + url_params['id']
		net.set_user_agent('Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36')
		try:
			content = net.http_GET(url, {'referer': url}).content
		except:
			dialog.ok('Error', 'Cannot find movie!')
			return
		moviepath = re.search('var moviepath = \'(.*?)\'', content).group(1)
	
		for row in result:
			info = {
				"id": url_params['id'],
				"title": row['name'].encode('utf8'),
				"episode": row['episode'].encode('utf8'),
				"season": url_params["season"].encode('utf8'),
				"tvshowtitle": params["title"].encode('utf8'),
				"moviepath": moviepath
			}
		
			contextMenuItems = [
				('Play As ...', 'XBMC.RunPlugin(%s?action=PlayTVShowAs&url=%s&params=%s)' % (sys.argv[0], urllib.quote_plus('1'), urllib.quote_plus(nav.paramsToUrl(info)))),
			]
			nav.addDir(row['name'].encode('utf8'), '1', 'PlayTVShow', '', info, isFolder=False, contextMenuItems=contextMenuItems)

	def PlayTvShow(self, url, params):
		progress = xbmcgui.DialogProgress()
		progress.create('Adjaranet', 'Opening data...')

		req_url = "http://adjaranet.com/req/series/req.php?reqId=getLangAndHd&id={0}&serie_id={1}&season={2}".format(params['id'], params['episode'], params['season'])
		content = net.http_GET(req_url).content
		data = json.loads(content)

		languages = data[0]['lang'].split(",")
		if _preferredLanguage in languages:
			lang = _preferredLanguage
		else:
			lang = languages[0]
		qualities = data[0]['quality'].split(",")
		
		videuUrl = params["moviepath"] + '{0}_{1}_{2}_{3}.mp4'.format(params['season'].rjust(2, '0'), params['episode'].rjust(2, '0'), lang, qualities[-1])
		
		progress.close()
		
		listitem = xbmcgui.ListItem(params['title'])	
		listitem.setInfo( type= "Video", 
                                infoLabels =
                                        {
                                             "title": params['title'],
                                             "episode": params['episode'],
                                             "season": params["season"],
                                             "tvshowtitle": params["tvshowtitle"]
                                        } )		
		xbmc.Player().play(videuUrl, listitem)
		
	def PlayTvShowAs(self, url, params):
		progress = xbmcgui.DialogProgress()
		progress.create('Adjaranet', 'Opening data...')

		req_url = "http://adjaranet.com/req/series/req.php?reqId=getLangAndHd&id={0}&serie_id={1}&season={2}".format(params['id'], params['episode'], params['season'])
		content = net.http_GET(req_url).content
		data = json.loads(content)

		languages = data[0]['lang'].split(",")
		qualities = data[0]['quality'].split(",")
		
		progress.close()
		
		dialog = xbmcgui.Dialog()
		lang = dialog.select('Choose Language', languages)
		if lang < 0: lang = 0
		
		quality = dialog.select('Select Quality', qualities)
		
		videuUrl = params["moviepath"] + '{0}_{1}_{2}_{3}.mp4'.format(params['season'].rjust(2, '0'), params['episode'].rjust(2, '0'), languages[lang], qualities[quality])

		
		listitem = xbmcgui.ListItem(params['title'])	
		listitem.setInfo( type= "Video", 
                                infoLabels =
                                        {
                                             "title": params['title'],
                                             "episode": params['episode'],
                                             "season": params["season"],
                                             "tvshowtitle": params["tvshowtitle"]
                                        } )		
		xbmc.Player().play(videuUrl, listitem)
		

	def GetTvShowInfo(self, id):
		net.set_user_agent('Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36')
		
		url = 'http://adjaranet.com/Movie/main?id=' + id + '&serie=1'
		content = net.http_GET(url).content
		
		infoDiv = common.parseDOM(content, 'div', attrs = {'id': 'movie-info-inner'})
		name = common.parseDOM(infoDiv, 'h1')[0]
		
		posterDiv = common.parseDOM(content, 'div', attrs = {'id': 'movie-poster'})
		poster = common.parseDOM(posterDiv, 'img', ret='src')[0]

		return {
			'name': name,
			'poster': poster,
			'url': url
		}
		
	def AddTvShow(self):
		dialog = xbmcgui.Dialog()
		id = dialog.numeric(0, 'Enter movie ID')
		
		if len(id) == 0:
			return
		
		movieInfo = self.GetTvShowInfo(id)
		
		data = []
		if os.path.exists(tvshowFilePath):
			jsonData = open(tvshowFilePath)
			data = json.load(jsonData)
		data.append({
			"name": movieInfo['name'],
			"poster": movieInfo['poster'],
			"url": movieInfo['url']
		})
		with open(tvshowFilePath, 'w') as outfile:
			json.dump(data, outfile)

	def LoadTvShows(self):
		if not os.path.exists(tvshowFilePath):
			return
		
		jsonData = open(tvshowFilePath)
		data = json.load(jsonData)
		for item in data:
			contextMenuItems = [
				('Remove', 'XBMC.RunPlugin(%s?action=RemoveTvShow&url=%s)' % (sys.argv[0], urllib.quote_plus(item["url"])))
			]
			nav.addDir(item["name"].encode('utf8'), item["url"], 'TVShow', item["poster"], {"title": item["name"].encode('utf8')}, contextMenuItems = contextMenuItems)
				
	def RemoveTvShow(self, url):
		jsonData = open(tvshowFilePath)
		data = json.load(jsonData)
		item = filter(lambda item: item['url'] == url, data)[0]
		dialog = xbmcgui.Dialog()
		if not dialog.yesno('Confirm Remove', 'Are you sure you want to remove \'' + item['name'] + '\'?'):
			return
		data.remove(item)
		with open(tvshowFilePath, 'w') as outfile:
			json.dump(data, outfile)		
		
		
	def GetMovie(self, id):
		url = 'http://adjaranet.com/test/newPlayer.php?id=' + id

		net.set_user_agent('Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36')
		try:
			content = net.http_GET(url, {'referer': url}).content
		except:
			dialog.ok('Error', 'Cannot find movie!')
			return
		
		common.log(content)
		
		movie_id = re.search('var movie_id = \'(.+?)\'', content).group(1)
		moviepath = re.search('var moviepath = \'(.*?)\'', content).group(1)
		languages = sorted(json.loads(re.search('var javascript_array = (\[.*?\]);', content).group(1)))
		maxres = re.search('var maxres = \'(.*?)\'', content).group(1)
		
		videoUrl = moviepath + languages[0] + '_' + maxres + '.mp4'
		
		common.log(videoUrl)
		
		url = 'http://adjaranet.com/Movie/main?id=' + id
		content = net.http_GET(url).content
		
		infoDiv = common.parseDOM(content, 'div', attrs = {'id': 'movie-info-inner'})
		name = common.parseDOM(infoDiv, 'h1')[0]
		
		posterDiv = common.parseDOM(content, 'div', attrs = {'id': 'movie-poster'})
		poster = common.parseDOM(posterDiv, 'img', ret='src')[0]

		return {
			'name': name,
			'videoUrl': videoUrl,
			'poster': poster,
			'languages': languages,
			'maxres': maxres,
			'moviepath': moviepath,
			'url': url
		}
		
	def AddMovie(self):
		dialog = xbmcgui.Dialog()
		id = dialog.numeric(0, 'Enter movie ID')
		
		if len(id) == 0:
			return
		
		movieInfo = self.GetMovie(id)
		
		data = []
		if os.path.exists(moviesFilePath):
			jsonData = open(moviesFilePath)
			data = json.load(jsonData)
		data.append({
			"name": movieInfo['name'],
			"videoUrl": movieInfo['videoUrl'],
			"poster": movieInfo['poster'],
			"url": movieInfo['url']
		})
		with open(moviesFilePath, 'w') as outfile:
			json.dump(data, outfile)
		
		
	def LoadMovies(self):
		if not os.path.exists(moviesFilePath):
			return
		
		jsonData = open(moviesFilePath)
		data = json.load(jsonData)
		for item in data:
			contextMenuItems = [
				('Play As ...', 'XBMC.RunPlugin(%s?action=PlayMovieAs&url=%s)' % (sys.argv[0], urllib.quote_plus(item["url"]))),
				('Remove', 'XBMC.RunPlugin(%s?action=RemoveMovie&url=%s)' % (sys.argv[0], urllib.quote_plus(item["videoUrl"])))
			]
			nav.addLink(item["name"].encode('utf8'), item["videoUrl"], item["poster"], item["poster"], contextMenuItems = contextMenuItems)
				
	
	def RemoveMovie(self, url):
		jsonData = open(moviesFilePath)
		data = json.load(jsonData)
		item = filter(lambda item: item['videoUrl'] == url, data)[0]
		dialog = xbmcgui.Dialog()
		if not dialog.yesno('Confirm Remove', 'Are you sure you want to remove \'' + item['name'] + '\'?'):
			return
		data.remove(item)
		with open(moviesFilePath, 'w') as outfile:
			json.dump(data, outfile)		
		
	def GetCollections(self, url):
		content = net.http_GET(url).content
		content = unicode(content, errors='ignore')
		items = common.parseDOM(content, 'div', attrs = {'class': "collections-front-item[^\"']*"})
		
		for item in items:
			titleDiv = common.parseDOM(item, 'div', attrs = {'class': "collections-title"})
			title = common.parseDOM(titleDiv, 'h2')[0].encode('utf8')
			thumbDiv = common.parseDOM(item, 'div', attrs = {'class': "collections-thumb"})
			thumbnail = common.parseDOM(thumbDiv, 'img', ret='src')[0]
			href = common.parseDOM(item, 'a', ret='href')[0]
			
			nav.addDir(title, href, 'GetMovies', thumbnail)
			
	def GetMovies(self, url):
		content = net.http_GET(url).content
		items = common.parseDOM(content, 'div', attrs = {'class': "movie-element"})
				
		for item in items:
			title = common.parseDOM(item, 'em', attrs = {'class': "title-en"})[0]
			thumbnail = common.parseDOM(item, 'img', ret='src')[0]
			href = common.parseDOM(item, 'a', ret='href')[0]

			contextMenuItems = [
				('Play As ...', 'XBMC.RunPlugin(%s?action=PlayMovieAs&url=%s)' % (sys.argv[0], urllib.quote_plus(href)))
			]
			nav.addDir(title.encode('utf8'), href, 'PlayMovie', thumbnail, isFolder=False, contextMenuItems = contextMenuItems)
			

	def PlayMovie(self, url):
		progress = xbmcgui.DialogProgress()
		progress.create('Adjaranet', 'Opening data...')
		urlMatcher = re.compile('http://adjaranet.com/Movie/main\?id=([0-9]+)', re.DOTALL).findall(url)
		common.log(urlMatcher)
		movieInfo = self.GetMovie(urlMatcher[0])
		progress.close()
		
		listitem = xbmcgui.ListItem(movieInfo['name'], '', '', movieInfo['poster'])		
		xbmc.Player().play(movieInfo['videoUrl'], listitem)
		
	def PlayMovieAs(self, url):
		progress = xbmcgui.DialogProgress()
		progress.create('Adjaranet', 'Opening data...')
		urlMatcher = re.compile('http://adjaranet.com/Movie/main\?id=([0-9]+)', re.DOTALL).findall(url)
		movieInfo = self.GetMovie(urlMatcher[0])

		progress.close()
		dialog = xbmcgui.Dialog()
		#dialog.select('Select Quality', ['Playlist #1', 'Playlist #2', 'Playlist #3'])
		lang = dialog.select('Choose Language', movieInfo['languages'])
		if lang < 0: lang = 0
		videoUrl = movieInfo['moviepath'] + movieInfo['languages'][lang] + '_' + movieInfo['maxres'] + '.mp4'
		
		common.log(lang)
		
		listitem = xbmcgui.ListItem(movieInfo['name'], '', '', movieInfo['poster'])		
		xbmc.Player().play(videoUrl, listitem)
		
		