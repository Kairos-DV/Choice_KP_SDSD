# sbor_kp.py
"""
Модуль с функциями для сбора КП из нескольких файлов разных форматов в один файл
"""
import pandas as pd
import os
from datetime import datetime
from core.config import *



def find_all_files(folder_path=PATH_TO_DATA):
    """
    Ищет и возврашает список всех файлов в указанной дериктории. По умолчанию ищет по пути указаному в config.py
    >>> 'TEST_DATA/2025-06-18 Отчет КУЭМ (21).xlsx' in find_all_files('TEST_DATA')
    True
    >>> 'TEST_DATA/2025-05-19 Симс.csv' in find_all_files('TEST_DATA')
    True
    >>> 'TEST_DATA/2025-06-18 для ткста поиска файлов.xlsx' in find_all_files('TEST_DATA')
    True
    >>> 'TEST_DATA/2025-06-18 Ведомость опроса для выгрузки в КУЭМ по ЭМИС.xlsx' in find_all_files('TEST_DATA')
    True
    >>> 'TEST_DATA/2025-06-18 Ведомость опроса для выгрузки в КУЭМ (с типом ПУ без AD) (тчк).xlsx' in find_all_files('TEST_DATA')
    True
    """
    name_all_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
                      if f.endswith((".xlsx", ".csv"))]
    return name_all_files


def identific_format_file(name_file):
    """
    Определяет формат содержащихся данных по имени файла
    name_file: Имя файла с данными
    return: Формат данных
    >>> identific_format_file('2025-06-18 Ведомость опроса для выгрузки в КУЭМ по ЭМИС.xlsx')
    'EMIS'
    >>> identific_format_file('2025-06-18 Ведомость опроса для выгрузки в КУЭМ (с типом ПУ без AD) (тчк).xlsx')
    'TELESCOP'
    >>> identific_format_file('2025-06-18 Отчет КУЭМ (20).xlsx')
    'PYRAMIDA'
    >>> identific_format_file('2025-05-19 Симс.csv')
    'SIMS'
    >>> identific_format_file('2025-05-19.txt') is None
    True
    """
    if NAME_FILES_PYRAMIDA in name_file:
        format_file = 'PYRAMIDA'
    elif NAME_FILES_TELESCOP in name_file:
        format_file = 'TELESCOP'
    elif NAME_FILES_SIMS in name_file:
        format_file = 'SIMS'
    elif NAME_FILES_EMIS in name_file:
        format_file = 'EMIS'
    else:
        format_file = None
    return format_file


def normalize_meter_number(meter_num):
    """Нормализует номер счетчика, удаляя незначащие нули в начале"""
    if pd.isna(meter_num):
        return meter_num
    # Преобразуем в строку и удаляем ведущие нули
    return str(meter_num).lstrip('0') or '0'  # Если осталась пустая строка, возвращаем '0'
    

def delete_duplicates(table, date_column='Дата КП', id_column='Номер ПУ'):
    """
    Удаляет дубликаты строк, оставляя только самые свежие показания для каждого прибора учета

    Параметры:
    ----------
    table : pd.DataFrame
        Исходная таблица с показаниями
    date_column : str, optional
        Название столбца с датами (по умолчанию 'Дата КП')
    id_column : str, optional
        Название столбца с идентификаторами ПУ (по умолчанию 'Номер ПУ')

    Возвращает:
    -----------
    pd.DataFrame
        Таблица без дубликатов с самыми свежими показаниями
    """
    try:
        # Проверяем наличие необходимых столбцов
        if date_column not in table.columns:
            raise ValueError(f"Столбец с датами '{date_column}' не найден")
        if id_column not in table.columns:
            raise ValueError(f"Столбец с номерами ПУ '{id_column}' не найден")
        # Создаем копию таблицы для работы
        table = table.copy()

        # Нормализуем номера счетчиков (удаляем ведущие нули)
        table['Номер ПУ'] = table[id_column].apply(normalize_meter_number)
        
        # Преобразуем даты, если они еще не в datetime
        if not pd.api.types.is_datetime64_any_dtype(table[date_column]):
            table[date_column] = pd.to_datetime(table[date_column], format='mixed', errors='coerce')

        # Убедимся, что номер ПУ - строка
        table[id_column] = table[id_column].astype(str)
        
        # Сортируем по дате (сначала самые свежие)
        table = table.sort_values(by=date_column, ascending=False)

        # Удаляем дубликаты, оставляя первую (самую свежую) запись
        cleaned_table = table.drop_duplicates(subset=[id_column], keep='first')

        # Сортируем по номеру ПУ для удобства
        cleaned_table = cleaned_table.sort_values(by=id_column)

        logging.info(f"Удалено дубликатов: {len(table) - len(cleaned_table)}")
        return cleaned_table

    except Exception as e:
        logging.info(f"Ошибка при удалении дубликатов: {str(e)}")
        return table


