import streamlit as st
import sqlite3
from datetime import date

def show():
    conn = sqlite3.connect('rental.db')
    c = conn.cursor()
    st.header("Оформление заявки на аренду")
    st.subheader("Данные клиента")
    name = st.text_input("Имя клиента")
    phone = st.text_input("Телефон")
    st.subheader("Оборудование для аренды")
    equipment_list = c.execute("SELECT id, name, price_per_day, status FROM equipment WHERE status='available'").fetchall()
    if equipment_list:
        options = [f"{name} ({price}₽/день)" for _, name, price, _ in equipment_list]
        idx = st.selectbox("Выберите оборудование", range(len(options)), format_func=lambda x: options[x])
        equipment_id, equipment_name, price_per_day, status = equipment_list[idx]
    else:
        st.error("Нет доступного оборудования для аренды")
        conn.close()
        return
    date_start = st.date_input("Дата начала аренды", date.today())
    date_end = st.date_input("Дата окончания аренды", date.today())
    if date_end >= date_start:
        days = (date_end - date_start).days + 1
        total_price = days * price_per_day
        st.write(f"Стоимость аренды за {days} дн.: {total_price:.2f} ₽")
    else:
        st.error("Дата окончания не может быть раньше даты начала")
        total_price = None
    if st.button("Оформить заявку"):
        if not name:
            st.error("Введите имя клиента")
            return
        if total_price is None:
            st.error("Проверьте даты аренды")
            return
        c.execute("INSERT INTO clients (name, phone) VALUES (?, ?)", (name, phone))
        client_id = c.lastrowid
        c.execute("UPDATE equipment SET status='rented' WHERE id=?", (equipment_id,))
        c.execute(
            "INSERT INTO requests (client_id, equipment_id, date_start, date_end, status) VALUES (?, ?, ?, ?, 'active')",
            (client_id, equipment_id, str(date_start), str(date_end))
        )

        conn.commit()
        st.success(f"Заявка оформлена. Итоговая стоимость: {total_price:.2f} ₽")
    conn.close()
