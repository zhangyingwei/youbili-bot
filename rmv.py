import os

path='/data/video'

for video in os.listdir(path):
    dpath = os.path.join(path,video,"done")
    try:
        if os.path.exists(dpath):
            print("+++++++++++++++++")
            for infile in os.listdir(os.path.join(path,video)):
                os.remove(os.path.join(path,video,infile))
                print(f"remove: {os.path.join(path,video,infile)}")
            os.remove(os.path.join(path,video))
            print(f"remove: {os.path.join(path, video, infile)}")
            print("-----------------")
    except:
        pass
