import pandas as pd
import re
import streamlit as st
import time
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Задание широкоформатного режима страницы и указание заголовка
st.set_page_config(layout="wide", page_title="UniGoTo", page_icon=":student:")

st.markdown("""
    <style>
        .reportview-container {margin-top: -2em;}
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)  # Убираем меню Streamlit

# Построение верхнего уровня визуализации
col1_1, col1_2, col1_3 = st.columns((3.6, 6, 1))  # Задаём пропорции колонок
with col1_1:  # Левая колонка
        st.title("UniGoTo")
        st.write("Рекомендательный сервис ВУЗов и специальностей на основе технологии Искусственного Интеллекта.")
with col1_2:  # Средняя колонка
        st.title(":gray[Las Teteras Desesperadas]")
        st.write("""
                 :gray[Рекомендательная система использует разреженную матрицу TF-IDF для преобразования строк 
                 интересов пользователей и алгоритм косинусного сходства для вычисления схожести их интересов.]
                 """)
with col1_3:  # Правая колонка
        st.image("Las_Teteras_Desesperadas.jpg", width=100)

@st.cache_resource  # Функция декоратора для хранения одноэлементных объектов
def load_data(file_name):  # предназначенная для избежания повторного пересчёта
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

# Функция вывода рекомендаций
def recommendation_output(top_indices, user_cosine_sim):
    for i, idx in enumerate(top_indices[:20]):
        similarity = round(user_cosine_sim[0][idx], 4)
        similar_university_id = data.loc[idx, 'university']
        similar_university_name = dfs[0].loc[dfs[0]['university'] == similar_university_id, 'university_name'].values[0]
        similar_faculty_id = data.loc[idx, 'faculty']
        similar_faculty_name = dfs[1].loc[dfs[1]['faculty'] == similar_faculty_id, 'faculty_name'].values[0]

        col1, col2, col3 = st.columns([3, 3, 1])  # Задаём пропорции колонок
        with col1:
                st.write(f"{i+1}\) {similar_university_name}")
        with col2:
                st.write(f"{similar_faculty_name}")
        with col3:
                st.write(f"{similarity}")

# Задаём словари интересов
user_interests = []
interest_col = ['about', 'activities', 'books', 'games', 'interests']
user_city = 'Москва'

# Построение среднего уровня визуализации
col2_1, col2_2 = st.columns((1, 2))  # Задаём пропорции колонок

with col2_1:  # Левая колонка
        # Задаём начальные значения виджетов в session state
        if "city_checkbox" not in st.session_state:
                st.session_state.city_checkbox = True
                st.session_state.text_city = "москва"

        # Переключатель города
        city_check = st.checkbox('Пропустить рекомендации по региону', key="city_checkbox")

        with st.form("interests_form"):  # Запрашиваем интересы пользователя
                st.write("**Введите ваши данные и предпочтения:**")
                input_0 = st.text_input("О себе", "Умный, оптимист")
                input_1 = st.text_input("Сфера деятельности", "Информатика, программирование")
                input_2 = st.text_input("Любимые книги", "Мастер и Маргарита")
                input_3 = st.text_input("Любимые игры", "Тетрис, Цивилизация")
                input_4 = st.text_input("Интересы и хобби", "Путешествия, развлечения")
                user_city = st.text_input("Ваш город", "", key="text_city", disabled=st.session_state.city_checkbox)

                submitted = st.form_submit_button("Отправить")  # Кнопка
                if submitted:  # Собираем интересы пользователя
                        user_interests.append(input_0)
                        user_interests.append(input_1)
                        user_interests.append(input_2)
                        user_interests.append(input_3)
                        user_interests.append(input_4)

                        # Создаём DataFrame с введёнными данными пользователя
                        user_data = pd.DataFrame([user_interests], columns=interest_col)

                        # Обрабатываем пропущенные значения в столбцах 'interests'
                        user_data.fillna('', inplace=True)

                        # Применяем функцию очистки к интересам
                        user_data.loc[:, interest_col] = user_data[interest_col].apply(lambda x: x.map(clean_text) if x.name in interest_col else x)

                        # Объединяем все строки интересов пользователя
                        user_data['preprocessed_interests'] = user_data.apply(lambda row: ' '.join(row), axis=1)

                        # Создаём разреженную матрицу TF-IDF для преобразования строк интересов пользователей
                        tfidf_vectorizer = TfidfVectorizer()
                        tfidf_matrix = csr_matrix(tfidf_vectorizer.fit_transform(data['preprocessed_interests']))

                        # Создаём разреженную матрицу TF-IDF для преобразования строк интересов пользователя
                        user_tfidf_matrix = tfidf_vectorizer.transform(user_data['preprocessed_interests'])

                        # Вычисляем косинусное сходство интересов пользователя и других пользователей
                        user_cosine_sim = cosine_similarity(user_tfidf_matrix, tfidf_matrix)

                        # Получаем ТОП-20 индексов пользователей с наибольшими косинусными сходствами
                        top_indices = user_cosine_sim.argsort()[0][-21:-1][::-1]

                else:
                        st.stop()  # Ждём нажатия кнопки 'Отправить'

        st.write("Ваши данные:", user_data['preprocessed_interests'].values)  # Вывод данных пользователя
        user_city = user_city.capitalize()
        st.write("Ваш город:", user_city)  # Вывод города пользователя

        # Проверяем соответствие введённого названия городам в 'regions'
        if user_city.lower() not in dfs[4]['city_title'].str.lower().values:
                st.write("Город не найден! Проверьте правильность ввода или укажите ближайший крупный город.")
        else:
                user_city_found = True  # Задаём флаг того, что город найден

with col2_2:  # Правая колонка
        with st.form("recommendations_form"):  # Вывод ТОП-20 предпочтений пользователей
                # Индикатор выполнения
                progress_text = "Подбираем рекомендации. Подождите..."
                my_bar = st.progress(0, text=progress_text)
                for percent_complete in range(100):
                        time.sleep(0.01)
                        my_bar.progress(percent_complete + 1, text=progress_text)
                my_bar.empty()  # Очищаем его

                # Вывод ТОП-20 предпочтений пользователей
                st.header("ТОП-20 рекомендованных ВУЗов:")
                col1, col2, col3 = st.columns([3, 3, 1])  # Задаём пропорции колонок
                col1.subheader("ВУЗ")
                col2.subheader("Факультет")
                col3.subheader("Сходство")

                # Применяем функцию вывода рекомендаций
                recommendation_output(top_indices, user_cosine_sim)
                submitted_1 = st.form_submit_button("Спасибо!", disabled=True)

# Построение нижнего уровня визуализации
if user_city_found:
        user_city = user_city.lower()
        # Получаем регион пользователя
        user_region = dfs[4].loc[dfs[4]['city_title'].str.lower() == user_city, 'region'].values[0]

        # Получаем все города из региона пользователя
        cities_in_region = dfs[4].loc[dfs[4]['region'] == user_region, 'city_id'].values

        # Вывод региона пользователя
        st.write("Ваш регион:", user_region)

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

                col3_1, col3_2 = st.columns((3, 2))  # Задаём пропорции колонок

                with col3_1:  # Левая колонка
                        # Вывод ТОП-20 предпочтений пользователей из этого региона
                        st.header("ТОП-20 рекомендованных ВУЗов для региона")
                with col3_2:  # Правая колонка
                        st.header(user_region)
                
                col1, col2, col3 = st.columns([3, 3, 1])  # Задаём пропорции колонок
                col1.subheader("ВУЗ")
                col2.subheader("Факультет")
                col3.subheader("Сходство")

                # Применяем функцию вывода рекомендаций
                recommendation_output(top_indices_from_region, user_cosine_sim_from_region)
