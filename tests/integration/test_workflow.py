# tests/integration/test_workflow.py
from main import main
from core.processor import find_all_files
import pytest


def test_full_workflow(tmp_path, monkeypatch):
    # Подготовка тестовых данных
    test_data_dir = tmp_path / "TEST_DATA"
    test_data_dir.mkdir()

    # Создаем тестовый файл
    test_file = test_data_dir / "Отчет КУЭМ.xlsx"
    pd.DataFrame({'A': range(5)}).to_excel(test_file)

    # Мокаем конфигурацию
    monkeypatch.setattr('core.config.PATH_TO_DATA', str(test_data_dir))

    # Запускаем основной workflow
    main()

    # Проверяем результаты
    files = find_all_files()
    assert len(files) == 1


def test_integration_workflow(tmp_path):
    # Создаем тестовые файлы разных форматов
    test_data_dir = tmp_path / "TEST_DATA"
    test_data_dir.mkdir()

    # 1. Тестовый файл Пирамиды
    pyramida_file = test_data_dir / "Отчет КУЭМ.xlsx"
    df_pyramida = pd.DataFrame({
        'A': range(5),
        'B': ['РЭС'] * 5,
        'C': ['ПУ'] * 5
    })
    df_pyramida.to_excel(pyramida_file, index=False)

    # 2. Тестовый файл SIMS
    sims_file = test_data_dir / "Симс.csv"
    sims_content = """header1
header2
1;РЭС1;Тип1;Номер1;2023-01-01;100;50;50"""
    with open(sims_file, 'w', encoding='windows-1251') as f:
        f.write(sims_content)

    # Запускаем основной workflow
    files = find_all_files(str(test_data_dir))
    assert len(files) == 2

    format1 = identific_format_file(str(pyramida_file))
    format2 = identific_format_file(str(sims_file))
    assert format1 == 'PYRAMIDA'
    assert format2 == 'SIMS'

    # Проверяем обработку через main
    with patch('config.PATH_TO_DATA', str(test_data_dir)):
        main()

    # Проверяем создание выходного файла
    output_files = list((tmp_path / "output").glob("*.xlsx"))
    assert len(output_files) == 1