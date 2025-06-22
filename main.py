#Meter reading collection
from core.loader import *
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm  # Для прогресс-бара
import logging


def main():
    """
    Собирает КП из нескольких файлов разных форматов в один файл
    """
    name_all_files = find_all_files()
    date_of_files = dict()

    # Параллельная обработка с прогресс-баром
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(tqdm(
            executor.map(process_file, name_all_files),
            total=len(name_all_files),
            desc="Обработка файлов"))

    # Фильтрация None и заполнение date_of_files
    for result in results:
        if result is not None:
            name, df, format = result
            date_of_files[name] = [df, format]

    if not date_of_files:
        logging.info("Нет данных для обработки - все файлы не загрузились")
        return

    # Собираем все таблицы в один файл
    all_tables = [df for df, _ in date_of_files.values()]
    result = pd.concat(all_tables, ignore_index=True)
    logging.info(f'Объединено {len(all_tables)} файлов. До удаления дублей {len(result)} строк')

    # Удаляем дубли строк с худшими КП
    result = delete_duplicates(result)

    # Приклеиваем КП из всех файлов к общей таблице
    result = extern_table(result, date_of_files)

    # Сохраняем файл в новый файл
    result_file_name = save_to_excel(result, 'Result')
    logging.debug('Результат сохранен в файле ', result_file_name)

def dev():
    """
    Тестирует функциональность. Удалить после разработк
    """
    # file_path = PATH_TO_DATA + "2025-05-19 Симс.csv"
    # LIMIT = 50
    # format = identific_format_file(file_path)
    # df = load_file(file_path, format)
    # print_table(df, LIMIT)
    # new_file_name = save_to_excel(df, file_path, output_folder='output', file_prefix='cleaned')
    # print('Файл сохранен под новым именем:', new_file_name)
    # Ищем фалы с данными
    name_all_files = find_all_files()
    date_of_files = dict()
    all_tables = []
    for name in name_all_files:
        format = identific_format_file(name)  # Определяем формат файла
        if format:
            df = load_file(name, format)  # Загружаем файлы
            df = delete_duplicates(df)  # Удаляем дубли строк с худшими КП
            all_tables.append(df)
            # new_file_name = save_to_excel(df, name)  # Сохраняем файл в новый файл
            date_of_files[name] = [df, format]
        else:
            print(f'В папке с данными лежит файл неизвестного формата. {name} Он не будет обработан')

    list_of_dfs = [value[0] for value in date_of_files.vaslue()]
    result = pd.concat(list_of_dfs, ignore_index=True)

if __name__ == "__main__":
    # Для тестирования
    # dev()

    # Для основного режима
    main()
