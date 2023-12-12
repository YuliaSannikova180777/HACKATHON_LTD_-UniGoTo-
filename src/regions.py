
import os
import zipfile
import pandas as pd


# Получаем путь к текущей папке скриптов src/
current_dir = os.path.dirname(os.path.abspath(__file__))  # для .py
# current_dir = os.getcwd()  # для .ipynb

# Находим папку проекта относительно папки src/
project_path = os.path.abspath(os.path.join(current_dir, os.pardir))
print(f"Путь к папке проекта '{project_path}'")

# Задаём путь к папке данных относительно папки проекта
data_folder = os.path.join(project_path, 'data')

# Задаём пути и имена файлов для сохранения в папке data/
cities_file = 'cities_filtered.csv'
cities_zip_path = os.path.join(data_folder, cities_file[:-4] + '.zip')
cities_csv_path = os.path.join(data_folder, cities_file)

regions_file = 'regions.csv'
regions_zip_path = os.path.join(data_folder, regions_file[:-4] + '.zip')
regions_csv_path = os.path.join(data_folder, regions_file)

output_file = 'cities_regions.csv'
output_path = os.path.join(data_folder, output_file)

# Проверяем наличие ZIP-архива
if os.path.exists(cities_zip_path):
    # Извлекаем содержимое архива
    with zipfile.ZipFile(cities_zip_path, 'r') as zip_ref:
        if cities_file in zip_ref.namelist():
            zip_ref.extract(cities_file, data_folder)
    input_file_path = cities_zip_path
else:
    input_file_path = cities_csv_path

# Загружаем файл с отфильтрованными данными
cities_data = pd.read_csv(input_file_path)

# Проверяем наличие ZIP-архива
if os.path.exists(regions_zip_path):
    # Извлекаем содержимое архива
    with zipfile.ZipFile(regions_zip_path, 'r') as zip_ref:
        if regions_file in zip_ref.namelist():
            zip_ref.extract(regions_file, data_folder)
    input_file_path = regions_zip_path
else:
    input_file_path = regions_csv_path

# Загружаем файл с отфильтрованными данными
regions_data = pd.read_csv(input_file_path)

# Удаляем строки с пустыми значениями в столбце 'city_title'
# Разкомментить, когда данных будет раз в 10 больше!
# cities_data.dropna(subset=['city_title'], inplace=True)

# Создаём словарь для соответствия города и региона
city_to_region = dict(zip(regions_data['city'], regions_data['region']))

# Создаём новый столбец 'region' на основе словаря соответствия
cities_data['region'] = cities_data['city_title'].map(city_to_region)

# Сохраняем файл соответствия города и региона в файл CSV
cities_data.to_csv(output_path, index=False)
print(f"Файл {output_file} сохранён")