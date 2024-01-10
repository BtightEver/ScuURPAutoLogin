from base64 import b64decode
import io
import time
from unittest import result
from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image
import requests
from io import BytesIO
from PIL import Image
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
import os
import uuid  # 导入 uuid 模块
import time
driver = webdriver.Chrome()
driver.implicitly_wait(60)
driver.set_page_load_timeout(60)
driver.maximize_window()
driver.get("http://zhjw.scu.edu.cn/login")

driver.find_element(By.CSS_SELECTOR, "#input_username").send_keys("2021141461064")
driver.find_element(By.CSS_SELECTOR, "#input_password").send_keys("wlmxhyqrfd1.")
captcha_element = driver.find_element(By.ID, "captchaImg")

# 获取验证码图片的位置和大小
location = captcha_element.location
size = captcha_element.size

screenshot = driver.execute_script("""
    var canvas = document.createElement('canvas');
    canvas.width = arguments[0];
    canvas.height = arguments[1];
    var ctx = canvas.getContext('2d');
    ctx.drawImage(arguments[2], 0, 0);
    return canvas.toDataURL();
    """, size['width'], size['height'], captcha_element)

# 解码截图数据并保存为图片文件
screenshot = screenshot.split(',')[1]
image_data = b64decode(screenshot)
image = Image.open(io.BytesIO(image_data))

while image.width < 100 or image.height < 100:
    image = image.resize((image.width*2, image.height*2))

image.save("captcha.png")
def perform_ocr(image_path):
    # 替换为你的认证信息
    subscription_key = "38649a1f5a0149b4994097010687212f"
    endpoint = "https://scuvison.cognitiveservices.azure.cn/"
    
    # 创建 ComputerVisionClient
    computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

    # 调用 OCR API
    with open(image_path, "rb") as image_stream:
        read_response = computervision_client.read_in_stream(image_stream, raw=True)

    # 获取操作位置和ID
    read_operation_location = read_response.headers["Operation-Location"]
    operation_id = read_operation_location.split("/")[-1]

    # 循环等待结果
    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)

    # 打印检测到的文本
    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                print(line.text)
                print(line.bounding_box)
            return text_result.lines
    else:
        print("OCR operation failed. Status:", read_result.status)
        print("Error details:", read_result)

    subscription_key = "38649a1f5a0149b4994097010687212f"
    endpoint = "https://scuvison.cognitiveservices.azure.cn/"
    computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
    result = []

    with open("captcha.png", "wb") as f:
        # 如果需要，向base64字符串添加填充
        image_data_padded = image_data + "=" * (4 - (len(image_data) % 4))
        f.write(b64decode(image_data_padded))

    with open("captcha.png", "rb") as image_stream:
        read_response = computervision_client.read_in_stream(image_stream, raw=True)

    read_operation_location = read_response.headers["Operation-Location"]
    operation_id = read_operation_location.split("/")[-1]

    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)

    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                result.append({
                    "text": line.text,
                    "bounding_box": line.bounding_box
                })
    else:
        print("OCR operation failed. Status:", read_result.status)
        print("Error details:", read_result)

    return result
result=perform_ocr("./captcha.png")
print("result")