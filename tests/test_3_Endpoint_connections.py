import pytest
import urllib.request
import ssl

context = ssl._create_unverified_context()


def test_is_online_index():
    assert urllib.request.urlopen("http://127.0.0.1:5000", context=context, timeout=10) #Test if localhost is up and running.

def test_is_online_form():
    assert urllib.request.urlopen("http://127.0.0.1:5000/priser", context=context, timeout=10) # Testing if the priser page is up and running.

def test_confirm_HTTPError_on_api_GET():
    with pytest.raises(urllib.request.HTTPError):
        urllib.request.urlopen("http://127.0.0.1:5000/api", context=context, timeout=10) # Makes sure that this page doesn't exist.

#Taken from teacher, are multiple test worth using.