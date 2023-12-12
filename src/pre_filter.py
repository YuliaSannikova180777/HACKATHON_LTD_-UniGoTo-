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
input_file = 'combined_data.csv'
input_zip_path = os.path.join(data_folder, input_file[:-4] + '.zip')
input_csv_path = os.path.join(data_folder, input_file)
output_file = 'prefiltered_data.csv'
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
data = pd.read_csv(input_file_path, low_memory=False)

# Создаём список столбцов интересов пользователей
interest_col = ['about', 'activities', 'books', 'games', 'interests']

# Создаём список столбцов с числовыми значениями
num_col = ['country_id', 'city_id', 'faculty', 'university']

# Удаляем дубликаты
data.drop_duplicates(inplace=True)
print("Дубликаты удалены")

# Удаляем строки, в которых количество заполненных столбцов интересов < 3
data.dropna(subset=interest_col, thresh=3, inplace=True)
print("Строки, в которых количество заполненных столбцов интересов < 3, удалены")

# Список рекламных слов и фраз
advertising_words = ['предлагаем', 'производим', 'продаем', 'продаём', 'работаем', 'пассивный доход',
                     'обучаем', 'недорого', 'стоимост', 'оплат', 'клиент', 'заработок', 'http', '@',
                     'полный спектр', 'лава украин', 'ava ukrain', 'уведомлени', 'kizarubones']

# Функция проверки наличия рекламных слов в столбцах интересов
def contains_advertising_words_in_interests(row):
    for col in interest_col:
        text = str(row[col]).lower()  # Приводим текст в столбце к нижнему регистру
        if any(word.lower() in text for word in advertising_words):
            return True
    return False

# Удаляем строки, содержащие рекламные слова в столбцах интересов
data = data[~data.apply(contains_advertising_words_in_interests, axis=1)]
print("Строки, содержащие рекламные слова в столбцах интересов, удалены")

# Меняем значения 'NaN' столбцов с числовыми значениями на 0
data[num_col] = data[num_col].fillna(0)

# Удаляем строки, где значения столбцов с числовыми значениями = 0
for col in num_col:
    data = data[data[col] != 0]
print("Строки с числовыми значениям = 0 удалены")

# Преобразуем типы данных столбцов
data['country_id'] = data['country_id'].astype('int16')
for col in num_col[1:]:
    data[col] = data[col].astype('int32')
print("Столбцы с числовыми значениями преобразованы в int16 и int32")

# Сохраняем отфильтрованные данные в файл CSV
data.to_csv(output_path, index=False)
print(f"Файл {output_file} сохранён")