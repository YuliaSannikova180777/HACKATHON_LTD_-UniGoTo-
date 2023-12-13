import streamlit as st
import time
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Задание широкоформатного режима страницы и указание заголовка
st.set_page_config(layout="wide", page_title="UniGoTo", page_icon=":student:")

st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)

# Построение верхнего уровня визуализации
row1_1, row1_2, row1_3 = st.columns((3.6, 6, 1))
with row1_1:
        st.title("UniGoTo")
        st.write("Рекомендательный сервис ВУЗов и специальностей на основе технологии Искусственного Интеллекта.")
with row1_2:
        st.title(":gray[Las Teteras Desesperadas]")
        st.write("""
                 :gray[Рекомендательная система использует разреженную матрицу TF-IDF для преобразования строк 
                 интересов пользователей и алгоритм косинусного сходства для вычисления схожести их интересов.]
                 """)
with row1_3:
        st.image("Las_Teteras_Desesperadas.jpg", width=100)
        
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

data = load_data("C:/ML/Hackathon2/data/preprocessed_data.csv")

# Обрабатываем пропущенные значения в столбце 'preprocessed_interests'
data['preprocessed_interests'].fillna('', inplace=True)

# Функция вывода рекомендаций
def recommendation_output(top_indices, user_cosine_sim):
    for i, idx in enumerate(top_indices[:20]):
        similarity = round(user_cosine_sim[0][idx], 4)
        similar_university_id = data.loc[idx, 'university']
        similar_university_name = dfs[0].loc[dfs[0]['university'] == similar_university_id, 'university_name'].values[0]
        similar_faculty_id = data.loc[idx, 'faculty']
        similar_faculty_name = dfs[1].loc[dfs[1]['faculty'] == similar_faculty_id, 'faculty_name'].values[0]

        col1, col2, col3 = st.columns([2, 2, 1])         
        with col1:
                st.write(f"{i+1}\) {similar_university_name}")
        with col2:
                st.write(f"{similar_faculty_name}")
        with col3:
                st.write(f"{similarity}")
        
# Задаём словари интересов
user_interests = []
interest_col = ['О себе', 'Сфера деятельности', 'Любимые книги', 'Любимые игры', 'Интересы и хобби']

# Построение второго уровня визуализации
row2_1, row2_2 = st.columns((1, 2))

with row2_1:
        with st.form("interests_form"):  # Собираем интересы пользователя
                st.write("**Введите ваши данные и предпочтения** (строчными буквами, без знаков препинания).")
                
                input_0 = st.text_input("О себе", "просто хороший человек")
                input_1 = st.text_input("Сфера деятельности", "гуманитарий")
                input_2 = st.text_input("Любимые книги", "мастер и маргарита")
                input_3 = st.text_input("Любимые игры", "тетрис цивилизация")
                input_4 = st.text_input("Интересы и хобби", "путешествия развлечения")
                
                submitted_1 = st.form_submit_button("Отправить")

                if submitted_1:
                        user_interests.append(input_0)
                        user_interests.append(input_1)
                        user_interests.append(input_2)
                        user_interests.append(input_3)
                        user_interests.append(input_4)

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

                else:
                        st.stop()

        st.write("Ваши данные:", user_interests)  # Вывод данных

with row2_2:
        with st.form("recommendations_form"):  # Вывод ТОП-20 предпочтений пользователей
                progress_text = "Подбираем рекомендации. Подождите..."
                my_bar = st.progress(0, text=progress_text)
                for percent_complete in range(100):
                        time.sleep(0.005)
                        my_bar.progress(percent_complete + 1, text=progress_text)
                my_bar.empty()
                st.header("ТОП-20 рекомендованных ВУЗов:")
                col1, col2, col3 = st.columns([2, 2, 1])
                col1.subheader("ВУЗ")
                col2.subheader("Факультет")
                col3.subheader("Сходство")
                recommendation_output(top_indices, user_cosine_sim)
                submitted_1 = st.form_submit_button("Спасибо!", disabled=True)
