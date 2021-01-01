from flask import Flask, render_template, request, redirect, url_for
from flask import Response, jsonify
import json, os, pathlib
from youtubesearchpython import VideosSearch, ResultMode
import time
import youtube_dl
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


app = Flask(__name__)

@app.route('/', methods=["POST", "GET"])
def home():
    if request.method == "POST":
        trm = request.form["search"]
        return redirect(url_for("search", term=trm, page=0))
    else:    
        return render_template('home.html')

@app.route('/search/')
@app.route('/search/<term>/<int:page>')
def search( term, page):
    videos = VideosSearch(term, limit = 20, language = 'en', region = 'US')
    for i in range(0, int(page)):
        videos.next()

    results_dict = videos.result(mode = ResultMode.dict)
    results = results_dict['result']
    print(results)
    term = results
    for i in range(0,19,3):
        try:
            term[i]['title']
        except IndexError:
            pass
        try:
            term[i+1]['title']
        except IndexError:
            pass

    my_dict = {"title":"", "thumbnails":"", "channel":"", "viewCount":"", "publishedTime":"", "id":""}
    term.append(my_dict)
    return render_template('search.html', term = term, page=page)

@app.route('/video/')
@app.route('/video/<title>/<id>/<views>/<channel>/<publishTime>/<back>', methods=["POST", "GET"])
def play(title, id, views, channel, publishTime, back):
    
    if request.method == "POST":
        val = request.form.get("id")
        opt = request.form.get("audiocheck")
        if opt == None:
            opt='blah'
        return redirect(url_for("download", title=title, vid=val, views=views, channel=channel, publishTime=publishTime, option=opt))
    else:
        return render_template('video.html', title=title, id=id, views=views, channel=channel, publishTime=publishTime, back=back)
    

@app.route('/download/')
@app.route('/download/<title>/<vid>/<views>/<channel>/<publishTime>/<option>', methods=["POST", "GET"])
def download(title, vid, views, channel, publishTime, option):
    if option == "checked":
        os.system(f"youtube-dl -i --extract-audio --audio-format mp3 --audio-quality 0 https://www.youtube.com/watch?v={vid}")
    else:
        os.system(f"youtube-dl -f mp4 https://youtube.com/watch?v={vid}")

    return redirect(url_for("play", title=title, id=vid, views=views, channel=channel, publishTime=publishTime, back=2))

@app.route('/downloads/')
def downloads():
    os.system("mv *.mp3 ~/Projects/Myroku/backend/static/downloads")
    os.system("mv *.mp4 ~/Projects/Myroku/backend/static/downloads")

    path = '/home/william/Projects/Myroku/backend/static/downloads/'

    files = os.listdir(path)

    audio = []
    video = []
    for f in files:
        p = pathlib.Path(path+f)
        if p.suffix == ".mp3":
            dict = {"filename":p.name, "path":path+f}
            audio.append(dict)
        else:
            dict = {"filename":p.name, "path":path+f}
            video.append(dict) 
    print(video)
    print(audio)
    return render_template('downloads.html', video=video, audio=audio)

@app.route('/suggest/')
@app.route('/suggest/<id>')
def suges(id):

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox') # required when running as root user. otherwise you would get no sandbox errors. 
    driver = webdriver.Chrome(chrome_options=chrome_options)


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
            print(result)
            if 'entries' in result:
                pass
            else:
                video = result
            info.append({'title':video['title'], 'id':video['id'], 'thumbnails':video['thumbnails'], 'viewCount':video['view_count'], 'channel':video['uploader'], 'publishTime':video[ 'upload_date']})
        
        if len(info)%2==0:
            pass
        else:
            info.append({'title':"", 'id':"", 'thumbnails':"", 'viewCount':"", 'channel':""})
        return info

    return render_template('suggest.html', suggest=getrecondmendations(id))