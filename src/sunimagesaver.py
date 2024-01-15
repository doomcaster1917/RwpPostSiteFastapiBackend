# It saves picture from user on vk.com's image server 'sunuserapi' and returns the url of image
import json
from io import BytesIO
import aiohttp
from PIL import Image
from .config import VK_TOKEN

public_token = (VK_TOKEN)
group_id = 168297205
version = 5.131

async def descriptor_image(image_content):
    img = BytesIO(image_content)
    data = Image.open(img, 'r')


    finished_image_content = BytesIO()
    data.save(finished_image_content, format='png')
    finished_image_content.seek(0)
    finished_image_content.name = (
        '/home/barbus/Изображения/Снимки экрана/Снимок экрана от 2022-07-17 23-55-24.png'
    )

    return finished_image_content

async def download_img_to_sun_userapi(image_content):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.vk.com/method/photos.getMessagesUploadServer',
                                   params={'access_token': public_token, 'group_id': group_id, 'v': version}) as resp:
                result = await resp.json()
                server_url = result['response']['upload_url']
                photo_bytes = await descriptor_image(image_content)
                resp = await session.post(server_url, data={'photo': photo_bytes})
                data = json.loads(await resp.content.read())
                result = await session.post('https://api.vk.com/method/photos.saveMessagesPhoto',
                                       data={'access_token': public_token, 'photo': data['photo'],
                                             'server': data['server'], 'hash': data['hash'], 'v': version})
                return json.loads(await result.content.read())
    except Exception as e:
        print(e)

async def get_sun_userapi_url(image_content):
    data = await download_img_to_sun_userapi(image_content)
    items = data['response'][0]['sizes']

    sizes = []
    for size in items:
        sizes.append([size['height'], size['width']])

    max_size = max(sizes)

    url = ''
    for item in items:
        if item['height'] == max_size[0] and item['width'] == max_size[1]:
            url = item['url']

    return url