def print_table(df, row_limit=10, col_limit=None):
    """
    Улучшенная функция для отладки, выводит указанное количество строк и столбцов

    Параметры:
    ----------
    df : pd.DataFrame
        Таблица для вывода
    row_limit : int, optional
        Максимальное количество строк для вывода (по умолчанию 10)
    col_limit : int, optional
        Максимальное количество столбцов для вывода (по умолчанию None - все столбцы)
    """
    if df is None or df.empty:
        print('Пустая таблица')
        return

    # Сохраняем текущие настройки
    original_colwidth = pd.get_option('display.max_columns')
    original_rows = pd.get_option('display.max_rows')
    original_width = pd.get_option('display.width')

    try:
        # Устанавливаем новые лимиты
        pd.set_option('display.max_columns', col_limit if col_limit else len(df.columns))
        pd.set_option('display.max_rows', row_limit)
        pd.set_option('display.width', 1000)  # Ширина вывода в символах

        # Выводим информацию о таблице
        print(f"\nДанные таблицы ({len(df)} строк, {len(df.columns)} столбцов):")
        print(f"Первые {min(row_limit, len(df))} строк:")

        # Выводим данные (работает в обычном Python)
        print(df.head(row_limit).to_string())

    finally:
        # Восстанавливаем оригинальные настройки
        pd.set_option('display.max_columns', original_colwidth)
        pd.set_option('display.max_rows', original_rows)
        pd.set_option('display.width', original_width)


def save_to_excel(table, file_name, output_folder='output', file_prefix='cleaned'):
    """
    Сохраняет DataFrame в двоичный формат Excel (.xlsb) с автоматическим именованием

    Параметры:
    ----------
    table : pd.DataFrame
        Таблица для сохранения
    file_name : str
        Имя исходного файла для генерации нового имени
    output_folder : str
        Папка для сохранения (по умолчанию 'output')
    file_prefix : str
        Префикс имени файла (по умолчанию 'cleaned')

    Возвращает:
    -----------
    str
        Полный путь к сохраненному файлу

    Исключения:
    -----------
    ValueError
        Если таблица пуста
    IOError
        При ошибках записи файла
    """
    try:
        # Проверка входных данных
        if table.empty:
            raise ValueError("Передана пустая таблица для сохранения")

        # Создание папки если не существует
        os.makedirs(output_folder, exist_ok=True)

        # Генерация имени файла с timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_name = file_name.replace('/','_')
        filename = f"{timestamp}_{file_prefix}_{new_name}.xlsx"
        filepath = os.path.join(output_folder, filename)

        # Сохранение в двоичном формате Excel
        table.to_excel(filepath, index=False, engine="openpyxl")

        logging.info(f"Файл успешно сохранен: {filepath}")
        return filepath

    except Exception as e:
        print(f"Критическая ошибка сохранения: {str(e)}")
        raise


def get_best_readings(pu, kp_data_list, current_month_year):
    """Выбирает лучшие показания для одного ПУ по заданным правилам"""
    logging.debug(f"Поиск лучших показаний для ПУ {pu}")
    pu_data = []

    for name, kp_data in kp_data_list:
        if 'Номер ПУ' not in kp_data.columns:
            logging.debug(f"В файле {name} отсутствует столбец 'Номер ПУ'")
            continue

        pu_kp = kp_data[kp_data['Номер ПУ'] == pu]
        if not pu_kp.empty:
            pu_kp = pu_kp.sort_values('Дата КП', ascending=False)
            latest = pu_kp.iloc[0]
            kp_date = latest['Дата КП']

            in_current_month = False
            if pd.notna(kp_date):
                month_year = (kp_date.month, kp_date.year)
                in_current_month = month_year == current_month_year

            pu_data.append({
                'Дата КП': kp_date,
                'Общий': latest['Общий'],
                'День': latest['День'],
                'Ночь': latest['Ночь'],
                'Источник': name,
                'В текущем месяце': in_current_month,
                'Полные данные': latest
            })

    if not pu_data:
        return {
            'Дата КП': pd.NaT,
            'Общий': None,
            'День': None,
            'Ночь': None,
            'Источник': None,
            'Примечание': "Нет данных"
        }

    # Сортировка по правилам
    pu_data_sorted = sorted(pu_data, key=lambda x: (
        -x['В текущем месяце'],
        x['Полные данные']['Общий'] is not None,
        -x['Полные данные']['Общий'] if x['Полные данные']['Общий'] is not None else 0,
        x['Дата КП'] if pd.notna(x['Дата КП']) else pd.NaT
    ))

    best = pu_data_sorted[0]
    note = "Нет даты" if pd.isna(best['Дата КП']) else \
        "Актуальные данные" if best['В текущем месяце'] else \
            "Из предыдущих месяцев"

    return {
        'Дата КП': best['Дата КП'],
        'Общий': best['Общий'],
        'День': best['День'],
        'Ночь': best['Ночь'],
        'Источник': best['Источник'],
        'Примечание': note
    }


