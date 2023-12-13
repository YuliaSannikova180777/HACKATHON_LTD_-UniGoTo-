from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import zipfile
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

class UserData(BaseModel):
    about: str
    activity_field: str
    favorite_books: str
    favorite_games: str
    hobbies: str

def load_data():
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

    def process_user_data(user_interests):
        
        # Преобразование интересов пользователя в TF-IDF вектор
        tfidf_vectorizer = TfidfVectorizer()
        user_tfidf_vector = tfidf_vectorizer.fit_transform([user_interests])
        
        # Преобразование в разреженную матрицу
        user_tfidf_matrix = csr_matrix(user_tfidf_vector)
        
        return user_tfidf_matrix

    def get_recommendations(user_cosine_sim, data, dfs):
        # Получаем индексы пользователей с наивысшим сходством
        top_indices = user_cosine_sim.argsort()[0][-21:-1][::-1]

        # Выводим рекомендации для каждого из ТОП-20 пользователей
        for idx in top_indices:
            # Получаем значение сходства
            similarity = round(user_cosine_sim[0][idx], 4)

            # Получаем информацию о рекомендованном университете
            similar_university_id = data.loc[idx, 'university']
            similar_university_name = dfs[0].loc[dfs[0]['university'] == similar_university_id, 'university_name'].values[0]
            
            # Получаем информацию о рекомендованном факультете
            similar_faculty_id = data.loc[idx, 'faculty']
            similar_faculty_name = dfs[1].loc[dfs[1]['faculty'] == similar_faculty_id, 'faculty_name'].values[0]

            # Выводим рекомендацию
            print(f"Пользователь {idx}:  "
                f"cos сходство {similarity},  "
                f"{similar_university_name},  "
                f"{similar_faculty_name}")

    @app.post("/recommendations/")
    def get_user_recommendations(user_data: UserData, include_location: bool = False):
        load_interest = input("\nLoad user interests (yes/no)?\t").lower()

        if load_interest == 'yes':
            user_data = process_user_data(pd.read_csv(output_path))
        elif load_interest == 'no':
            user_data = process_user_data(pd.DataFrame([user_data.dict()]))

        tfidf_matrix = load_data()  # Загрузка TF-IDF матрицы
        user_tfidf_matrix = process_user_data(user_data)  # Обработка данных пользователя

        user_cosine_sim = cosine_similarity(user_tfidf_matrix, tfidf_matrix)

        top_indices = user_cosine_sim.argsort()[0][-21:-1][::-1]

        recommendations = []
        for idx in top_indices:
            similarity = round(user_cosine_sim[0][idx], 4)
            similar_university_id = data.loc[idx, 'university']
            similar_university_name = dfs[0].loc[dfs[0]['university'] == similar_university_id, 'university_name'].values[0]
            similar_faculty_id = data.loc[idx, 'faculty']
            similar_faculty_name = dfs[1].loc[dfs[1]['faculty'] == similar_faculty_id, 'faculty_name'].values[0]
            recommendations.append({
                "user_id": idx,
                "similarity": similarity,
                "university_name": similar_university_name,
                "faculty_name": similar_faculty_name
            })

        if include_location:
            # Добавьте код для обработки местоположения пользователя и рекомендаций на основе этого местоположения
            pass

        return {"recommendations": recommendations}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)