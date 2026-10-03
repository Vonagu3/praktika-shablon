"""Рисуем график по любой таблице CSV из папки data.

Запуск:
    python 01_график.py                      # файл по умолчанию
    python 01_график.py data/мои_шаги.csv    # свой файл

Правила для файла:
- первая строка — названия столбцов;
- первый столбец — дата или номер измерения (ось X);
- остальные столбцы — числа (каждый рисуется своей линией).

Результат: сводка в терминале и файл график_<имя файла>.png.
"""

import sys
from pathlib import Path

import pandas as pd
import matplotlib

matplotlib.use("Agg")  # рисуем в файл, окно не открываем
import matplotlib.pyplot as plt

# 1. Какой файл читаем: из аргумента или по умолчанию.
путь = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/визиты_к_кормушке.csv")
if not путь.exists():
    print("Нет такого файла:", путь)
    sys.exit(1)

таблица = pd.read_csv(путь)
ось_x = таблица.columns[0]
столбцы = [c for c in таблица.columns[1:] if pd.api.types.is_numeric_dtype(таблица[c])]
if not столбцы:
    print("В файле нет числовых столбцов, кроме первого. Проверьте данные.")
    sys.exit(1)

# Если первый столбец похож на дату — превращаем в дату, чтобы ось была красивой.
try:
    таблица[ось_x] = pd.to_datetime(таблица[ось_x])
except (ValueError, TypeError):
    pass

# 2. Сводка по каждому числовому столбцу.
print("Файл:", путь, "| строк:", len(таблица))
for c in столбцы:
    print(f"  {c}: среднее {таблица[c].mean():.1f}, минимум {таблица[c].min()}, максимум {таблица[c].max()}")
if len(столбцы) >= 2:
    a, b = столбцы[0], столбцы[1]
    print(f"  Связь «{a}» и «{b}» (корреляция): {таблица[a].corr(таблица[b]):.2f}")

# 3. График: каждый числовой столбец — своя линия.
цвета = ["#E07A1F", "#2E7DAF", "#2F6B45", "#A33A3A", "#6A4C93"]
fig, ось = plt.subplots(figsize=(10, 5))
for i, c in enumerate(столбцы):
    ось.plot(таблица[ось_x], таблица[c], marker="o", linewidth=2, color=цвета[i % len(цвета)], label=c)
ось.set_xlabel(ось_x)
ось.set_title(f"Данные из файла {путь.name}")  # поменяйте заголовок
ось.legend()
ось.grid(alpha=0.3)
fig.autofmt_xdate()
fig.tight_layout()

имя = f"график_{путь.stem}.png"
fig.savefig(имя, dpi=150)
print("Готово:", имя)