def add_additional_readings(result_table, date_of_files, cols_KP):
    """Добавляет все показания справа с нумерацией"""
    logging.info(f"Добавление дополнительных показаний из {len(date_of_files)} файлов")
    
    counter = 1
    for name, (kp_data, _) in date_of_files.items():
        if 'Номер ПУ' not in kp_data.columns:
            logging.warning(f"В файле {name} отсутствует столбец 'Номер ПУ' - пропуск")
            continue

        logging.debug(f"Обработка файла {name} (источник #{counter})")
        kp_subset = kp_data[cols_KP].copy()
        kp_subset[f'Файл_{counter}'] = name

        cols_to_rename = [col for col in cols_KP if col != 'Номер ПУ']
        kp_subset = kp_subset.rename(columns={col: f"{col}_{counter}" for col in cols_to_rename})

        result_table = pd.merge(
            result_table,
            kp_subset,
            on='Номер ПУ',
            how='left'
        )
        counter += 1
    logging.info(f"Добавлено {counter-1} источников дополнительных показаний")    
    return result_table


def prepare_best_columns(main_table):
    """Подготавливает столбцы для лучших показаний"""
    result_table = main_table.copy()
    best_columns = ['Дата КП', 'Общий', 'День', 'Ночь', 'Источник', 'Примечание']

    for col in best_columns:
        if col in result_table.columns:
            result_table.drop(col, axis=1, inplace=True)

    return result_table, best_columns


def extern_table(main_table, date_of_files, cols_KP=COLS_KP):
    """
    Объединяет основную таблицу с показаниями из нескольких источников,
    добавляя лучшие показания и все доступные показания для каждого ПУ

    Параметры:
        main_table (pd.DataFrame): Основная таблица с данными ПУ
        date_of_files (dict): Словарь с загруженными данными в формате {имя_файла: (df, формат)}
        cols_KP (list): Список столбцов с показаниями для сохранения

    Возвращает:
        pd.DataFrame: Объединенная таблица с лучшими и всеми доступными показаниями

    Алгоритм:
        1. Для каждого ПУ выбирает лучшие показания по правилам:
           - Предпочтение показаниям текущего месяца
           - Более высокие показания предпочтительнее
           - Более свежие даты предпочтительнее
        2. Добавляет все доступные показания из всех источников
    """
    logging.info("Начало обработки extern_table")

    try:
        # Подготовка
        current_date = pd.to_datetime('today')
        current_month_year = (current_date.month, current_date.year)
        logging.info(f"Текущая дата для сравнения: {current_date}")
        
        result_table, best_columns = prepare_best_columns(main_table)
        logging.info(f"Подготовлены столбцы для лучших показаний: {best_columns}")

        # Собираем данные для обработки
        kp_data_list = [(name, data) for name, (data, _) in date_of_files.items()]
        logging.info(f"Получено {len(kp_data_list)} источников данных для обработки")

        # Получаем лучшие показания для каждого ПУ
        best_readings = {}
        pu_count = len(result_table['Номер ПУ'].unique())
        logging.info(f"Начало обработки {pu_count} приборов учета")
        
        for i, pu in enumerate(result_table['Номер ПУ'].unique(), 1):
            if i % 1000 == 0 or i == pu_count:  # Логируем каждые 1000 ПУ и последний
                logging.info(f"Обработано {i}/{pu_count} приборов учета ({i/pu_count:.1%})")
            
            best_readings[pu] = get_best_readings(pu, kp_data_list, current_month_year)
        
        logging.info("Все приборы учета обработаны, добавление лучших показаний в таблицу")

        # Добавляем лучшие показания в таблицу
        for col in best_columns:
            result_table[col] = [best_readings[pu][col] for pu in result_table['Номер ПУ']]

        # Переносим лучшие столбцы в начало
        cols_order = best_columns + [col for col in result_table.columns if col not in best_columns]
        result_table = result_table[cols_order]
        logging.info("Лучшие показания добавлены в таблицу")

        # Добавляем все остальные показания
        logging.info("Начало добавления дополнительных показаний из всех источников")
        result_table = add_additional_readings(result_table, date_of_files, cols_KP)
        logging.info("Дополнительные показания добавлены")
        
        logging.info(f"Обработка завершена. Итоговый размер таблицы: {len(result_table)} строк")
        return result_table
    
    except Exception as e:
        logging.error(f"Критическая ошибка в extern_table: {str(e)}", exc_info=True)
        raise

# Пример использования
if __name__ == "__main__":
    import doctest
    doctest.testmod()

    # all_files = find_all_files()
    # for file_name in all_files:
    #     print(file_name, identific_format_file(file_name), sep=' - ')

