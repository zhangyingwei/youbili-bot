import os

path='/data/video'

for video in os.listdir(path):
    dpath = os.path.join(path,video,"done")
    try:
        if os.path.exists(dpath):
            print("+++++++++++++++++")
            for infile in os.listdir(os.path.join(path,video)):
                infile_path = os.path.join(path,video,infile)
                if os.path.isdir(infile_path):
                    os.rmdir(infile_path)
                    print(f"remove dir: {infile_path}")
                else:
                    os.remove(infile_path)
                    print(f"remove file: {os.path.join(path,video,infile)}")
            os.remove(os.path.join(path,video))
            print(f"remove: {os.path.join(path, video, infile)}")
            print("-----------------")
    except Exception as e:
        print(f"报错了: {e}. 尝试删除dir")
        try:
            os.rmdir(infile_path)
            print(f"remove dir: {infile_path}")
        except Exception as e2:
            print(f"remove dir failed.{e2}")
