import pytest
from main import *
from unittest.mock import patch, MagicMock


@patch('main.find_all_files')
@patch('main.process_file')
def test_main(mock_process_file, mock_find_all_files):
    # Настраиваем моки
    mock_find_all_files.return_value = ['file1.xlsx', 'file2.csv']
    mock_df = MagicMock()
    mock_process_file.return_value = ('file1.xlsx', mock_df, 'PYRAMIDA')

    # Вызываем main
    main()

    # Проверяем вызовы
    mock_find_all_files.assert_called_once()
    assert mock_process_file.call_count == 2


@patch('main.find_all_files')
def test_main_no_files(mock_find_all_files, capsys):
    mock_find_all_files.return_value = []
    main()
    captured = capsys.readouterr()
    assert "Нет данных для обработки" in captured.out