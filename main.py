import streamlit as st
from pages import form_page, reports_page

st.set_page_config(page_title="Прокат оборудования", layout="wide")

st.title("Система аренды оборудования")

page = st.sidebar.selectbox("Перейти на страницу", ["Оформить заявку", "Заявки и отчеты"])

if page == "Оформить заявку":
    form_page.show()
elif page == "Заявки и отчеты":
    reports_page.show()
