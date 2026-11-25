# Books Rec System

Веб-приложение для подбора книг по описаниям и жанрам. Выберите от трёх до пяти книг из локального каталога, и система покажет похожие книги с оценкой сходства. Интерфейс приложения на английском.

[Быстрый старт](#быстрый-старт) · [Настройка каталога](SETUP_GUIDE.md) · [История версий](CHANGELOG.md)

[![Релиз](https://img.shields.io/github/v/release/Lizard51/books-rec-system?include_prereleases)](https://github.com/Lizard51/books-rec-system/releases)
[![Лицензия MIT](https://img.shields.io/badge/license-MIT-427259)](LICENSE)

## Что умеет

- Искать книги в CSV-каталоге.
- Сравнивать описания и жанры с помощью TF-IDF и косинусного сходства.
- Показывать до десяти рекомендаций и оценку сходства для каждой книги.
- Искать книги через Google Books при наличии API-ключа. Для расчёта рекомендаций выбранные названия должны присутствовать в локальном каталоге.

## Быстрый старт

Нужны Python 3.9–3.11, Git и PowerShell. В репозитории есть небольшой каталог с вымышленными книгами для демонстрации.

```powershell
git clone https://github.com/Lizard51/books-rec-system.git
cd books-rec-system
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item data/books.example.csv data/books.csv
.\.venv\Scripts\python.exe -m flask --app app run --host 127.0.0.1
```

Откройте [http://127.0.0.1:5000](http://127.0.0.1:5000). В разделе **Search Local Database** выберите **The Lantern Archive**, **Crown of Moss** и **The Forest Compass**, затем нажмите **Generate Recommendations**.

Команды для macOS и Linux и формат своего каталога приведены в [руководстве по настройке](SETUP_GUIDE.md).

## Как устроен проект

| Файл | Что в нём |
| --- | --- |
| [app.py](app.py) | Flask-приложение, поиск и запросы рекомендаций |
| [recommender.py](recommender.py) | TF-IDF, профиль по выбранным книгам и ранжирование |
| [utils/preprocessing.py](utils/preprocessing.py) | Очистка и проверка каталога |
| [data/books.example.csv](data/books.example.csv) | Демонстрационный каталог |

## Лицензия

Исходный код и демонстрационный каталог доступны по [лицензии MIT](LICENSE).
