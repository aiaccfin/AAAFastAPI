import json, requests
from base64 import b64encode

def request_ocr(endpoint_url, api_key, imgpath):
    img_data = make_image_data(imgpath)
    response = requests.post(
        endpoint_url,
        data=img_data,
        params={'key': api_key},
        headers={'Content-Type': 'application/json'}
    )
    return response

def make_image_data(imgpath):
    with open(imgpath, 'rb') as f:
        content = b64encode(f.read()).decode()
        img_req = {
            'image': {
                'content': content
            },
            'features': [{
                'type': 'DOCUMENT_TEXT_DETECTION',
                'maxResults': 1
            }]
        }
    return json.dumps({"requests": [img_req]}).encode()
