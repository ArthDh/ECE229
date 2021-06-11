import sys
from os import path
from selenium.webdriver.chrome.options import Options
from app import create_app
import pytest


sys.path.append(path.dirname(path.dirname(__file__)))

@pytest.fixture
def app():
    yield create_app()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


def pytest_setup_options():
    options = Options()
    options.add_argument('--disable-gpu')
    options.add_argument('--headless')
    return options