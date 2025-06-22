import pytest
from core.config import *


def test_config_constants():
    assert PATH_TO_DATA == 'TEST_DATA/'
    assert NAME_FILES_PYRAMIDA == 'Отчет КУЭМ '
    assert NAME_FILES_TELESCOP == 'типом ПУ без AD'
    assert NAME_FILES_SIMS == 'Симс'
    assert NAME_FILES_EMIS == 'ЭМИС'

    assert isinstance(PYRAMIDA_NEEDED_COLS, list)
    assert isinstance(TELESCOP_NEEDED_COLS, list)
    assert isinstance(SIMS_NEEDED_COLS, list)
    assert isinstance(EMIS_NEEDED_COLS, list)

    assert isinstance(NEW_NAMES, list)
    assert isinstance(SIMS_NEW_NAMES, list)
    assert isinstance(EMIS_NEW_NAMES, list)
    assert isinstance(TELESCOP_NEW_NAMES, list)

    assert isinstance(COLS_KP, list)


def test_logging_config():
    import logging
    assert logging.getLogger().level == logging.INFO