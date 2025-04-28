from json import JSONDecodeError
from unittest.mock import patch, MagicMock

import httpx
import pytest

from api.base_api import BaseApi

pytestmark = pytest.mark.unit


@pytest.fixture
def base_api():
    token = 'dummy_token'
    base_url = 'https://automation-qa-test.universeapps.limited'
    return BaseApi(base_url=base_url, token=token)


def test_init(base_api):
    assert base_api.base_url == 'https://automation-qa-test.universeapps.limited'
    assert 'Bearer dummy_token' in base_api.headers['Authorization']
    assert isinstance(base_api.client, httpx.Client)
    assert base_api.headers['Content-Type'] == 'application/json'


@pytest.mark.parametrize('method, url', [
    ('GET', '/test_endpoint'),
    ('HEAD', '/another_endpoint'),
    ('OPTIONS', '/options_endpoint'),
    ('DELETE', '/delete_endpoint')
])
def test_request_methods_without_body(base_api, method, url):
    with patch.object(base_api.client, 'request', return_value=httpx.Response(200)) as mock_request:
        response = base_api.request(method, url)
        assert response.status_code == 200
        mock_request.assert_called_once_with(method, f'{base_api.base_url}{url}', headers=base_api.headers)


@pytest.mark.parametrize('method, url, data', [
    ('POST', '/post_endpoint', {'key': 'value'}),
    ('PUT', '/put_endpoint', {'id': 1, 'name': 'test'}),
    ('PATCH', '/patch_endpoint', {'status': 'active'})
])
def test_request_methods_with_body(base_api, method, url, data):
    with patch.object(base_api.client, 'request', return_value=httpx.Response(200)) as mock_request:
        response = base_api.request(method, url, data=data)
        assert response.status_code == 200
        mock_request.assert_called_once_with(method, f'{base_api.base_url}{url}', headers=base_api.headers, json=data)


def test_request_with_expected_status(base_api):
    with patch.object(base_api.client, 'request', return_value=httpx.Response(400)):
        with patch.object(BaseApi, 'check_status_code') as mock_check:
            response = base_api.request('GET', '/test', expected_status=400)
            mock_check.assert_called_once_with(response, 400)


@pytest.mark.parametrize('status_code', [200, 201, 204])
def test_check_status_code_success(status_code):
    response_mock = MagicMock(status_code=status_code)
    BaseApi.check_status_code_success(response_mock)


@pytest.mark.parametrize('status_code', [400, 404, 500])
def test_check_status_code_success_failure(status_code):
    response_mock = MagicMock(status_code=status_code, reason_phrase='Error', text='Error message')
    with pytest.raises(AssertionError) as excinfo:
        BaseApi.check_status_code_success(response_mock)
    assert f'Response code = {status_code}' in str(excinfo.value)


@pytest.mark.parametrize('expected_code, actual_code, should_raise', [
    (200, 200, False),
    (404, 404, False),
    (500, 500, False),
    (200, 400, True),
    (201, 500, True)
])
def test_check_status_code(expected_code, actual_code, should_raise):
    response_mock = MagicMock(status_code=actual_code)
    response_mock.json.return_value = {'error': 'Test error'}

    if should_raise:
        with pytest.raises(AssertionError) as excinfo:
            BaseApi.check_status_code(response_mock, expected_code)
        assert f'Expected = {expected_code}, received = {actual_code}' in str(excinfo.value)
    else:
        BaseApi.check_status_code(response_mock, expected_code)


def test_check_status_code_with_json_decode_error():
    response_mock = MagicMock(status_code=400, text='Invalid JSON')
    response_mock.json.side_effect = JSONDecodeError('Invalid JSON', '', 0)

    with pytest.raises(AssertionError) as excinfo:
        BaseApi.check_status_code(response_mock, 200)
    assert 'Unable to parse error' in str(excinfo.value)


def test_parse_response_to_json():
    json_data = {'key': 'value'}
    response_mock = MagicMock()
    response_mock.json.return_value = json_data
    assert BaseApi.parse_response_to_json(response_mock) == json_data


def test_del_method(base_api):
    with patch.object(base_api.client, 'close') as mock_close:
        base_api.__del__()
        mock_close.assert_called_once()


@pytest.mark.parametrize('method_name, http_method', [
    ('get', 'GET'),
    ('head', 'HEAD'),
    ('options', 'OPTIONS'),
    ('post', 'POST'),
    ('put', 'PUT'),
    ('patch', 'PATCH'),
    ('delete', 'DELETE')
])
def test_http_method_wrappers(base_api, method_name, http_method):
    with patch.object(base_api, 'request', return_value=httpx.Response(200)) as mock_request:
        method = getattr(base_api, method_name)

        # Different parameter handling for methods with body vs without
        if method_name in ('post', 'put', 'patch'):
            data = {'test': 'data'}
            response = method('/test_endpoint', data=data)
            mock_request.assert_called_once_with(http_method, '/test_endpoint', headers=None, data=data)
        else:
            response = method('/test_endpoint')
            mock_request.assert_called_once_with(http_method, '/test_endpoint', None)

        assert response.status_code == 200
