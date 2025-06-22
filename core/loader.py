# Загрузчики данных
import pandas as pd
from functools import lru_cache
import hashlib

from core.processor import *


@lru_cache(maxsize=32)
def cached_load_file(file_path, format):
    """Кэшированная версия функции load_file"""
    if not os.path.exists(file_path):
        logging.info(f"Файл не найден: {file_path}")
        return None
    try:
        # Генерируем хеш содержимого файла для инвалидации кэша
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()

        # Ключ кэша = путь + хеш + формат
        cache_key = f"{file_path}_{file_hash}_{format}"
        return load_file(file_path, format)
    except Exception as e:
        logging.info(f"Ошибка при кэшированной загрузке файла {file_path}: {str(e)}")
        return None

def get_file_hash(file_path):
    """Генерирует хеш файла для инвалидации кэша при изменениях"""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def load_and_extend_sims(file_path):
    """
    Загружает файл SIMS и добавляет недостающие столбцы, заполняя их"Не указано"
    """
    if not os.path.exists(file_path):
        logging.info(f"Файл не найден: {file_path}")
        return None
    try:
        # Загрузка CSV с разделителем ";"
        df = pd.read_csv(
            file_path,
            sep=';',
            encoding='windows-1251',
            header=1,  # Пропускаем первую строку
            usecols=SIMS_NEEDED_COLS,
            names=SIMS_NEW_NAMES,
            on_bad_lines='warn',
            decimal=','
        )
        # Очистка данных
        df = df.dropna(how='all')
        pu_column = 'Номер ПУ'

        if pu_column not in df.columns:
            raise ValueError(f"Столбец с номером ПУ не найден. Доступные столбцы: {df.columns.tolist()}")

        # Создаем недостающие столбцы и заполняем их номером ПУ
        additional_columns = {
            'ПО': "СИМС",
            'Населенный пункт': "Не указано",
            'ТП': "Не указано",
            'Потребитель': "Не указано",
            'Лицевой счет': "Не указано"
        }

        for col_name, values in additional_columns.items():
            if col_name not in df.columns:
                df[col_name] = values

        return df

    except Exception as e:
        logging.info(f"Ошибка обработки файла {file_path}: {str(e)}")
        return None


def optimize_dataframe(df):
    """Оптимизация типов данных для ускорения обработки"""
    if df.empty:
        return df

    # Числовые столбцы
    num_cols = ['Общий', 'День', 'Ночь']
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce', downcast='float')

    # Категориальные данные
    cat_cols = ['ПО', 'РЭС', 'Тип ПУ']
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].astype('category')

    # Даты
    if 'Дата КП' in df.columns:
        df['Дата КП'] = pd.to_datetime(df['Дата КП'], format='mixed', errors='coerce')

    return df


def load_file(file_path, format):
    """Загружает файл с автоматической фильтрацией столбцов и переименованием заголовков"""
    if not os.path.exists(file_path):
        logging.info(f"Файл не найден: {file_path}")
        return None
    try:
        # Читаем файл в зависимости от формата
        if format == 'PYRAMIDA':
            # Определяем строку с заголовком
            header_row = 4
            # Загружаем данные Пирамиды, пропуская метастроки
            df = pd.read_excel(file_path,
                               header=header_row,
                               usecols=PYRAMIDA_NEEDED_COLS,
                               names=NEW_NAMES
                               )
        elif format == 'TELESCOP':
            header_row = 2
            # Загружаем данные Телескоп, пропуская метастроки
            df = pd.read_excel(file_path,
                               header=header_row,
                               usecols=TELESCOP_NEEDED_COLS,
                               names=TELESCOP_NEW_NAMES,
                               decimal=','
                               )
        elif format == 'EMIS':
            header_row = 2
            # Загружаем данные Эмис, пропуская метастроки
            df = pd.read_excel(file_path,
                               header=header_row,
                               usecols=EMIS_NEEDED_COLS,
                               names=EMIS_NEW_NAMES
                               )
        elif format == 'SIMS':
            # Загружаем файл SIMS и добавляем недостающие столбцы, заполняя их значением "Не указано"
            df = load_and_extend_sims(file_path)
        else:
            raise ('неизвесный формат')

        # Оптимизация типов данных для ускорения обработки
        df = optimize_dataframe(df)

        df = df.reindex(columns=NEW_NAMES)  # Оставляем только нужные столбцы в правильном порядке
        # Добавление столбца с источником данных


        # Отладочная информация
        logging.info(f"Успешно загружен файл {file_path}. Формат файла {format}.")  # Столбцы:", df.columns.tolist())
        return df
    except Exception as e:
        logging.info(f"Ошибка загрузки файла: {e}")
        return None


def process_file(name):
    """Обработка одного файла с возвратом имени файла и результата"""
    format = identific_format_file(name)
    if not format:
        logging.info(f'В папке с данными лежит файл неизвестного формата. {name} Он не будет обработан')
        return None

    try:
        df = cached_load_file(name, format)
        if df is not None:
            df = delete_duplicates(df)
            return (name, df, format)
        else:
            logging.info(f"Не удалось загрузить файл {name}")
    except Exception as e:
        logging.info(f"Ошибка обработки файла {name}: {str(e)}")
    return None

if __name__ == "__main__":
    import doctest

    doctest.testmod()