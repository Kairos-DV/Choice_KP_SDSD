# tests/unit/test_loader.py
import pandas as pd
import os
import pytest
from core.loader import *
import pandas as pd



def test_load_and_extend_sims(tmp_path):
    # Подготовка тестового файла
    test_file = tmp_path / "Симс.csv"
    content = """header1\nheader2\n1;РЭС1;Тип1;Номер1;2023-01-01;100;50;50"""
    test_file.write_text(content, encoding='windows-1251')

    # Вызов тестируемой функции
    result = load_and_extend_sims(str(test_file))

    # Проверки
    assert isinstance(result, pd.DataFrame)
    assert 'ПО' in result.columns
    assert result['ПО'].iloc[0] == 'СИМС'

def test_load_and_extend_sims2(tmp_path):
    # Создаем тестовый CSV файл SIMS
    test_file = tmp_path / "Симс.csv"
    content = """header1
    header2
    1;2;3;4;5;6;7;8;9"""
    with open(test_file, 'w', encoding='windows-1251') as f:
        f.write(content)

    result = load_and_extend_sims(str(test_file))
    assert isinstance(result, pd.DataFrame)
    assert 'ПО' in result.columns
    assert 'РЭС' in result.columns
    assert result['ПО'].iloc[0] == 'СИМС'


def test_cached_load_file(tmp_path, monkeypatch):
    # Создаем тестовый файл с корректными данными для PYRAMIDA
    test_file = tmp_path / "Отчет КУЭМ test.xlsx"

    # Создаем DataFrame с нужными колонками
    df = pd.DataFrame({
        'A': range(5),
        'B': ['РЭС'] * 5,
        'C': ['Населенный пункт'] * 5,
        # ... все остальные колонки согласно PYRAMIDA_NEEDED_COLS
    })
    df.to_excel(test_file, index=False)

    # Мокаем identific_format_file
    monkeypatch.setattr('core.processor.identific_format_file', lambda x: 'PYRAMIDA')

    # Мокаем load_file чтобы возвращал тестовый DataFrame
    with monkeypatch.context() as m:
        m.setattr('core.loader.load_file', lambda x, y: df)

        # Тестируем cached_load_file
        result = cached_load_file(str(test_file), 'PYRAMIDA')
        assert result is not None
        assert isinstance(result, pd.DataFrame)

        # Проверяем кэширование
        result_cached = cached_load_file(str(test_file), 'PYRAMIDA')
        assert result.equals(result_cached)

def test_optimize_dataframe():
    data = {
        'Общий': ['100', '200'],
        'ПО': ['A', 'B'],
        'Дата КП': ['2023-01-01', '2023-01-02']
    }
    df = pd.DataFrame(data)
    result = optimize_dataframe(df)

    assert pd.api.types.is_float_dtype(result['Общий'])
    assert pd.api.types.is_categorical_dtype(result['ПО'])
    assert pd.api.types.is_datetime64_any_dtype(result['Дата КП'])