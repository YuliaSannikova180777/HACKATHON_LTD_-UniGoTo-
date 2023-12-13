import streamlit as st  # - фреймворк для развертывания моделей и визуализаций


# Задание широкоформатного режима страницы и указание заголовка
st.set_page_config(layout="wide", page_title="UniGoTo", page_icon=":ai:")

with row1_1:
    st.title("UniGoTo")

with row1_2:
    st.write(
        """
    ##
    Рекомендательный сервис ВУЗов и специальностей на основе технологии Искусственного Интеллекта.
    """
    )
