# -*- coding: utf-8 -*-
from flask import Flask,render_template,Response,request,redirect,jsonify,url_for
import os
from datetime import *
import math
from operator import itemgetter
import numpy as np
import xml.dom.minidom
import xml.etree.ElementTree as ET
from werkzeug.security import generate_password_hash, check_password_hash
from json import dumps
from urllib.parse import urlencode
from fileinput import filename
import platform
print(platform.release())
print(platform.version())
OnPi = False

app = Flask(__name__)

CurrentPage = 1
PerPage = 23
pages = 0
LastPage = 1
CP = 0
data = {}
loggedin = 0
message = ""

# Get configuration
def get_config():
    # parse the XML file
    xml_doc = xml.dom.minidom.parse('static/config.xml')
    # get all the config elements
    config = xml_doc.getElementsByTagName('config')
    # loop through the configuration and extract the data
    
    for item in config:
        itemsperpage = int(item.getElementsByTagName('itemsperpage')[0].childNodes[0].data)             #0
        music_start_delay = item.getElementsByTagName('music_start_delay')[0].childNodes[0].data        #1
        sound_start_delay = item.getElementsByTagName('sound_start_delay')[0].childNodes[0].data        #2
        delay_between_sounds = item.getElementsByTagName('delay_between_sounds')[0].childNodes[0].data  #3
        music_volume = item.getElementsByTagName('music_volume')[0].childNodes[0].data                  #4
        sound_volume = item.getElementsByTagName('sound_volume')[0].childNodes[0].data                  #5
        pin = item.getElementsByTagName('pin')[0].childNodes[0].data                                    #6
        music_path = item.getElementsByTagName('music_path')[0].childNodes[0].data                      #7
        sound_path = item.getElementsByTagName('sound_path')[0].childNodes[0].data                      #8
        shit_duration = item.getElementsByTagName('shit_duration')[0].childNodes[0].data
        play_music = item.getElementsByTagName('play_music')[0].childNodes[0].data                #9
    config = [itemsperpage,music_start_delay,sound_start_delay,delay_between_sounds,music_volume,sound_volume,pin,music_path,sound_path,shit_duration,play_music]    
    return config

def save_config(data):
    global message
    try:
        tree = ET.parse('static/config.xml')
        root = tree.getroot()
        root[0].text = data[0]
        root[1].text = data[1]
        root[2].text = data[2]
        root[3].text = data[3]
        root[4].text = data[4]
        root[5].text = data[5]
        root[6].text = data[6]
        root[7].text = data[7]
        root[8].text = data[8]
        root[9].text = data[9]
        root[10].text = data[10]
        # create a new XML file with the new element
        tree.write('static/config.xml')
    except Exception as e:
        message = "Error saving config<br>"+e
        return False
    return True

config = get_config()

def getMusic(path):
    music = []
    for root,d_names,f_names in os.walk(path):
        for file in f_names:
            music.append(root+"/"+file)
    return music

def getsoundfx(path):
    sounds = []
    for root,d_names,f_names in os.walk(path):
        for file in f_names:
            sounds.append(root+"/"+file)
    return sounds

@app.errorhandler(404) 
def invalid_route(e):
	return render_template('404.html',error=e)

@app.route('/login', methods=["POST"])
def Auth():
    global loggedin
    global message
    config = get_config()
    pin = request.form['pin']
    res = "Login Failed"
    if pin == config[8]:
        res = "Authorized"
        loggedin = 1
        message = "Logged In"
    else:
        loggedin = 0
        message = "Login Failed, please try again"
    return redirect('/config')

@app.route('/logout', methods=["GET"])
def logout():
    global loggedin
    global message
    loggedin = 0
    message = "Logged Out"
    return redirect('/config')

@app.route('/', methods=["GET"])
def index():
    config = get_config()
    
    return render_template('config.html',config=config,loggedin=loggedin,message=message)

CurrentPage = 1
pages = 0
LastPage = 1
CP = 0
@app.route('/music/<int:CurrentPage>', methods=["GET"])
def music(CurrentPage):
    config = get_config()
    PerPage = config[0]
    global CP
    global LastPage
    data = []
    config = get_config()
    data = ""
    pages = 1
    NextPage = 1
    PrevPage = 1
    music = getMusic(config[7])
    print(music)
    try:
        CurrentPage = int(CurrentPage)
        stuff = music
        items = len(stuff)
        pages = items / PerPage
        pages = math.ceil(pages)
        NextPage = CurrentPage+1
        PrevPage = CurrentPage-1        

        #print(CurrentPage,LastPage)
        if CurrentPage > LastPage:
            CP = CP+PerPage
            data = music[CP:CP+PerPage]
            print("PageUp",CP,CP+PerPage)
            LastPage = CurrentPage

        elif CurrentPage < LastPage:
            CP = CP-PerPage
            data = music[CP:CP+PerPage]
            print("PageDown",CP,CP+PerPage)
            LastPage = CurrentPage

        if CurrentPage <= 1:
            CP = 0
            data = music[CP:CP+PerPage]
            NextPage = CurrentPage+1
            PrevPage = 1

        if CurrentPage >= pages:
            CP = items-PerPage
            NextPage = CurrentPage
            PrevPage = CurrentPage-1
            data = music[CP:items-1]
        if pages <= 1:
            pages = 1
            PrevPage = 1
            NextPage = 1
            data = music

    except Exception as e:
        print("Index ERROR: ",e)
    print("Pages: ",pages)
    if len(music) < 2: data=music
    return render_template('music.html',config=config,music=data,page=CurrentPage, pages=int(pages),nextPage = NextPage, prevPage=PrevPage)

