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

# Задаём список имён файлов для загрузки
files_to_process = ['universities.csv', 'faculties.csv', 'countries.csv', 'cities.csv']

# Задаём список имён столбцов для фильтрации
col_names = ['university_name', 'faculty_name']

for file_name in files_to_process:
    # Пути к архиву и файлу для загрузки и сохранения
    input_zip_path = os.path.join(data_folder, file_name[:-4] + '.zip')
    input_csv_path = os.path.join(data_folder, file_name)
    output_path = os.path.join(data_folder, file_name[:-4] + '_filtered.csv')

    # Проверяем наличие ZIP-архива
    if os.path.exists(input_zip_path):
        # Извлекаем содержимое архива
        with zipfile.ZipFile(input_zip_path, 'r') as zip_ref:
            if file_name in zip_ref.namelist():
                zip_ref.extract(file_name, data_folder)
        input_file_path = input_zip_path
    else:
        input_file_path = input_csv_path

    # Загружаем файл CSV в DataFrame
    data = pd.read_csv(input_file_path)

    # Удаляем дубликаты
    data.drop_duplicates(inplace=True)

    # Сортируем по возрастанию первых столбцов
    data.sort_values(by=data.columns[0], inplace=True)

    # Фильтруем названия ВУЗов
    if file_name == 'universities.csv':
        # Группировка данных по столбцу university
        grouped = data.groupby('university')

        # Функция для отбора строки с максимальной длиной имени ВУЗа
        def select_max_length(row):
            max_length = row['university_name'].fillna('').str.len().max()
            return row[row['university_name'].fillna('').str.len() == max_length]

        # Применяем функцию для отбора строк с максимальной длиной имени ВУЗа
        data = grouped.apply(select_max_length)

    # Фильтруем названия факультетов
    if file_name == 'faculties.csv':
        # Группировка данных по столбцу faculty
        grouped = data.groupby('faculty')

        # Функция фильтрации данных: оставляем только строки, содержащие "факультет"
        def filter_group(group):
            if not any(group['faculty_name'].fillna('').str.contains('факультет', case=False)):
                return group
            return group[group['faculty_name'].fillna('').str.contains('факультет', case=False)]

        # Удаление строк в группах, удовлетворяющих условию
        data = grouped.apply(filter_group)

        # Сбросим индекс, чтобы избежать проблемы с дублирующимся столбцом
        data = data.reset_index(drop=True)

        # Переименуем столбец 'faculty', чтобы избежать конфликта
        data = data.rename(columns={'faculty': 'faculty_id'})

        # Функция для отбора строки с максимальной длиной имени факультета
        def select_max_length(row):
            max_length = row['faculty_name'].fillna('').str.len().max()
            return row[row['faculty_name'].fillna('').str.len() == max_length]

        # Применяем функцию для отбора строк с максимальной длиной имени факультета
        data = data.groupby('faculty_id').apply(select_max_length).reset_index(drop=True)

        # Переименуем столбец 'faculty_id' обратно
        data = data.rename(columns={'faculty_id': 'faculty'})

    # Удаляем символы переноса строки
    for col in col_names:
        if col in data.columns:
            data[col] = data[col].str.replace(r'\r\n', '', regex=True)

    # Удаляем 1 строку (где 0 индекс)
    data.drop(labels=[0], axis=0, inplace=True)

    # Сохраняем обработанные данные в CSV
    data.to_csv(output_path, index=False)
    print(f"Файл {file_name[:-4] + '_filtered.csv'} сохранён")