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

class Scraper:
    
	def AddTvShows(self, url):
		content = net.http_GET(url).content
		data = json.loads(content)
		
		for row in data["data"]:
			nav.addDir(row["title_en"], row["link"], 'TVShow', row["poster"], {"title": row["title_en"].encode('utf8')})
	
	def AddTvSeasons(self, url, params):
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
				nav.addDir(title, seasonsUrl, 'GetEpisodes', 'http://static.adjaranet.com/moviecontent/' + str(movieId) + '/covers/214x321-' + str(movieId) + '.jpg', {"title": params["title"]})
				season = season + 1
			else:
				season = 0
	
	def GetEpisodes(self, url, url_params, params):
		req = urllib2.Request(url)
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
		u = urllib2.urlopen(req)
		result = json.load(u)
		u.close()
			
		for row in result:
			url = 'rtmp://edge2.vod.adjaranet.com/vod playpath=mp4:{0}/{0}_{1}_{2}_{3}_800'.format(url_params['id'], url_params['season'].rjust(2, '0'), row['episode'].rjust(2, '0'), 'English')
			li = xbmcgui.ListItem(row['name'], iconImage = '', thumbnailImage = '')
			li.setInfo( type= "Video", 
                                infoLabels =
                                        {
                                             "title": row['name'],
                                             "episode": row['episode'],
                                             "season": url_params["season"],
                                             "tvshowtitle": params["title"]
                                        } )
			url_without_language = 'rtmp://edge2.vod.adjaranet.com/vod playpath=mp4:{0}/{0}_{1}_{2}_{3}_800'.format(url_params['id'], url_params['season'].rjust(2, '0'), row['episode'].rjust(2, '0'), '{0}')
                        li.addContextMenuItems([('Choose Language', 'XBMC.RunPlugin(%s?action=ChooseLanguage&id=%s&url=%s)' % (sys.argv[0], row['id'], urllib.quote_plus(url_without_language)))]) 
			xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = url, listitem = li)

	def GetLanguages(self, id):
		req_url = "http://adjaranet.com/req/series/req.php?id={0}&reqId=info".format(id)
		content = net.http_GET(req_url).content
		
		ge = common.parseDOM(content, "video", ret = "ge")
		ru = common.parseDOM(content, "video", ret = "ru")
		en = common.parseDOM(content, "video", ret = "en")
		
		languages = []
		if (common.makeAscii(ge) == "1"):
			languages.append("Georgian")
		if (common.makeAscii(ru) == "1"):
			languages.append("Russian")
		if (common.makeAscii(en) == "1"):
			languages.append("English")
			
		return languages
		
	def AddMovie(self):
		dialog = xbmcgui.Dialog()
		id = dialog.numeric(0, 'Enter movie ID')
		
		if len(id) == 0:
			return
		
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
		
		common.log(poster)
		
		common.log(name)
		
		data = []
		if os.path.exists(moviesFilePath):
			jsonData = open(moviesFilePath)
			data = json.load(jsonData)
		data.append({
			"name": name,
			"url": videoUrl,
			"poster": poster
		})
		with open(moviesFilePath, 'w') as outfile:
			json.dump(data, outfile)
		
		
	def LoadMovies(self):
		if not os.path.exists(moviesFilePath):
			return
		
		jsonData = open(moviesFilePath)
		data = json.load(jsonData)
		for item in data:
			contextMenuItems = [('Remove', 'XBMC.RunPlugin(%s?action=RemoveMovie&url=%s)' % (sys.argv[0], urllib.quote_plus(item["url"])))]
			nav.addLink(item["name"].encode('utf8'), item["url"], item["poster"], item["poster"], contextMenuItems = contextMenuItems)
				
	
	def RemoveMovie(self, url):
		jsonData = open(moviesFilePath)
		data = json.load(jsonData)
		item = filter(lambda item: item['url'] == url, data)[0]
		dialog = xbmcgui.Dialog()
		if not dialog.yesno('Confirm Remove', 'Are you sure you want to remove \'' + item['name'] + '\'?'):
			return
		data.remove(item)
		with open(moviesFilePath, 'w') as outfile:
			json.dump(data, outfile)		
		
		