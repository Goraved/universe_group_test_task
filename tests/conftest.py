import os
import platform
import sys
from datetime import datetime

import httpx
import pytest

from api import APIs


# Pytest configuration
def pytest_configure(config):
    config.option.metadata = {
        'Project': 'Universe Group test task HTML report',
        'Base URL': os.getenv('API_BASE_URL', 'https://automation-qa-test.universeapps.limited'),
        'Python Version': sys.version,
        'httpx Version': httpx.__version__,
        'Platform': platform.platform(),
        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    api_token = os.getenv('API_TOKEN')
    if not api_token or not api_token.startswith('eyJ'):
        pytest.fail("ERROR: Invalid or missing API_TOKEN environment variable")


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    pytest.current_test = item


def pytest_html_report_title(report):
    report.title = "Universe Group test task HTML report"


def pytest_html_results_summary(prefix, summary, postfix):
    prefix.append("<h3>Test Summary</h3>")
    prefix.append(f"<p>API URL: {os.getenv('API_BASE_URL', 'https://automation-qa-test.universeapps.limited')}</p>")
    prefix.append(f"<p>Test executed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")


@pytest.fixture(scope="session")
def apis():
    return APIs()


@pytest.fixture(scope="session")
def apis_invalid_token():
    return APIs().with_invalid_token()
