import re
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
input_file = 'prefiltered_data.csv'
input_zip_path = os.path.join(data_folder, input_file[:-4] + '.zip')
input_csv_path = os.path.join(data_folder, input_file)
output_file = 'filtered_data.csv'
output_path = os.path.join(data_folder, output_file)

# Проверяем наличие ZIP-архива
if os.path.exists(input_zip_path):
    # Извлекаем содержимое архива
    with zipfile.ZipFile(input_zip_path, 'r') as zip_ref:
        if input_file in zip_ref.namelist():
            zip_ref.extract(input_file, data_folder)
    input_file_path = input_zip_path
else:
    input_file_path = input_csv_path

# Загружаем файл с отфильтрованными данными
data = pd.read_csv(input_file_path)

# Создаём список столбцов интересов пользователей
interest_col = ['about', 'activities', 'books', 'games', 'interests']

# Функция для очистки текста от лишних символов
def clean_text(text):
    # Применяем только к непустым (не NaN) значениям
    if not pd.isnull(text):
        # Заменяем пробелами все знаки, кроме русских, английских букв и пробелов
        text = re.sub(r'[^a-zA-Zа-яА-ЯёЁ\s]', ' ', text)
        
        # Приводим к нижнему регистру
        text = text.lower()
        
        # Удаляем сочетания более 3 подряд идущих букв
        text = re.sub(r'([a-zа-яё])\1{3,}', '', text)
        
        # Удаляем повторяющиеся слова
        text = re.sub(r'\b(\w+)(\s+\1)+\b', r'\1', text)
        
        # Заменяем подряд идущие пробелы на один
        text = re.sub(r'\s+', ' ', text)
                
        # Удаляем пробелы в начале и конце строки
        text = re.sub(r'^\s+|\s+$', '', text)
    return text

# Применяем функцию очистки к интересам
data.loc[:, interest_col] = data[interest_col].apply(lambda x: x.map(clean_text) if x.name in interest_col else x)
print("Столбцы интересов очищены от лишних символов")

# Заменяем пустые значения на 'NaN'
data.replace('', pd.NA, inplace=True)

# Удаляем строки с 'NaN' во всех 5 столбцах интересов
data.dropna(subset=interest_col, thresh=1, inplace=True)
print("Строки с незаполненными столбцами интересов удалены")

# Сохраняем отфильтрованные данные в файл CSV
data.to_csv(output_path, index=False)
print(f"Файл {output_file} сохранён")