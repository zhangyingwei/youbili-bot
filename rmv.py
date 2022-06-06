import os

path='/app/youbili-bot/video'

for video in os.listdir(path):
    vpath = os.path.join(path,video,"v.mp4")
  #  print(vpath)
    try:
        os.remove(vpath)
        print(vpath)
    except:
        pass
