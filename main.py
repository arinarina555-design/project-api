from dotenv import load_dotenv
import os
from tqdm import tqdm
import requests
from time import sleep
import json





class YD:
    base_url = 'https://cloud-api.yandex.net/v1/disk'
    folder_name = 'PDARZ-TRF-158'
    file_name = 'geo.json'

    def __init__(self, token):
        self.headers = {'Authorization': f'OAuth {token}'}

    def create_folder(self, folder_name):
        params = {'path': f'{folder_name}'}
        response = requests.put(f'{self.base_url}/resources',
                                params=params,
                                headers=self.headers)
        if response.status_code == 201:
            print(f"✅ Папка {folder_name} создана")
        elif response.status_code == 409:
            print(f"⚠️ Папка {folder_name} уже существует")
        else:
            print(f"❌ Ошибка при создании папки {folder_name}: {response.json()}")
        return folder_name

    def get_upload_link(self):
        params = {'path': f'{self.folder_name}/{self.file_name}',
                  'overwrite': 'true'}
        response = requests.get(f'{self.base_url}/resources/upload',
                                headers=self.headers,
                                params=params)
        if response.status_code == 200:
            disk_path = response.json()['href']
            return disk_path
        else:
            error_msg = response.json().get('message', 'Неизвестная ошибка')
            raise Exception(f"Ошибка: {error_msg}")


    def upload_geo(self, geo_data, disk_path):
        try:
            # Преобразуем данные в JSON строку и загружаем
            json_data = json.dumps(geo_data, ensure_ascii=False, indent=2).encode('utf-8')

            # Загружаем файл
            upload = requests.put(disk_path, data=json_data)

            if upload.status_code == 201:
                print(f"✅ Файл {self.file_name} загружен успешно")
                return True
            else:
                print(f"❌ Ошибка загрузки: {upload.text}")
                return False

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False



class IP:
    @staticmethod
    def get_ip()-> str:
        your_ip = requests.get('https://api.ipify.org/?format=json')
        ip = your_ip.json()['ip']
        return ip



class Geo:
    @staticmethod
    def get_geo(ip) -> dict:
        geo_file = requests.get(f'https://ipinfo.io/{ip}/geo')
        if geo_file.status_code == 200:
            return geo_file.json()
        else:
            raise Exception(f"Ошибка получения геоданных: {geo_file.status_code}")







def main():

    load_dotenv()
    token = os.getenv('TOKEN')

    yd = YD(token)
    steps = [
        "Получение IP-адреса",
        "Получение геоданных",
        "Создание папки на Яндекс.Диске",
        "Получение ссылки для загрузки",
        "Загрузка данных на Яндекс.Диск"
    ]
    with tqdm(total=len(steps), desc="Выполнение задачи", unit="шаг") as pbar:
        pbar.set_description("Получение IP-адреса")
        ip = IP.get_ip()
        pbar.update(1)
        sleep(0.1)

        pbar.set_description("🌍 Получение геоданных")
        geo_data = Geo.get_geo(ip)
        pbar.update(1)
        sleep(0.1)

        pbar.set_description("📁 Создание папки на Яндекс.Диске")
        new_folder = yd.create_folder(YD.folder_name)
        pbar.update(1)
        sleep(0.1)

        pbar.set_description("🔗 Получение ссылки для загрузки")
        upload_link = yd.get_upload_link()
        pbar.update(1)
        sleep(0.1)

        pbar.set_description("⬆️ Загрузка данных на Яндекс.Диск")
        yd.upload_geo(geo_data, upload_link)
        pbar.update(1)

        print(f"✅ Данные загружены на Яндекс.Диск: {YD.file_name}")

        return 0

if __name__ == "__main__":
    exit(main())