import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Індекси областей
regions = {
    1: "Черкаська", 2: "Чернігівська", 3: "Чернівецька", 4: "АР Крим", 5: "Дніпропетровська", 6: "Донецька", 7: "Івано-Франківська", 8: "Харківська",
    9: "Херсонська", 10: "Хмельницька", 11: "Київська", 12: "м. Київ", 13: "Кіровоградська", 14: "Луганська", 15: "Львівська", 16: "Миколаївська",
    17: "Одеська", 18: "Полтавська", 19: "Рівненська", 20: "м. Севастополь", 21: "Сумська", 22: "Тернопільська", 23: "Закарпатська", 24: "Вінницька",
    25: "Волинська", 26: "Запорізька", 27: "Житомирська"
}

# Дефолтні значення
default_values = {
    'min_week': 1, 'max_week': 52, 'min_year': 1982, 'max_year': 2024, 'slider_week': (1,52),'slider_year': (1982, 2024),
    'sort_ascending': True, 'sort_descending': False,  'set': 'vci', 'region': 'Черкаська'
}

# Завантаження даних
df = pd.read_csv('df/whole_df.csv', index_col=False)

# Фільтрація даних
def data_filter(min_week, max_week, min_year, max_year, set, region, sort_ascending, sort_descending):
    # Визначення регіону
    reg = [k for k, v in regions.items() if v == region][0]
    # Фільтр обраного регіону
    selected_df = df[(df['year'] >= min_year) & (df['year'] <= max_year) & (df['week'] >= min_week) & (df['week'] <= max_week) & (df['region'] == reg)]
    selected_df = selected_df[['year','week',set]]

    # Фільтр інших регіонів
    other_df = df[(df['year'] >= min_year) & (df['year'] <= max_year) & (df['week'] >= min_week) & (df['week'] <= max_week) & (df['region'] != reg)]
    other_df = other_df[['year','week',set]]
    avg_df = other_df.groupby(['year','week'], as_index=False)[set].mean()

    # Побудова графіків
    graph1, ax1 = plt.subplots(figsize=(10, 4))
    sns.lineplot(data=selected_df, x="year", y=set, ax=ax1, label='Ваша обрана область')

    graph2, ax2 = plt.subplots(figsize=(10, 4))
    sns.lineplot(data=selected_df, x="year", y=set, ax=ax2, label='Ваша обрана область')
    sns.lineplot(data=avg_df, x="year", y=set, ax=ax2, label='Решта')

    # Сортування даних
    if sort_ascending and not sort_descending:
        table = selected_df.sort_values(by=[set])
    elif not sort_ascending and sort_descending:
        table = selected_df.sort_values(by=[set], ascending=False)
    else:
        table = selected_df

    return table, graph1, graph2

for k, v in default_values.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Оновлення чисел
def nums_upd(value):
    st.session_state[f'min_{value}'] = st.session_state[f'slider_{value}'][0]
    st.session_state[f'max_{value}'] = st.session_state[f'slider_{value}'][1]

# Оновлення чекбоксів із сортуванням
def checkboxes(value):
    cb = ['sort_ascending', 'sort_descending']
    cb.remove(value)
    rest_value = cb[0]

    if st.session_state[value]:
        st.session_state[rest_value] = False

st.markdown(
    """
    <style>
        .block-container {
            max-width: 90%;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

col2, _, col1 = st.columns([3, 1, 10])

with col1:
    tab1, tab2, tab3 = st.tabs(["Таблиця", "Графік", "Графік порівняння даних"])

    min_week = st.session_state['min_week']
    max_week = st.session_state['max_week']
    min_year = st.session_state['min_year']
    max_year = st.session_state['max_year']
    set = st.session_state['set']
    region = st.session_state['region']
    sort_ascending = st.session_state['sort_ascending']
    sort_descending = st.session_state['sort_descending']

    table, graph1, graph2 = data_filter(min_week, max_week, min_year, max_year, set, region, sort_ascending, sort_descending)

    with tab1:
        st.write(table)
    with tab2:
        st.pyplot(graph1)
    with tab3:
        st.pyplot(graph2)

with col2:
    # Випадаючи списки
    col2_1, col2_2 = col2.columns([2, 3])
    col2_1.selectbox('Оберіть індекс', ('vci', 'tci', 'vhi'), key='set')
    col2_2.selectbox('Оберіть область', regions.values(), key='region')

    # Слайдер для тижнів
    st.markdown("<hr>" '<b>Оберіть тижні</b>', unsafe_allow_html=True)
    slider_week = st.slider(" ", min_value=1, max_value=52, key='slider_week', on_change=nums_upd, args=('week',))

    # Слайдер для років
    st.markdown("<hr>" '<b>Оберіть роки</b>', unsafe_allow_html=True)
    slider_year = st.slider(" ", min_value=1982, max_value=2024, key='slider_year', on_change = nums_upd, args = ('year',))

    # Режим сортування
    st.markdown("<hr>" '<b>Сортувати за:</b>', unsafe_allow_html=True)
    st.checkbox('Зростанням', key='sort_ascending', on_change=checkboxes, args=('sort_ascending',))
    st.checkbox('Спаданням', key='sort_descending', on_change=checkboxes, args=('sort_descending',))

    # Скидання фільтрів
    st.markdown("<br>", unsafe_allow_html=True)
    def reset_filters():
        for key in default_values:
            st.session_state.pop(key, None)

    st.button("Очистити фільтри", on_click=reset_filters)