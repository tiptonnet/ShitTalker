import pygame
from pygame import mixer
import time
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
import os
import random
import xml.dom.minidom
import xml.etree.ElementTree as ET
import platform
import datetime
#  Make sure this is a Raspberry before we load GPIO
OnPi = True

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
sensor = 23
GPIO.setup(sensor, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Get configuration
def traps(data):
    x = datetime.datetime.now()
    print(x)
    file1 = open("error.log", "a")  # append mode
    file1.write(str(x)+" \n"+data+"\n")
    file1.close()
    return True

def get_config():
    try:    
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
    except Exception as E:
        traps(str(E))
        return False

config = get_config()
# We need to know how many seconds have elapsed since motion trigger
seconds_elapsed = float(config[1]) + float(config[2])
music_elapsed = float(config[1]) + float(config[2])

def getMusic(path):
    try:
        music = []
        for root,d_names,f_names in os.walk(path):
            for file in f_names:
                music.append(root+"/"+file)
        return music
    except Exception as E:
        traps(str(E))
        return False

Soundsplayed = []

def getsoundfx(path):
    try:
        sounds = []
        for root,d_names,f_names in os.walk(path):
            for file in f_names:
                sounds.append(root+"/"+file)
        return sounds
    except Exception as E:
        traps(str(E))
        return  False

soundfx = getsoundfx(config[8])
sounds = len(soundfx)

def mutagen_length(path):
    try:
        try:
            audio = MP3(path)
            length = audio.info.length
            return length
        except:
            audio = WAVE(path)
            length = audio.info.length
            return length
    except Exception as E:
        traps(str(E))
        return False
    
def mutagen_frequency(path):
    try:
        try:
            audio = MP3(path)
            frequency=audio.info.sample_rate
            #print(frequency)
            return frequency
        except:
            audio = WAVE(path)
            frequency = audio.info.sample_rate
            #print(frequency)
            return frequency
    except Exception as E:
        traps("mutagen_frequency: "+str(E))
        return False
    
def HasPlayed(sound):
    global Soundsplayed
    soundfx = getsoundfx(config[8])
    sounds = len(soundfx)
    if not sound in Soundsplayed:
        Soundsplayed.append(sound)
        print(sounds,len(Soundsplayed))
        if len(Soundsplayed) >= sounds/2:
            Soundsplayed = []
        print(Soundsplayed)
        return False
    else:
        print(sounds,len(Soundsplayed))
        return True
    
def get_random(ceiling): 
    # resultant random numbers list
    randomList=[]
    # traversing the loop 15 times
    for i in range(15):
        # generating a random number in the range 1 to 100
        r=random.randint(1,100)
        # checking whether the generated random number is not in the
        # randomList
        if r not in randomList:
            # appending the random number to the resultant list, if the condition is true
            randomList.append(r)
    # printing the resultant random numbers list
    print("non-repeating random numbers are:")
    print(randomList)
    # removing repeating elements from the list using the set() function
    resultSet=set(randomList)
    # converting the set into a list(now the list has only unique elements)
    uniqueList =list(resultSet)
    # printing 4 random numbers from the list which is non-repeating
    print("4 non-repeating random numbers from the list are:")
    print(random.sample(uniqueList, 1))

music = getMusic(config[7])

def get_song(music):
    try:
        songs = len(music)
        get_random(songs)
        s = random.randint(0, songs-1)
        song = music[s]
        print(s,song)
        return song
    except Exception as E:
        traps(str(E))
        return False

def get_sound():
    #print(sounds)
    s = random.randint(0, sounds-1)
    try:
        snd = mixer.Sound(soundfx[s])
        length = mutagen_length(soundfx[s])
        frequency = mutagen_frequency(soundfx[s])
        length = round(length)
        #Reduce repeats
        if HasPlayed(s):
            get_sound()
            return False
        #print(s,soundfx[s],length+2,frequency)
        return [snd,length,frequency]
    except Exception as e:
        print(str(e))
        traps("get_sound: "+str(e))
        return False

def Listen():
    if OnPi:
        print("Listening")
        while True:
            if GPIO.input(sensor):
                print("Motion:  Play some shit!!")
                PlayShit()
                break
    else:
        print("Wrong device, Nothing to do here but shit")
        PlayShit()

# Play the sounds; these will play simultaneously with the music
def PlayShit():
    try:
        global seconds_elapsed
        global music_elapsed
        if config[10] == "1":
            song = get_song(music)
            if song:
                # Starting the mixer
                frequency = mutagen_frequency(song)
                mixer.init(frequency=frequency)
                mixer.music.load(song)
                # Setting the volume
                mixer.music.set_volume(float(config[4]))
                # Start playing the song
                time.sleep(int(config[1]))
                mixer.music.play(-1)
                musiclength = mutagen_length(song)
            else:
                mixer.init(44100)
                musiclength = 0
        else:
            mixer.init(44100)
            musiclength = 0

        for i in range(mixer.get_num_channels()):
            c = mixer.Channel(i)
            c.set_volume(float(config[5]))

        time.sleep(int(config[2]))
        while True:
            snd = get_sound()
            length = 1
            if snd != False:
                snd1 = snd[0]
                length = snd[1]
                snd1.play()

            time.sleep(length+int(config[3]))
            seconds_elapsed += length+int(config[3])
            music_elapsed += length+int(config[3])
            print("seconds_elapsed: ",seconds_elapsed)
            if config[10] == "1":
                print("music_elapsed: ",music_elapsed," Music length: ",musiclength)
                #Play a new song when first one quits

                if music_elapsed > musiclength-20:
                    music_elapsed = float(config[1]) + float(config[2])
                    mixer.music.stop()
                    song = get_song(music)
                    if song:
                        mixer.music.load(song)
                        mixer.music.play(-1)

            #Stop the Shit Talk after about 400 seconds.
            if seconds_elapsed > int(config[9]):
                seconds_elapsed = float(config[1]) + float(config[2])
                snd1.stop()
                if config[10] == "1":
                    mixer.music.stop()
                Listen()
                
    except Exception as E:
        traps("PlayShit: "+str(E))
        return False

#PlayShit()
x = 10
while x > 0:
    print(x)
    x -= 1
    time.sleep(1)
#PlayShit()
Listen()
