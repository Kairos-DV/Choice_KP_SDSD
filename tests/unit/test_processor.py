import pytest
from core.processor import *
from datetime import datetime
import pandas as pd
import os


def test_find_all_files():
    files = find_all_files('TEST_DATA')
    assert len(files) > 0
    assert all(f.endswith(('.xlsx', '.csv')) for f in files)


def test_identific_format_file():
    assert identific_format_file('test_Отчет КУЭМ.xlsx') == 'PYRAMIDA'
    assert identific_format_file('test_типом ПУ без AD.xlsx') == 'TELESCOP'
    assert identific_format_file('test_Симс.csv') == 'SIMS'
    assert identific_format_file('test_ЭМИС.xlsx') == 'EMIS'
    assert identific_format_file('unknown.txt') is None


def test_delete_duplicates():
    data = {
        'Номер ПУ': ['1', '1', '2', '2'],
        'Дата КП': ['2023-01-01', '2023-01-02', '2023-01-01', '2023-01-03'],
        'Общий': [100, 200, 300, 400]
    }
    df = pd.DataFrame(data)
    df['Дата КП'] = pd.to_datetime(df['Дата КП'])

    result = delete_duplicates(df)
    assert len(result) == 2
    assert result['Номер ПУ'].tolist() == ['1', '2']
    assert result['Общий'].tolist() == [200, 400]


def test_save_to_excel(tmp_path):
    df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    output_folder = tmp_path / "output"
    filepath = save_to_excel(df, 'test', output_folder=str(output_folder))
    assert os.path.exists(filepath)
    assert 'test' in filepath