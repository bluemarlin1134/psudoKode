import time
import youtube_dl
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os, json

chrome_options = Options()

chrome_options.headless = True

driver = webdriver.Chrome()

def getrecondmendations(id):

	driver.get(f"https://www.youtube.com/watch?v={id}")
	time.sleep(5)
	links = []
	for a in driver.find_elements_by_xpath('.//a'):
		if "watch?v=" in str(a.get_attribute('href')):
			links.append(str(a.get_attribute('href')))

	for l in links:
		if "start_radio" in l:
			inde =links.index(l)
			del links[inde]
			print(inde)

	for l in links:
		if "start_radio" in l:
			inde =links.index(l)
			del links[inde]
			print(inde)

	links = list(set(links)) 
	driver.quit()

	info = []
	for l in links:
		y = youtube_dl.YoutubeDL({'outtmpl': '%(id)s.%(ext)s'})
		result = y.extract_info(l, download=False)

		if 'entries' in result:
			pass
		else:
			video = result
		info.append({'title':video['title'], 'id':video['id'], 'thumbnails':video['thumbnails'], 'viewCount':video['view_count'], 'likes':video['like_count'], 'dislikes':video['dislike_count']})

	return info
exit()	
