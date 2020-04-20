import cv2
import io
import time
import requests
import numpy as np
from skills.mycroft_aimar import aimar_util

picamera_enabled = False
TEMP_IMAGE_PATH = "temp_image.png"

try:
    import picamera
    picamera_enabled = True
except ImportError as ex:
    print(f"Warning: No picamera library found.")


def capture_usbcam():
    # captures image and stores in 'frame' variable
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    # save as png buffer
    is_success, arr = cv2.imencode(".jpg", frame)
    buf = io.BytesIO(arr)
    image_data = buf.getvalue()
    return image_data


def capture_picam():
    # Create an in-memory stream
    buf = io.BytesIO()
    with picamera.PiCamera() as camera:
        camera.start_preview()
        # Camera warm-up time
        time.sleep(2)
        camera.capture(buf, 'jpeg')
    image_data = buf.getvalue()
    buf.close()
    return image_data


def capture_image():
    try:
        if picamera_enabled:
            image_data = capture_picam()
        else:
            image_data = capture_usbcam()
    except cv2.error as e:
        print(e)
        return None
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    cv2.imwrite(TEMP_IMAGE_PATH, img)
    return image_data


def diagnose_skin_image(image_data):
    try:
        resp = requests.post(f"http://{aimar_util.DESKTOP_IP}/api/skin", data=image_data)
        resp_json = resp.json()
        report_text = ""
        for key in resp_json:
            report_text += f"{key}: {100*float(resp_json[key]):.1f}%\n"
        return report_text
    except OSError:
        return None
