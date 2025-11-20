import streamlit as st
import sqlite3
import pandas as pd

def get_requests(conn):
    return pd.read_sql_query("""
        SELECT r.id AS request_id, c.name AS client, e.name AS equipment, e.price_per_day,
               r.date_start, r.date_end, r.status, r.equipment_id
        FROM requests r
        JOIN clients c ON r.client_id = c.id
        JOIN equipment e ON r.equipment_id = e.id
        ORDER BY r.date_start DESC
    """, conn)

def get_equipment(conn):
    return pd.read_sql_query("SELECT id, name, price_per_day, status FROM equipment ORDER BY name", conn)

def get_olap(conn):
    return pd.read_sql_query("""
        SELECT date_start, COUNT(*) AS total_requests
        FROM requests
        GROUP BY date_start
        ORDER BY date_start
    """, conn)

def show():
    conn = sqlite3.connect('rental.db')
    c = conn.cursor()

    st.header("Текущие заявки")
    requests_df = get_requests(conn)

    if requests_df.empty:
        st.info("Заявок пока нет.")
        conn.close()
        return
    else:
        st.dataframe(requests_df[['request_id', 'client', 'equipment', 'date_start', 'date_end', 'status']])

    st.header("Управление заявкой")
    request_ids = requests_df['request_id'].tolist()
    selected_id = st.selectbox("Выберите заявку", request_ids)

    selected_request = requests_df[requests_df['request_id'] == selected_id].iloc[0]
    equipment_id = selected_request['equipment_id']
    status_options = ['active', 'closed', 'extended']
    new_status = st.selectbox("Изменить статус заявки", status_options, index=status_options.index(selected_request['status']))

    if st.button("Обновить статус заявки"):
        c.execute("UPDATE requests SET status=? WHERE id=?", (new_status, selected_id))
        if new_status == 'closed':
            c.execute("UPDATE equipment SET status='available' WHERE id=?", (equipment_id,))
        else:
            c.execute("UPDATE equipment SET status='rented' WHERE id=?", (equipment_id,))
        conn.commit()
        st.success("Статус заявки и оборудования обновлены. Чтобы увидеть изменения в таблице, обновите страницу.")

    st.subheader("Удалить заявку")
    if st.button("Удалить заявку"):
        c.execute("SELECT equipment_id FROM requests WHERE id=?", (selected_id,))
        equipment = c.fetchone()
        if equipment:
            equipment_id = equipment[0]
            c.execute("UPDATE equipment SET status='available' WHERE id=?", (equipment_id,))
        c.execute("DELETE FROM requests WHERE id=?", (selected_id,))
        conn.commit()
        st.success("Заявка удалена и оборудование освобождено. Чтобы увидеть изменения в таблице, обновите страницу.")

    st.header("Статус оборудования")
    equipment_df = get_equipment(conn)
    st.dataframe(equipment_df)

    st.header("OLAP-анализ заявок")
    olap_df = get_olap(conn)
    if olap_df.empty:
        st.write("Данных для OLAP-анализа пока нет.")
    else:
        olap_df['date_start'] = pd.to_datetime(olap_df['date_start'])
        olap_df.set_index('date_start', inplace=True)
        st.bar_chart(olap_df['total_requests'])

    conn.close()
