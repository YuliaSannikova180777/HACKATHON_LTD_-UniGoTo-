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

# Задаём путь к папке с файлами ZIP относительно папки проекта
folder_path = os.path.join(project_path, 'raw_data')

# Получаем список файлов в папке raw_data/
files = os.listdir(folder_path)

# Создаём пустой список для хранения DataFrame из каждого файла
df_list = []

# Задаём список столбцов для считывания в DataFrame
col_names = ['about',
             'activities',
             'books',
             'games',
             'interests',
             # 'education_form',  # форма обучения
             # 'education_status',  # статус студента
             'university',
             'university_name',
             'faculty',
             'faculty_name',
             # 'graduation',  # год выпуска
             'country_id',
             'country_title',
             'city_id',
             'city_title']

# Задаём тип данных 'Int64' для поддержки NaN значений
dtypes = {'university': 'Int64',
          'faculty': 'Int64',
          # 'graduation': 'Int64',  # год выпуска
          'country_id': 'Int64',
          'city_id': 'Int64'}

# Считывание каждого файла CSV из архива ZIP
for file in files:
    if file.endswith('.zip'):
        file_path = os.path.join(folder_path, file)

        # Открываем архив ZIP
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            # Ищем и считываем первый файл CSV внутри архива
            for zip_file in zip_ref.namelist():
                if zip_file.endswith('.csv'):
                    with zip_ref.open(zip_file) as csv_file:
                        # Считываем указанных столбцов и задание типа данных для них
                        df = pd.read_csv(csv_file, usecols=col_names, dtype=dtypes)
                        # Добавляем DataFrame в список df_list
                        df_list.append(df)
                    break  # Прерываем цикл, чтобы прочитать только первый CSV-файл из архива

# Объединяем все DataFrame из списка df_list в один
data = pd.concat(df_list, ignore_index=True)

# Задаём пороговые значения
thresholds = {'country_id': 500,
              'city_id': 9000000,
              'faculty': 5000000,
              'university': 3000000}

# Удаляем строки, где значения превышают пороговые значения
for column, threshold in thresholds.items():
    data = data[data[column] <= threshold]
print("Строки, где значения превышают пороговые значения, удалены")

# Создаём паттерн для поиска русских символов
russian_pattern = re.compile('[А-Яа-яЁё]+')

# Функция для определения, является ли строка русским текстом
def is_russian(text):
    return bool(russian_pattern.search(str(text)))

# Фильтруем данные, оставляя только строки с русскими названиями ВУЗов и незаполненными значениями
data = data[(data['university_name'].apply(is_russian)) | (data['university_name'].isnull())]
print("Строки, где названия ВУЗов указаны не на русском языке, удалены, а незаполненные - оставлены")

# Сохраняем вспомогательные таблицы в отдельные DataFrame
universities = data[['university', 'university_name']]
faculties = data[['faculty', 'faculty_name']]
countries = data[['country_id', 'country_title']]
cities = data[['city_id', 'city_title']]

# Задаём пути и имена файлов и папок для сохранения внутри папки проекта
data_folder = os.path.join(project_path, 'data')
universities_file = os.path.join(data_folder, 'universities.csv')
faculties_file = os.path.join(data_folder, 'faculties.csv')
countries_file = os.path.join(data_folder, 'countries.csv')
cities_file = os.path.join(data_folder, 'cities.csv')
output_file = os.path.join(data_folder, 'combined_data.csv')

# Создаём папку для хранения данных, если её нет
os.makedirs(data_folder, exist_ok=True)

# Сохраняем вспомогательные таблицы в отдельные файлы CSV
universities.to_csv(universities_file, index=False)
print("Файл universities.csv сохранён")
faculties.to_csv(faculties_file, index=False)
print("Файл faculties.csv сохранён")
countries.to_csv(countries_file, index=False)
print("Файл countries.csv сохранён")
cities.to_csv(cities_file, index=False)
print("Файл cities.csv сохранён")

# Удаляем вспомогательные столбцы из исходного DataFrame
data.drop(['university_name', 'faculty_name', 'country_title', 'city_title'], axis=1, inplace=True)

# Сохраняем DataFrame в файл CSV
data.to_csv(output_file, index=False)
print("Файл combined_data.csv сохранён")