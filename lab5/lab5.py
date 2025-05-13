import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.widgets import Slider, RangeSlider, Button, CheckButtons
import numpy as np
from scipy.signal import butter, filtfilt

def sidebar(fig, sidebar_grid, redraw): # створюємо панель налаштувань
    axes = {}
    sliders = {}

    grid = sidebar_grid.subgridspec(9, 1)   # розділемо панель на 9 частин

    # 1: чекбокс, який показує шум на графіку
    axes['Показати шум'] = fig.add_subplot(grid[0])
    showNoise = CheckButtons(axes['Показати шум'], ['Показати шум'], [True])
    showNoise.on_clicked(lambda label: redraw(False))

    # 2: чекбокс, який показує фільтр на графіку
    axes['Показати фільтр'] = fig.add_subplot(grid[1])
    showFilter = CheckButtons(axes['Показати фільтр'], ['Показати фільтр'], [True])
    showFilter.on_clicked(lambda label: redraw(False))

    # 3-7: створюємо слайдери для кожного параметра
    params = [  # параметри слайдерів
        ('Амплітуда', (0.1, 5, 2)),
        ('Частота', (1, 10, 5)),
        ('Фаза', (0, 2 * np.pi, 0)),
        ('Середнє шуму', (-2, 2, 0.5)),
        ('Дисперсія шуму', (0, 1, 0.5))
    ]
    for i, (name, (min_val, max_val, def_val)) in enumerate(params, start=2):
        axes[name] = fig.add_subplot(grid[i])
        sliders[name] = Slider(axes[name], name, min_val, max_val, valinit=def_val)
        is_noise = name not in ['Амплітуда', 'Частота', 'Фаза']
        sliders[name].on_changed(lambda val, noise_flag=is_noise: redraw(noise_flag))

    # 8: слайдер частоти зрізу фільтра
    axes['Частота зрізу'] = fig.add_subplot(grid[7])
    sliders['Частота зрізу'] = Slider(axes['Частота зрізу'], 'Частота зрізу', 0.01, 50, valinit=10)
    sliders['Частота зрізу'].on_changed(lambda val: redraw(False))

    # 9: кнопка скидання
    axes['Скинути налаштування'] = fig.add_subplot(grid[8])
    reset_btn = Button(axes['Скинути налаштування'], 'Скинути налаштування')

    # при скиданні повертає всі слайдери до дефолту
    def reset(event):
        for name, slider in sliders.items():
            try:
                slider.reset()
            except AttributeError:
                pass
        redraw(True)

    reset_btn.on_clicked(reset)
    return sliders, showNoise, showFilter, reset_btn

def appWindow():
    fig = plt.figure(figsize=(15, 5))
    main_grid = GridSpec(ncols=2, nrows=1, figure=fig, width_ratios=[3, 2], wspace=0.3)
    ax_plot = fig.add_subplot(main_grid[0, 0])

    # змінні для ліній графіка
    signal_line = noise_line = filtered_line = None
    noise_data = None

    def updatePlot(redraw_noise):   # функція для оновлення графіка
        nonlocal signal_line, noise_line, filtered_line, noise_data
        # формуємо синусоїду з параметрів
        time = np.linspace(0, 1, 500)
        amplitude = sliders['Амплітуда'].val
        frequency = sliders['Частота'].val
        phase = sliders['Фаза'].val
        y = amplitude * np.sin(2 * np.pi * frequency * time + phase)

        if signal_line is None: # якщо лінії сигналу ще не існує, то створюємо
            signal_line, = ax_plot.plot(time, y, label='Сигнал')
        else:
            signal_line.set_ydata(y) # оновлюємо дані для неї

        if redraw_noise or noise_data is None: # якщо треба оновити шум або він ще не існує
            mean = sliders['Середнє шуму'].val
            cov = sliders['Дисперсія шуму'].val
            noise_data = np.random.normal(mean, cov, size=time.shape) #генеруємо шум
        y_noise = y + noise_data

        if showNoise.get_status()[0]: # якщо ввімкнено шум
            if noise_line:
                noise_line.set_ydata(y_noise) # оновлюємо лінію шуму
            else:
                noise_line, = ax_plot.plot(time, y_noise, label='Шум', alpha=0.5, color='orange') # або створюємо лінію шуму
        else:
            if noise_line: # в іншому випадку видаляємо її
                noise_line.remove();
                noise_line = None

        if showFilter.get_status()[0]: # якщо ввімкнено фільтр
            cutoff = sliders['Частота зрізу'].val
            b, a = butter(N=4, Wn=cutoff, btype='low', fs=500)  # створюємо фільтр
            filtered = filtfilt(b, a, y_noise)  # фільтруємо

            if filtered_line is None:
                filtered_line, = ax_plot.plot(time, filtered, label='Фільтр', color='green') # створюємо лінію фільтра
            else:
                filtered_line.set_ydata(filtered) # або оновлюємо лінію фільтра
        else:
            if filtered_line: # в іншому випадку видаляємо її
                filtered_line.remove();
                filtered_line = None

        ax_plot.relim()
        ax_plot.legend()
        fig.canvas.draw_idle()

    sliders, showNoise, showFilter, reset_btn = sidebar(fig, main_grid[0, 1], updatePlot)

    updatePlot(True)
    plt.show()

if __name__ == '__main__':
    appWindow()