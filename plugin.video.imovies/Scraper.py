import urllib,urllib2,re
import xbmc, xbmcplugin, xbmcgui, xbmcaddon
import sys, os, datetime, locale, time, string, HTMLParser, json, uuid
from datetime import datetime, date, timedelta
from xml.dom import minidom
from Lib.net import Net
import CommonFunctions
from urlparse import urlparse

import Navigation

addon = xbmcaddon.Addon()
addonID = addon.getAddonInfo('id')

usersFilePath = xbmc.translatePath("special://profile/addon_data/" + addonID + "/users.json")
listsFilePath = xbmc.translatePath("special://profile/addon_data/" + addonID + "/lists.json")
moviesFilePath = xbmc.translatePath("special://profile/addon_data/" + addonID + "/movies.json")
_preferredLanguage = addon.getSetting('preferredLanguage')

common = CommonFunctions
common.plugin = 'imovies.ge'
common.dbg = True
common.dbglevel = 2
nav = Navigation.Navigation()
net = Net()

    
class Scraper:
    
	def GetSeasons(self, url):
		urlMatcher = re.compile('http://www.imovies.ge/movies/([0-9]+)', re.DOTALL).findall(url)
		movieId = urlMatcher[0]
		
                req = urllib2.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                response = urllib2.urlopen(req)
                content = response.read()
                response.close()
                match = re.compile('<li><a data-group="(.+?)" href="#episodes-list-season-[0-9]+" class=".+?">([0-9]+)</a></li>').findall(content)
                title = common.parseDOM(content, "h2", attrs = { "class": "[^\"']*film_title_eng[^\"']*" })[0]
                
                for name, season in match:
                        params = {
                                "title": title,
                                "season": season
                        }
                        nav.addDir('Season %s' % (season), 'http://www.imovies.ge/get_playlist_jwQ.php?movie_id=%s&activeseria=0&group=sezoni %s' % (movieId, season), 'GetEpisodes', '', params)
				
                if len(match) == 0:
                        params = {
                                "title": title,
                                "season": 1
                        }
                        nav.addDir('Season %s' % (1), 'http://www.imovies.ge/get_playlist_jwQ.php?movie_id=%s&activeseria=0&group=sezoni %s' % (movieId, 1), 'GetEpisodes', '', params)
	
	def GetEpisodes(self, url, params):
		content = net.http_GET(url).content
		itemList = common.parseDOM(content, "item")
			
		for item in itemList:
			name = common.stripTags(common.replaceHTMLCodes(common.parseDOM(item, "description")[0]))
			url = common.parseDOM(item, "jwplayer:source", ret="file")[0]
			path = urlparse(url).path
			langData = sorted(common.parseDOM(item, "jwplayer:source", ret="lang")[0].split(','))
			episode = re.compile('([0-9]+)').findall(common.parseDOM(item, "title")[0])[0]
			thumbnail = common.parseDOM(item, "jwplayer:image")[0]
			
			if not name:
				name = "Episode " + str(episode)
			
			li = xbmcgui.ListItem(name, iconImage = thumbnail, thumbnailImage = thumbnail)
			li.setInfo( type= "Video", 
                                infoLabels =
                                        {
                                             "title": name,
                                             "episode": episode,
                                             "season": params["season"],
                                             "tvshowtitle": params["title"]
                                        } )
			
			langIndex = 0
			contextMenuItems = []
			for lang in langData:
				urlData = self.GetEpisodeUrl(lang, path)
				if urlData['lang'] == _preferredLanguage:
					langIndex = langData.index(lang)
				contextMenuItems.append((urlData['lang'], 'PlayMedia("' + urlData['url'] + '")'))
			
			contextMenuItems.pop(langIndex)
			li.addContextMenuItems(contextMenuItems)			
			xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = self.GetEpisodeUrl(langData[langIndex], path)['url'], listitem = li)

	def GetEpisodeUrl(self, langData, path):
		reLang = re.compile('(.*?)\:(.*?)\:')
                langMatcher = reLang.findall(langData)[0]
                lang = langMatcher[0]
                ip = langMatcher[1]
                
                return { 'url': 'http://' + ip + path + lang, 'lang': lang}
                
	def AddUser(self):
		dialog = xbmcgui.Dialog()
		id = dialog.numeric(0, 'Enter user ID')
		
		if len(id) == 0:
			return
		
		url = 'http://www.imovies.ge/users/' + id
		try:
			content = net.http_GET(url).content
		except:
			dialog.ok('Error', 'Cannot find user!')
			return
		
		userBox = common.parseDOM(content, "div", attrs = { "class": "userbox" })
		if len(userBox) == 0:
			return
		name = common.parseDOM(userBox, "div", attrs = { "class": "firstname" })[0] + ' ' + common.parseDOM(userBox, "div", attrs = { "class": "lastname" })[0]
		avatar = common.parseDOM(userBox, "img", ret="src")[0]

		if not dialog.yesno('Confirm User', 'Confirm to add user: ', name):
			return
		
		usersData = []
		if os.path.exists(usersFilePath):
			jsonData = open(usersFilePath)
			usersData = json.load(jsonData)
		usersData.append({
			"name": name,
			"url": url + '/watchlist',
			"thumbnail": avatar
		})
		with open(usersFilePath, 'w') as outfile:
			json.dump(usersData, outfile)
	
	def LoadUsers(self):
		if not os.path.exists(usersFilePath):
			return
		
		jsonData = open(usersFilePath)
		usersData = json.load(jsonData)
		for user in usersData:
			contextMenuItems = [('Remove', 'XBMC.RunPlugin(%s?action=RemoveUser&url=%s)' % (sys.argv[0], urllib.quote_plus(user["url"])))]
			nav.addDir(user["name"], user["url"], 'ScrapPage', user["thumbnail"], thumbnail = user["thumbnail"], contextMenuItems = contextMenuItems)
	
	def RemoveUser(self, url):
		jsonData = open(usersFilePath)
		usersData = json.load(jsonData)
		user = filter(lambda user: user['url'] == url, usersData)[0]
		dialog = xbmcgui.Dialog()
		if not dialog.yesno('Confirm Remove', 'Are you sure you want to remove \'' + user['name'] + '\'?'):
			return
		usersData.remove(user)
		with open(usersFilePath, 'w') as outfile:
			json.dump(usersData, outfile)

	def AddList(self):
		dialog = xbmcgui.Dialog()
		id = dialog.numeric(0, 'Enter list ID')
		
		if len(id) == 0:
			return
		
		url = 'http://www.imovies.ge/lists/' + id
		try:
			content = net.http_GET(url).content
		except:
			dialog.ok('Error', 'Cannot find user!')
			return
		
		contentDiv = common.parseDOM(content, "div", attrs = { "class": "content" })
		if len(contentDiv) == 0:
			return
		name = common.parseDOM(contentDiv, "h1")[0]

		if not dialog.yesno('Confirm List', 'Confirm to add list: ', name):
			return
		
		listsData = []
		if os.path.exists(listsFilePath):
			jsonData = open(listsFilePath)
			listsData = json.load(jsonData)
		listsData.append({
			"name": name,
			"url": url
		})
		with open(listsFilePath, 'w') as outfile:
			json.dump(listsData, outfile)
	
	def LoadLists(self):
		if not os.path.exists(listsFilePath):
			return
		
		jsonData = open(listsFilePath)
		listsData = json.load(jsonData)
		for list in listsData:
			contextMenuItems = [('Remove', 'XBMC.RunPlugin(%s?action=RemoveList&url=%s)' % (sys.argv[0], urllib.quote_plus(list["url"])))]
			nav.addDir(list["name"].encode('utf8'), list["url"], 'ScrapListPage', '', contextMenuItems = contextMenuItems)
	
	def RemoveList(self, url):
		jsonData = open(listsFilePath)
		listsData = json.load(jsonData)
		list = filter(lambda list: list['url'] == url, listsData)[0]
		dialog = xbmcgui.Dialog()
		if not dialog.yesno('Confirm Remove', 'Are you sure you want to remove \'' + list['name'] + '\'?'):
			return
		listsData.remove(list)
		with open(listsFilePath, 'w') as outfile:
			json.dump(listsData, outfile)

	def AddTvShow(self):
		dialog = xbmcgui.Dialog()
		id = dialog.numeric(0, 'Enter TV Show ID')
		
		if len(id) == 0:
			return
		
		url = 'http://www.imovies.ge/movies/' + id
		try:
			content = net.http_GET(url).content
		except:
			dialog.ok('Error', 'Cannot find tv show!')
			return
		
		contentDiv = common.parseDOM(content, "div", attrs = { "id": "infodiv" })
		if len(contentDiv) == 0:
			return
			
		name = common.parseDOM(contentDiv, "h2")[0]

		if not dialog.yesno('Confirm TV Show', 'Confirm to add TV Show: ', name):
			return

		thumbnailDiv = common.parseDOM(content, "div", attrs = { "class": "distributor" })
		thumbnail = common.parseDOM(thumbnailDiv, "img", ret="src")[0]
			
		movieData = []
		if os.path.exists(moviesFilePath):
			jsonData = open(moviesFilePath)
			movieData = json.load(jsonData)
		movieData.append({
			"name": name,
			"thumbnail": 'http://www.imovies.ge' + thumbnail,
			"url": url
		})
		with open(moviesFilePath, 'w') as outfile:
			json.dump(movieData, outfile)
	
	def LoadTvShows(self):
		if not os.path.exists(moviesFilePath):
			return
		
		jsonData = open(moviesFilePath)
		movieData = json.load(jsonData)
		for movie in movieData:
			contextMenuItems = [('Remove', 'XBMC.RunPlugin(%s?action=RemoveTvShow&url=%s)' % (sys.argv[0], urllib.quote_plus(movie["url"])))]
			nav.addDir(movie["name"].encode('utf8'), movie["url"], 'TVShow', movie['thumbnail'], contextMenuItems = contextMenuItems)
	
	def RemoveTvShow(self, url):
		jsonData = open(moviesFilePath)
		movieData = json.load(jsonData)
		movie = filter(lambda movie: movie['url'] == url, movieData)[0]
		dialog = xbmcgui.Dialog()
		if not dialog.yesno('Confirm Remove', 'Are you sure you want to remove \'' + movie['name'] + '\'?'):
			return
		movieData.remove(movie)
		with open(moviesFilePath, 'w') as outfile:
			json.dump(movieData, outfile)
	
	def GetTvShows(self, url):
		content = net.http_GET(url).content
		
		ajaxContent = re.compile("\$j\('#films'\).html\(\"(.*?)\"\)", re.DOTALL).findall(content)
		if ajaxContent:
			content = ajaxContent[0].decode("string_escape").replace('\/', '/')
		
		items = common.parseDOM(content, "div", attrs = { "class": "item[^\"']*" })
		
		for item in items:
			title_ge = re.sub('<[^<]+?>', '', common.parseDOM(item, "h", attrs = { "class": "film_title[^\"']*" })[0])
			title_en = re.sub('<[^<]+?>', '', common.parseDOM(item, "h", attrs = { "class": "film_title[^\"']*" })[1])
			movieUrl = common.parseDOM(item, "a", ret="href")[0]
			thumbnail = common.parseDOM(item, "img", ret="src")[0]
			
			movieId = common.parseDOM(item, "a", attrs = { "class": "wishlist[^\"']*" }, ret="film_id")[0]
			movieInfo = net.http_GET('http://www.imovies.ge/get_playlist_temp.php?activeseria=0&group=&language=ENG&movie_id=' + movieId).content
			movieItems = common.parseDOM(movieInfo, "item")
			if movieItems:
				fileUrl = common.parseDOM(movieInfo, "implayer:hd.file")[0]
				nav.addLink(title_en, fileUrl, 'movie', thumbnail)
			else:
				nav.addDir(title_en, 'http://www.imovies.ge' + movieUrl, 'TVShow', '', thumbnail = thumbnail)

    
	def ScrapListPage(self, url):
		content = net.http_GET(url).content
		
		items = common.parseDOM(content, "li", attrs = { "class": "clearfix" })
		
		for item in items:
			filmTitle = common.parseDOM(item, "div", attrs = { "class": "film_title" })
			title = common.stripTags(filmTitle[0])
			movieUrl = common.parseDOM(item, "a", ret="href")[0]
			thumbnail = common.parseDOM(item, "img", ret="src")[0]
			
			movieId = common.parseDOM(item, "a", ret="href")[0]
			movieInfo = net.http_GET('http://www.imovies.ge/get_playlist_temp.php?activeseria=0&group=&language=ENG&movie_id=' + movieId).content
			movieItems = common.parseDOM(movieInfo, "item")
			if movieItems:
				fileUrl = common.parseDOM(movieInfo, "implayer:hd.file")[0]
				nav.addLink(title.encode('utf8'), fileUrl, 'movie', thumbnail)
			else:
				nav.addDir(title.encode('utf8'), 'http://www.imovies.ge' + movieUrl, 'TVShow', '', thumbnail = thumbnail)

    
