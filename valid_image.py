import requests
import json
try:
    from PIL import Image
except ImportError:
    import Image
from io import BytesIO
import base64

class ValidImageClient:
    def __init__(self):
        self.ocr_url = "http://localhost:6688/api.Text_Choose_Click"

    def __convert_img__(self,img):
        img = img.convert("L")  # 处理灰度
        pixels = img.load()
        for x in range(img.width):
            for y in range(img.height):
                if pixels[x, y] > 145:
                    pixels[x, y] = 255
                else:
                    pixels[x, y] = 0
        return img

    def __get_texts__(self,img_url):
        res = requests.get(img_url)
        image_data = res.content
        img = Image.open(BytesIO(image_data))
        cropped_img = img.crop((0, img.height - 40, 150, img.height))
        cropped_img = cropped_img.convert("L")
        # cropped_img.show()
        buffered = BytesIO()
        cropped_img.save(buffered, format="JPEG")
        encoded_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
        print(encoded_image)
        text = self.__get_from_ocr__(encoded_image)
        if text is not None:
            texts = []
            for tt in text:
                texts.append(tt)
            return texts
        return None

    def __get_points_dict__(self,img_url):
        res = requests.get(img_url)
        image_data = res.content
        img = Image.open(BytesIO(image_data))
        cropped_img = img.crop((0, 0, img.width, img.height-40))
        r_channel, g_channel, b_channel = cropped_img.split()
        # cropped_img = g_channel.convert("L")
        # b_channel.show()
        text_dict_r = self.__get_points_dict_of_image__(r_channel)
        text_dict_g = self.__get_points_dict_of_image__(g_channel)
        text_dict_b = self.__get_points_dict_of_image__(b_channel)
        merged_dict = {}
        merged_dict.update(text_dict_r)
        merged_dict.update(text_dict_g)
        merged_dict.update(text_dict_b)
        return merged_dict

    def __get_from_ocr__(self,base64_str):
        res = requests.post(self.ocr_url,data=json.dumps({
            "ChoiceClick_ImageBase64": base64_str
        }))
        if res.status_code == 200:
            print(res.content.decode(encoding="UTF-8"))
            json_res = json.loads(res.content.decode(encoding="UTF-8"))
            return json_res['result']
        else:
            return None

    def valid(self,img_url):
        texts = self.__get_texts__(img_url)
        text_dict = self.__get_points_dict__(img_url)
        print(texts,text_dict)
        if texts is None:
            return None
        points = []
        for text in texts:
            point = text_dict.get(text,[0,0])
            points.append(point)
        return points

    def __get_points_dict_of_image__(self, image):
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        encoded_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
        # print(encoded_image)
        text = self.__get_from_ocr__(encoded_image)
        return text


if __name__ == '__main__':
    img_url="https://static.geetest.com/captcha_v3/batch/v3/33410/2023-04-26T12/word/a58ff87cdeae4637a86e5af4f8fdf9d0.jpg?challenge=3e43647e528cdbeb966271f1dca17a64"
    client = ValidImageClient()
    points = client.valid(img_url)
    print(points)