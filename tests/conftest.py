import pytest
import pandas as pd

@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        'Номер ПУ': ['1', '2'],
        'Дата КП': ['2023-01-01', '2023-01-02'],
        'Общий': [100, 200]
    })