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


if __name__ == "__main__":
    # Для основного режима
    main()
