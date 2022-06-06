import os

path='/app/youbili-bot/video'

for video in os.listdir(path):
    vpath = os.path.join(path,video,"v.mp4")
    dpath = os.path.join(path,video,"done")
  #  print(vpath)
    try:
        if os.path.exists(dpath):
            os.remove(vpath)
            print(vpath)
    except:
        pass
