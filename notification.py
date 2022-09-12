import requests
import logging
import base64
import hashlib
import cv2

class Notification:
    def send_wechat(self, pic):
        # image_path = 'D:\\Project\\travel-robot\\mobile_phone\\test_real_image\\test1.jpeg'

        datas = {
            "msgtype": "markdown",
            "markdown": {
                "content": "# 失物招领\nHi， 我发现了一部手机！快看看是哪个小可爱忘了拿？"
            }
        }

        r = requests.post("https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=17c57034-e17c-4d8d-90d5-dbe8bb12e178", json=datas)

        retval, buffer = cv2.imencode('.jpg', pic)
        #with open(image_path, "rb") as img_file:
        #    file_content = img_file.read()
        b64_string = str(base64.b64encode(buffer), encoding='utf-8')
        # logging.info(b64_string)
        md5 = hashlib.md5(buffer).hexdigest()

        datas = {
            "msgtype": "image",
            "image": {
                "base64": b64_string,
                "md5": md5
            }
        }

        r = requests.post("https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=17c57034-e17c-4d8d-90d5-dbe8bb12e178", json=datas)
        logging.info("notificaiton sent with result" + r.text)
