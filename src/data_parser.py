import os
import requests
import json
import time
import pandas as pd
import zipfile


# Задаём токен для доступа к API сервиса
# token = "gQJVK5ifwfJqd4OBDmM"  # наш
token = "JyfAAd77dWtxuK5FUYw"

# Задаём начальную и конечную страницы
start_page = 454001
end_page = 500000

# Задаём размер батча
batch_size = 250

# Задаём максимальное количество запросов в минуту
requests_limit = 10

# Задаём задержку между запросами в секундах
delay = 60 / requests_limit

# Получаем путь к текущей папке скриптов src/
current_dir = os.path.dirname(os.path.abspath(__file__))  # для .py
# current_dir = os.getcwd()  # для .ipynb

# Находим папку проекта относительно папки src/
project_path = os.path.abspath(os.path.join(current_dir, os.pardir))
print(f"Путь к папке проекта '{project_path}'")

# Задаём путь к папке raw_data/ относительно папки проекта
output_folder = os.path.join(project_path, 'raw_data')

# Создаём папку raw_data/, если ёё нет
os.makedirs(output_folder, exist_ok=True)

# Проходим по каждому батчу страниц и получаем JSON
for batch_start in range(start_page, end_page + 1, batch_size):
    batch_end = min(batch_start + batch_size - 1, end_page)
    output_filename = f'all_pages_data {batch_start}-{batch_end}.csv'  # Формирование уникального имени файла
    zip_filename = f'all_pages_data {batch_start}-{batch_end}.zip'  # Формирование уникального имени ZIP-архива
    
    # Создаём пустой DataFrame для хранения данных текущего батча
    all_pages_data = pd.DataFrame()
    
    for page_number in range(batch_start, batch_end + 1):
        url = f"http://45.91.8.110/api/{page_number}?token={token}"
        response = requests.get(url)
        
        if response.status_code == 200:
            page_data = response.json()
            if 'response' in page_data and page_data['response']:
                users_data = page_data['response']
                
                for user_data in users_data:
                    if 'country' in user_data and 'city' in user_data:
                        user_data.update({
                            'country_id': user_data['country']['id'],
                            'country_title': user_data['country']['title'],
                            'city_id': user_data['city']['id'],
                            'city_title': user_data['city']['title']
                        })
                        del user_data['country']
                        del user_data['city']
                    else:
                        print(f"Данные по стране или городу отсутствуют на странице {page_number}")
                
                page_df = pd.DataFrame(users_data)
                all_pages_data = pd.concat([all_pages_data, page_df], ignore_index=True)
            else:
                print(f"Данные отсутствуют на странице {page_number}")
        else:
            print(f"Не удалось получить данные с {url}")
        
        time.sleep(delay)
    
    # Сохраняем данные текущего батча в отдельный файл CSV
    if not all_pages_data.empty:
        output_path = os.path.join(output_folder, output_filename)
        all_pages_data.to_csv(output_path, index=False, encoding='utf-8')
        
        # Создаём ZIP-архив и добавляем в него CSV-файл
        with zipfile.ZipFile(os.path.join(output_folder, zip_filename), 'w') as zipf:
            zipf.write(output_path, arcname=output_filename)
        
        print(f"Файл {zip_filename} сохранён")
        os.remove(output_path)  # Удаляем исходный CSV-файл после архивирования
    else:
        print(f"Нет данных для сохранения в файле {output_filename}")
