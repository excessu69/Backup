import vk_api
from vk_api.exceptions import VkApiError
import json
import requests
from yadisk import YaDisk
import tempfile
import time
from tqdm import tqdm


def get_photos(vk_session, user_id):
    try:
        vk = vk_session.get_api()
        photos = vk.photos.get(owner_id=user_id, album_id='profile', rev=1, extended=1, photo_sizes=1)
        return photos['items']
    except VkApiError as e:
        print(f"VK API error occurred: {e}")
        return []


def create_photos_folder(y):
    try:
        y.mkdir("/photos")
    except Exception as e:
        print(f"Ошибка при создании папки 'photos' на Яндекс.Диске: {e}")


def save_photo_to_disk(yadisk, photo_url, photo_name):
    response = requests.get(photo_url)
    if response.status_code == 200:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(response.content)
        with open(tmp_file.name, "rb") as f:
            yadisk.upload(f, f"/photos/{photo_name}.jpg", overwrite=True)  # Сохраняем фото в папку 'photos'


def main():
    # Введите свои данные для входа в VK
    vk_token = input("Введите токен VK: ")
    vk_session = vk_api.VkApi(token=vk_token)

    # Введите свои данные для входа в Яндекс.Диск
    yandex_token = input("Введите токен Яндекс.Диска: ")
    y = YaDisk(token=yandex_token)

    create_photos_folder(y)

    user_id = input("Введите ID пользователя VK: ")

    photos = get_photos(vk_session, user_id)
    if photos:
        photos.sort(key=lambda x: x['likes']['count'], reverse=True)  # Сортируем фотографии по количеству лайков
        photos_info = []

        mylist = list(range(5))

        with tqdm(total=len(mylist), desc='Загрузка фотографий') as pbar:
            for photo_index in mylist:  # Берем только первые 5 фотографий с наибольшим количеством лайков
                pbar.update(1)
                photo = photos[photo_index]
                max_size = max(photo['sizes'], key=lambda x: x['width'])
                likes = photo['likes']['count']
                date = photo['date']
                photo_name = f"{likes}_{date}"
                save_photo_to_disk(y, max_size['url'], photo_name)
                photos_info.append({"file_name": f"{photo_name}.jpg", "size": max_size['type']})

        with open("photos_info.json", "w") as json_file:
            json.dump(photos_info, json_file, indent=4)
        print(
            "5 фотографий с наибольшим количеством лайков успешно сохранены на Яндекс.Диске в папке 'photos'.")
    else:
        print("Не удалось получить фотографии с профиля пользователя VK.")


if __name__ == "__main__":
    main()

