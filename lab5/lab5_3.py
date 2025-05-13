import dash
from dash import dcc, html, Input, Output
import numpy as np
import plotly.graph_objs as go

time = np.linspace(0, 1, 500)
noise_data = np.zeros_like(time)
noise_generated = False

def moving_average(signal, value_range):  # функція фільтрації через ковзне середнє
    filtered = np.zeros_like(signal) # створюємо масив для збереження фільтрованих значень
    half_range = value_range // 2  # визначаємо діапазон для кожної точки.
    for i in range(len(signal)):
        start = max(0, i - half_range)
        end = min(len(signal), i + half_range + 1)
        filtered[i] = np.mean(signal[start:end]) # обчислюємо середнє значення діапазону
    return filtered

def createSlider(id, min_val, max_val, step, val, label): # функція для створення слайдера
    return html.Div([
        html.Label(label),
        dcc.Slider(
            id=id,
            min=min_val,
            max=max_val,
            step=step,
            value=val,
            marks={round(min_val, 2): str(round(min_val, 2)), round(max_val, 2): str(round(max_val, 2))},
            tooltip={"placement": "top", "always_visible": True}
        )
    ])

# ініціалізуємо наш додаток
app = dash.Dash(__name__)

# створюємо інтерфейс
app.layout = html.Div([
    dcc.Graph(id='signal-graph'), # основний графік

    html.Div([ # параметри слайдерів
        createSlider('amp', 0.1, 5, 0.1, 2, 'Амплітуда'),
        createSlider('freq', 1, 10, 0.1, 5, 'Частота'),
        createSlider('phase', 0, 2 * np.pi, 0.1, 0, 'Фаза'),
        createSlider('noise-mean', -2, 2, 0.1, 0.5, 'Середнє шуму'),
        createSlider('noise-cov', 0, 1, 0.01, 0.5, 'Дисперсія шуму'),
        createSlider('cutoff', 0.01, 50, 0.5, 10, 'Частота зрізу'),

        html.Br(),
        html.Label("Що відображати:"),
        dcc.Dropdown(   # Dropdown меню з вибором елементів на графіку
            id='options',
            options=[
                {'label': 'Сигнал', 'value': 'signal'},
                {'label': 'Сигнал + шум', 'value': 'signal_noise'},
                {'label': 'Сигнал + фільтр', 'value': 'signal_filter'},
                {'label': 'Все', 'value': 'signal_noise_filter'},
            ],
            value='signal_noise_filter',
            clearable=False,
            style={'width': '220px'}
        ),
        html.Br(),
        # кнопка скидання
        html.Button('Скинути налаштування', id='reset', n_clicks=0, style={'fontSize': '25px'})
    ], style={'width': '95%', 'display': 'inline-block', 'verticalAlign': 'top'})
], style={'padding': '30px', 'fontSize': '25px'})

# callback для повернення стандартних значеннь, якщо натиснуто кнопку скидання
@app.callback(
    [  # Output() - що функція буде повертати
        Output('amp', 'value'),
        Output('freq', 'value'),
        Output('phase', 'value'),
        Output('noise-mean', 'value'),
        Output('noise-cov', 'value'),
        Output('cutoff', 'value')
    ],
    [Input('reset', 'n_clicks')],
    prevent_initial_call=True # не викликаємо при першому завантаженні
)
def reset_parameters(reset_clicks):
    if reset_clicks > 0:
        return 2, 5, 0, 0.5, 0.5, 10
    return dash.no_update  # якщо кнопка не натискалася, нічого не змінюється

# callback для оновлення графіка
@app.callback(  # Input() - що буде передаватися в функцію
    Output('signal-graph', 'figure'),
    Input('amp', 'value'),
    Input('freq', 'value'),
    Input('phase', 'value'),
    Input('noise-mean', 'value'),
    Input('noise-cov', 'value'),
    Input('cutoff', 'value'),
    Input('options', 'value'),
    prevent_initial_call=False
)
def updatePlot(amplitude, frequency, phase, noise_mean, noise_cov, cutoff, options):
    global noise_data, noise_generated, time
    # формуємо синусоїду
    y = amplitude * np.sin(2 * np.pi * frequency * time + phase)

    ctx = dash.callback_context # визначаємо, який елемент викликав callback
    changed_inputs = [trg['prop_id'].split('.')[0] for trg in ctx.triggered] if ctx.triggered else []

    # генеруємо шум, якщо його не було згенеровано, натиснули кнопку reset або ж змінились його параметри
    if (not noise_generated or 'reset' in changed_inputs or 'noise-mean' in changed_inputs or 'noise-cov' in changed_inputs):
        noise_data = np.random.normal(noise_mean, noise_cov, size=time.shape)
        noise_generated = True

    y_noise = y + noise_data

    # визначаємо діапазон для фільтрації на основі частоти зрізу
    value_range = max(1, int(500 / cutoff))
    filtered = moving_average(y_noise, value_range) # фільтруємо

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time, y=y, mode='lines', name='Сигнал', line=dict(color='blue')))

    # додаємо шум або фільтр залежно від вибору в Dropdown меню
    if options in ['signal_noise', 'signal_noise_filter']:
        fig.add_trace(go.Scatter(x=time, y=y_noise, mode='lines', name='Шум', line=dict(color='orange')))
    if options in ['signal_filter', 'signal_noise_filter']:
        fig.add_trace(go.Scatter(x=time, y=filtered, mode='lines', name='Фільтр', line=dict(color='green')))

    fig.update_layout(height=500, margin=dict(l=50, r=10, t=40, b=40))
    return fig

if __name__ == '__main__':
    app.run(debug=True)