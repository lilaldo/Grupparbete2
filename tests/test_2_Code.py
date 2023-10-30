from application import func

def test_Func_json_url_to_html_POSITIVE():
    url = f"https://date.nager.at/api/v3/PublicHolidays/2023/se"
    assert not isinstance(func.json_url_to_html_table(url), Exception)

def test_Func_json_url_to_html_NEGATIVE():
    url = f"http://vecka.nu"
    assert isinstance(func.json_url_to_html_table(url), Exception)
