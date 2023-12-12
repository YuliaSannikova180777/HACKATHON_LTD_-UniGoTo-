import os
import zipfile
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Получаем путь к текущей папке скриптов src/
current_dir = os.path.dirname(os.path.abspath(__file__))  # для .py
# current_dir = os.getcwd()  # для .ipynb

# Находим папку проекта относительно папки src/
project_path = os.path.abspath(os.path.join(current_dir, os.pardir))
print(f"Путь к папке проекта '{project_path}'")

# Задаём путь к папке данных относительно папки проекта
data_folder = os.path.join(project_path, 'data')

# Задаём пути и имена файлов для сохранения результатов
input_file = 'preprocessed_data.csv'
input_zip_path = os.path.join(data_folder, input_file[:-4] + '.zip')
input_csv_path = os.path.join(data_folder, input_file)
output_file = 'user_data.csv'
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

# Задаём список имён файлов для загрузки
files_to_process = ['universities_filtered.csv', 'faculties_filtered.csv', 'countries_filtered.csv', 'cities_filtered.csv', 'cities_regions.csv']
dfs = {}  # Используем словарь для хранения DataFrame

for file_name, idx in zip(files_to_process, range(len(files_to_process))):
    # Пути к архиву и файлу для загрузки и сохранения
    input_zip_path = os.path.join(data_folder, file_name[:-4] + '.zip')
    input_csv_path = os.path.join(data_folder, file_name)

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
    dfs[idx] = pd.read_csv(input_file_path)

# Обрабатываем пропущенные значения в столбце 'preprocessed_interests'
data['preprocessed_interests'].fillna('', inplace=True)

# Задаём словари интересов
user_interests = []
interest_col = ['О себе', 'Сфера деятельности', 'Любимые книги', 'Любимые игры', 'Интересы и хобби']

# Загружаем интересы пользователя
load_interest = input("\nЗагрузить интересы пользователя (да/нет)?\t").lower()

# Проверяем ответ
while load_interest not in ['да', 'нет']:
    load_interest = input('Уточните ответ: "да" или "нет"?\t').lower()
if load_interest == 'да':
    user_data = pd.read_csv(output_path)
elif load_interest == 'нет':
    # Запрашиваем интересы пользователя
    print("Введите ваши данные и предпочтения (на русском языке, можно без точек и запятых).")

    # Собираем интересы пользователя
    for col in interest_col:
        user_interests.append(input(f"Введите информацию '{col}': "))

    # Создаём DataFrame с введёнными данными пользователя
    user_data = pd.DataFrame([user_interests], columns=interest_col)

    # Обрабатываем пропущенные значения в столбцах 'interests'
    user_data = user_data.fillna('')

    # Объединяем все строки интересов пользователя
    user_data['preprocessed_interests'] = user_data.apply(lambda row: ' '.join(row), axis=1)

    # Обрабатываем пропущенные значения в столбце 'preprocessed_interests'
    user_data['preprocessed_interests'].fillna('', inplace=True)

    # Сохраняем данные пользователя в файл CSV
    user_data.to_csv(output_path, index=False)
    print(f"Файл {output_file} сохранён")

# Создаём разреженную матрицу TF-IDF для преобразования строк интересов пользователей
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = csr_matrix(tfidf_vectorizer.fit_transform(data['preprocessed_interests']))

# Создаём разреженную матрицу TF-IDF для преобразования строк интересов пользователей
user_tfidf_matrix = tfidf_vectorizer.transform(user_data['preprocessed_interests'])

# Вычисляем косинусное сходство пользователя с другими пользователями
user_cosine_sim = cosine_similarity(user_tfidf_matrix, tfidf_matrix)

# Получаем ТОП-20 индексов пользователей с наибольшими косинусными сходствами
top_indices = user_cosine_sim.argsort()[0][-21:-1][::-1]

# Функция вывода рекомендаций
def recommendation_output(top_indices, user_cosine_sim):
    for idx in top_indices:
        similarity = round(user_cosine_sim[0][idx], 4)
        similar_university_id = data.loc[idx, 'university']
        similar_university_name = dfs[0].loc[dfs[0]['university'] == similar_university_id, 'university_name'].values[0]
        similar_faculty_id = data.loc[idx, 'faculty']
        similar_faculty_name = dfs[1].loc[dfs[1]['faculty'] == similar_faculty_id, 'faculty_name'].values[0]
        # similar_country_id = data.loc[idx, 'country_id']
        # similar_country_name = dfs[2].loc[dfs[2]['country_id'] == similar_country_id, 'country_title'].values[0]
        # similar_city_id = data.loc[idx, 'city_id']
        # similar_city_name = dfs[3].loc[dfs[3]['city_id'] == similar_city_id, 'city_title'].values[0]
        print(f"Пользователь {idx}:  "
            f"cos сходство {similarity},  "
            f"{similar_university_name},  "
            f"{similar_faculty_name}")

# Вывод ТОП-20 предпочтений пользователей
print("\nТОП-20 рекомендованных ВУЗов на основе предпочтений других пользователей:")
recommendation_output(top_indices, user_cosine_sim)

# Запрашиваем желание пользователя ввести его город
answer = input("\nХотите ли вы получить рекомендации на основе вашего места жительства (да/нет)?\t").lower()

# Проверяем ответ
while answer not in ['да', 'нет']:
    answer = input('Уточните ответ: "да" или "нет"?\t').lower()
if answer == 'да':
    while True:  # Получаем название города пользователя
        user_city = input("Введите ваш город: ").capitalize()

        # Проверяем соответствие введённого названия городам в 'regions'
        if user_city.lower() not in dfs[4]['city_title'].str.lower().values:
            print("Город не найден! Проверьте правильность ввода или укажите ближайший крупный город.")
        else:  # Выходим из цикла
            break

    user_city = user_city.lower()

    # Получаем регион пользователя
    user_region = dfs[4].loc[dfs[4]['city_title'].str.lower() == user_city, 'region'].values[0]

    # Получаем все города из региона пользователя
    cities_in_region = dfs[4].loc[dfs[4]['region'] == user_region, 'city_id'].values

    # ПРоверяем, не пуст ли список городов
    print(cities_in_region)

    # Фильтруем данные по пользователям из того же региона
    users_from_region = data[data['city_id'].isin(cities_in_region)]

    # Если пользователей из региона нет, выдаем предупреждение
    if users_from_region.empty:
        print(f"Нет пользователей из региона {user_region}!")
    else:
        # Создаём разреженную матрицу TF-IDF для пользователей из региона
        tfidf_matrix_from_region = csr_matrix(tfidf_vectorizer.transform(users_from_region['preprocessed_interests']))

        # Вычисляем косинусное сходство пользователя с другими пользователями из его региона
        user_cosine_sim_from_region = cosine_similarity(user_tfidf_matrix, tfidf_matrix_from_region)

        # Получаем ТОП-20 индексов пользователей из этого региона
        top_indices_from_region = user_cosine_sim_from_region.argsort()[0][-21:-1][::-1]

        # Вывод ТОП-20 предпочтений пользователей из этого региона
        print(f"\nТОП-20 рекомендованных ВУЗов на основе предпочтений других пользователей из региона {user_region}:")
        recommendation_output(top_indices_from_region, user_cosine_sim_from_region)
elif answer == 'нет':
    print('Спасибо за использование наших рекомендаций!')  # Благодарность