@app.route('/sound/<int:CurrentPage>', methods=["GET"])
def sound(CurrentPage):
    config = get_config()
    PerPage = config[0]
    global CP
    global LastPage
    data = []
    config = get_config()
    data = ""
    pages = 1
    NextPage = 1
    PrevPage = 1
    soundfx = getsoundfx(config[8])
    print("Page: ",CurrentPage)
    try:
        CurrentPage = int(CurrentPage)
        stuff = soundfx
        items = len(stuff)
        pages = items / PerPage
        pages = math.ceil(pages)
        NextPage = CurrentPage+1
        PrevPage = CurrentPage-1

        #print(CurrentPage,LastPage)
        if CurrentPage > LastPage:
            CP = CP+PerPage
            data = soundfx[CP:CP+PerPage]
            print("PageUp",CP,CP+PerPage)
            LastPage = CurrentPage

        elif CurrentPage < LastPage:
            CP = CP-PerPage
            data = soundfx[CP:CP+PerPage]
            print("PageDown",CP,CP+PerPage)
            LastPage = CurrentPage

        if CurrentPage == 1:
            CP = 0
            data = soundfx[CP:CP+PerPage]
            NextPage = CurrentPage+1
            PrevPage = CurrentPage

        if CurrentPage == pages:
            CP = items-PerPage
            NextPage = CurrentPage
            PrevPage = CurrentPage-1
            data = soundfx[CP:items-1]
        if pages <= 1:
            pages = 1
            PrevPage = 1
            NextPage = 1
            data = soundfx

    except Exception as e:
        print("Index ERROR: ",e)

    config = get_config()
    if len(soundfx) < 2: data=soundfx
    return render_template('sounds.html',config=config,soundfx=data, page=CurrentPage, pages=int(pages),prevPage=PrevPage,nextPage=NextPage)


@app.route("/playsound", methods = ["POST"])
def streamwav():
    file = request.form['file']
    def generate(file):
        with open(file, "rb") as fwav:
            data = fwav.read(1024)
            while data:
                yield data
                data = fwav.read(1024)
    return Response(generate(), mimetype="audio/x-mp3")

@app.route("/DeleteFile", methods = ["POST"])
def DeleteFile():
    file = request.form['filename']
    print(os.getcwd())
    if os.path.exists(os.getcwd()+"/"+file):
        os.remove(os.getcwd()+"/"+file)
        return file+" Has been deleted"
    else:
        return "The file does not exist"

@app.route('/save_config', methods=["POST"])
def saveconfig():
    global message
#try:
    config = get_config()
    config[0] = request.form['list_items']
    config[1] = request.form['music_start_delay']
    config[2] = request.form['sound_start_delay']
    config[3] = request.form['delay_between_sounds']
    config[4] = request.form['music_volume']
    config[5] = request.form['sound_volume']
    config[6] = "123456"
    config[7] = request.form['music_path']
    config[8] = request.form['sound_path']
    config[9] = request.form['shit_duration']
    try:
        config[10] = request.form['play_music']
    except:
        config[10] = "0"
        pass

    save_config(config)
#except Exception as E:
#    print("SaveConfig: ",str(E))
#finally:
    return redirect("/")

@app.route('/errorlog', methods=["GET"])
def errrolog():
    file1 = open("error.log", "r")  # append mode
    content = file1.read()
    file1.close()    
    return render_template('errorlog.html',content=content)

@app.route('/confirmrestart', methods=["GET"])
def ConfRestart():
    config = get_config()
    return render_template('restart.html',config=config)

@app.route('/confirmstop', methods=["GET"])
def ConfStop():
    return render_template('stop.html')

@app.route('/restart', methods=["GET"])
def Restart():
    os.system("echo pjlxdv12 | sudo -S reboot &")
    return "REBOOTING"

@app.route('/stop', methods=["GET"])
def Stop():
    os.system("echo pjlxdv12 | sudo -S shutdown now &")
    return "Shutdown"

@app.route('/checkconnect', methods=["GET"])
def checkconnect():
    return "Connected"

@app.route('/success', methods = ['POST'])  
def success():  
    if request.method == 'POST':
        path = request.form['path']
        if path == "/sound/1":store=config[8]
        if path == "/music/1":store=config[7]
        f = request.files['file']
        f.save(store+"/"+f.filename)  
        return redirect(path)
     
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000, debug=True, threaded=True)

