# Загрузчики данных
import pandas as pd
import os
from datetime import datetime
from config import *


def load_and_extend_sims(file_path):
    """
    Загружает файл SIMS и добавляет недостающие столбцы, заполняя их"Не указано"
    """
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
        print(f"Ошибка обработки файла {file_path}: {str(e)}")
        return None


def load_file(file_path, format):
    """Загружает файл с автоматической фильтрацией столбцов и переименованием заголовков"""
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

        df = df.reindex(columns=NEW_NAMES)  # Оставляем только нужные столбцы в правильном порядке
        # Добавление столбца с источником данных


        # Отладочная информация
        print(f"Успешно загружен файл {file_path}. Формат файла {format}.")  # Столбцы:", df.columns.tolist())
        return df
    except Exception as e:
        print(f"Ошибка загрузки файла: {e}")
        return None


if __name__ == "__main__":
    import doctest

    doctest.testmod()