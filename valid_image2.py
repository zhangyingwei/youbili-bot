import json
import base64,requests
from io import BytesIO
try:
    from PIL import Image
except ImportError:
    import Image

class ValidImage2:
    def __init__(self):
        self.__api_post_url__ = "http://www.bingtop.com/ocr/upload/"
        self.__api_user_name__="tester"
        self.__api_password__="723129bao"

    def valid_image(self, img_url):
        res = requests.get(img_url)
        image_data = res.content
        img = Image.open(BytesIO(image_data))
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        img64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        params = {
            "username": "%s" % self.__api_user_name__,
            "password": "%s" % self.__api_password__,
            "captchaData": img64,
            "captchaType": 1324
        }
        response = requests.post(self.__api_post_url__, data=params)
        if response.status_code == 200:
            dictdata = json.loads(response.text)
            return dictdata['data']['recognition']
        return None


if __name__ == '__main__':
    ValidImage2().valid_image(img_url="https://static.geetest.com/captcha_v3/batch/v3/33446/2023-04-26T21/word/ee5f67a959784dc3a25baf039514e66e.jpg?challenge=e7d4ca122bf3d0c6309c14099e548056")