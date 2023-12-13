import streamlit as st
import pandas as pd

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
        
# Построение среднего уровня визуализации
@st.cache_resource   # Функция декоратора для хранения одноэлементных объектов
def load_data():     # предназначенная для избежания повторного пересчета
        data = pd.read_csv("./data/preprocessed_data.zip")
        return data

data = load_data()
st.write(data)

with st.form("interests_form"):
        st.write("Введите ваши данные и предпочтения (на русском языке, можно без точек и запятых).")
        interest1 = st.text_input('О себе', '')
        interest2 = st.text_input('Сфера деятельности', '')
        interest3 = st.text_input('Любимые книги', '')
        interest4 = st.text_input('Любимые игры', '')
        interest5 = st.text_input('Интересы и хобби', '')
        submitted = st.form_submit_button("Отправить")
        
        if submitted:
                interests = st.write(interest1 + ' ' + interest2 + ' ' + interest3 + ' ' + interest4 + ' ' + interest5)
