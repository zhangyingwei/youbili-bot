import os

path='/data/video'

def try_delete_file(file_path):
    if os.path.isdir(file_path):
        os.rmdir(file_path)
        print(f"remove dir: {file_path}")
    else:
        os.remove(file_path)
        print(f"remove file: {file_path}")

for video in os.listdir(path):
    dpath = os.path.join(path,video,"done")
    try:
        if os.path.exists(dpath):
            print("+++++++++++++++++")
            for infile in os.listdir(os.path.join(path,video)):
                infile_path = os.path.join(path,video,infile)
                try_delete_file(infile_path)
            try_delete_file(os.path.join(path,video))
            print("-----------------")
    except Exception as e:
        print(f"报错了: {e}")
        pass