import streamlit as st
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Задание широкоформатного режима страницы и указание заголовка
st.set_page_config(layout="wide", page_title="UniGoTo", page_icon=":ai:")

# Построение верхнего уровня визуализации
row1_1, row1_2, row1_3 = st.columns((2, 4, 1))

with row1_1:
        st.header("UniGoTo")
        st.write("Рекомендательный сервис ВУЗов и специальностей на основе технологии Искусственного Интеллекта.")

with row1_2:
        st.header("Las Teteras Desesperadas")
        st.write("""
                 Рекомендательная система использует разреженную матрицу TF-IDF для преобразования строк 
                 интересов пользователей и алгоритм косинусного сходства для вычисления схожести их интересов.
                 """)
with row1_3:
        st.image("Las_Teteras_Desesperadas.jpg", width=150)
        
# Построение второго уровня визуализации
@st.cache_resource   # Функция декоратора для хранения одноэлементных объектов
def load_data(file_name):     # предназначенная для избежания повторного пересчета
        data = pd.read_csv(file_name)
        return data

# Задаём список имён файлов для загрузки
files_to_process = ['./data/universities_filtered.zip',
                    './data/faculties_filtered.zip',
                    './data/countries_filtered.zip',
                    './data/cities_filtered.zip',
                    './data/cities_regions.zip']
dfs = {}  # Используем словарь для хранения DataFrame

# Загружаем файлы CSV в DataFrame
for file_name, idx in zip(files_to_process, range(len(files_to_process))):
        dfs[idx] = load_data(file_name)

data = load_data("./data/preprocessed_data.zip")

# Обрабатываем пропущенные значения в столбце 'preprocessed_interests'
data['preprocessed_interests'].fillna('', inplace=True)

# Выводим считанный DataFrame
st.write(data)

# Задаём словари интересов
user_interests = []
interest_col = ['О себе', 'Сфера деятельности', 'Любимые книги', 'Любимые игры', 'Интересы и хобби']

# Построение второго уровня визуализации
with st.form("interests_form"):  # СОбираем интересы пользователя
        st.write("Введите ваши данные и предпочтения (на русском языке, строчными буквами, без знаков препинания).")
        input0 = st.text_input('О себе', 'человек')
        input1 = st.text_input('Сфера деятельности', 'студент')
        input2 = st.text_input('Любимые книги', 'учебники')
        input3 = st.text_input('Любимые игры', 'стратегии')
        input4 = st.text_input('Интересы и хобби', 'спорт')
        submitted = st.form_submit_button("Отправить")
        
        if submitted:
                user_interests.append(input0)
                user_interests.append(input1)
                user_interests.append(input2)
                user_interests.append(input3)
                user_interests.append(input4)

# Создаём DataFrame с введёнными данными пользователя
user_data = pd.DataFrame([user_interests], columns=interest_col)

# Обрабатываем пропущенные значения в столбцах 'interests'
user_data = user_data.fillna('')

# Объединяем все строки интересов пользователя
user_data['preprocessed_interests'] = user_data.apply(lambda row: ' '.join(row), axis=1)

# Обрабатываем пропущенные значения в столбце 'preprocessed_interests'
user_data['preprocessed_interests'].fillna('', inplace=True)

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
        st.write(f"Пользователь {idx}:  "
            f"cos сходство {similarity},  "
            f"{similar_university_name},  "
            f"{similar_faculty_name}")

# Вывод ТОП-20 предпочтений пользователей
st.subheader("ТОП-20 рекомендованных ВУЗов на основе предпочтений других пользователей:")
recommendation_output(top_indices, user_cosine_sim)
