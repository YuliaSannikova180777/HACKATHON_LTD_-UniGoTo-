import os
import re
import nltk
import zipfile
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Проверяем наличие необходимых ресурсов NLTK перед их загрузкой
try:
    nltk.data.find('punkt')
    nltk.data.find('stopwords')
    nltk.data.find('wordnet')
# Загружаем необходимые ресурсы для обработки
# текстовых данных из Natural Language Toolkit
except LookupError:
    nltk.download('punkt')  # токенизатор 
    nltk.download('stopwords')  # список стоп-слов
    nltk.download('wordnet')  # модуль для лемматизации

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
interest_col = ['about', 'activities', 'books', 'games', 'interests']
interest_col_input = ['О себе', 'Сфера деятельности', 'Любимые книги', 'Любимые игры', 'Интересы и хобби']

# Функция предобработки текстовых данных
def preprocess_text(text):
    # Токенизируем текст на отдельные слова
    tokens = word_tokenize(text)
    
    # Задаём стоп-слова для русского и английского языков
    # (общие слова, не несущие смысловой нагрузки в контексте анализа)
    stop_words_ru = set(stopwords.words('russian'))
    stop_words_en = set(stopwords.words('english'))
    
    # Объединяем стоп-слова
    stop_words = stop_words_ru.union(stop_words_en)
    
    # Удаляем стоп-слова
    tokens = [word for word in tokens if word not in stop_words]
    
    # Инициализируем лемматизатор
    lemmatizer = WordNetLemmatizer()
    
    # Лемматизируем слова (приводим к их базовой форме - лемме)
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return ' '.join(tokens)

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

# Загружаем интересы пользователя
load_interest = input("\nЗагрузить интересы пользователя (да/нет)?\t").lower()

# Проверяем ответ
while load_interest not in ['да', 'нет']:
    load_interest = input('Уточните ответ: "да" или "нет"?\t').lower()
if load_interest == 'да':
    user_data = pd.read_csv(output_path)
elif load_interest == 'нет':
    # Запрашиваем интересы пользователя
    print("Введите ваши данные и предпочтения:")

    # Собираем интересы пользователя
    for col in interest_col_input:
        user_interests.append(input(f"{col}: "))

    # Создаём DataFrame с введёнными данными пользователя
    user_data = pd.DataFrame([user_interests], columns=interest_col)

    # Обрабатываем пропущенные значения в столбцах 'interests'
    user_data.fillna('', inplace=True)

    # Применяем функцию очистки к интересам
    user_data.loc[:, interest_col] = user_data[interest_col].apply(lambda x: x.map(clean_text) if x.name in interest_col else x)

    # Объединяем все строки интересов пользователя
    user_data['preprocessed_interests'] = user_data.apply(lambda row: ' '.join(row), axis=1)

    # Применяем функцию предобработки текста
    user_data['preprocessed_interests'] = preprocess_text(user_data['preprocessed_interests'])

    print("\nВаши данные:\n", user_data['preprocessed_interests'].values)  # Вывод данных пользователя

    # Сохраняем данные пользователя в файл CSV
    user_data.to_csv(output_path, index=False)
    print(f"\nФайл {output_file} сохранён")

# Создаём разреженную матрицу TF-IDF для преобразования строк интересов пользователей
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = csr_matrix(tfidf_vectorizer.fit_transform(data['preprocessed_interests']))

# Создаём разреженную матрицу TF-IDF для преобразования строк интересов пользователя
user_tfidf_matrix = tfidf_vectorizer.transform(user_data['preprocessed_interests'])

# Вычисляем косинусное сходство интересов пользователя и других пользователей
user_cosine_sim = cosine_similarity(user_tfidf_matrix, tfidf_matrix)

# Получаем ТОП-20 индексов пользователей с наибольшими косинусными сходствами
top_indices = user_cosine_sim.argsort()[0][-21:-1][::-1]

# Функция вывода рекомендаций
def recommendation_output(top_indices, user_cosine_sim):
    for i, idx in enumerate(top_indices[:20]):
        similarity = round(user_cosine_sim[0][idx], 4)
        similar_university_id = data.loc[idx, 'university']
        similar_university_name = dfs[0].loc[dfs[0]['university'] == similar_university_id, 'university_name'].values[0]
        similar_faculty_id = data.loc[idx, 'faculty']
        similar_faculty_name = dfs[1].loc[dfs[1]['faculty'] == similar_faculty_id, 'faculty_name'].values[0]
        # similar_country_id = data.loc[idx, 'country_id']
        # similar_country_name = dfs[2].loc[dfs[2]['country_id'] == similar_country_id, 'country_title'].values[0]
        # similar_city_id = data.loc[idx, 'city_id']
        # similar_city_name = dfs[3].loc[dfs[3]['city_id'] == similar_city_id, 'city_title'].values[0]
        print(f"{i+1}) {similar_university_name},  "
            f"{similar_faculty_name},  "
            f"сходство {similarity}")

# Вывод ТОП-20 предпочтений пользователей
print("\nТОП-20 рекомендованных ВУЗов:")

# Применяем функцию вывода рекомендаций
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
        print(f"\nТОП-20 рекомендованных ВУЗов для региона {user_region}:")

        # Применяем функцию вывода рекомендаций
        recommendation_output(top_indices_from_region, user_cosine_sim_from_region)
        print('\nСпасибо за использование наших рекомендаций!')  # Благодарность
elif answer == 'нет':
    print('Спасибо за использование наших рекомендаций!')  # Благодарность
