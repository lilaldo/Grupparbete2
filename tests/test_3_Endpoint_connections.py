import pytest
import urllib.request
import ssl

context = ssl._create_unverified_context()


def test_Is_online_index():
    assert urllib.request.urlopen("http://127.0.0.1:5000", context=context, timeout=10)

def test_Is_online_form():
    assert urllib.request.urlopen("http://127.0.0.1:5000/form", context=context, timeout=10)

def test_Confirm_HTTPError_on_api_GET():
    with pytest.raises(urllib.request.HTTPError):
        urllib.request.urlopen("http://127.0.0.1:5000/api", context=context, timeout=10)

def test_Confirm_no_error_on_api_POST():
    with pytest.raises(urllib.request.HTTPError):
        urllib.request.urlopen("http://127.0.0.1:5000/api", context=context, timeout=10)
