import streamlit as st
import pandas as pd

# Задание широкоформатного режима страницы и указание заголовка
st.set_page_config(layout="wide", page_title="UniGoTo", page_icon=":ai:")

st.title("UniGoTo")
st.write("Рекомендательный сервис ВУЗов и специальностей на основе технологии Искусственного Интеллекта.")

@st.cache_resource   # Функция декоратора для хранения одноэлементных объектов
def load_data():     # предназначенная для избежания повторного пересчета
    data = pd.read_csv("./data/preprocessed_data.csv")
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
