from urllib import request

# SSL står för Secure Socket Layer och handlar om krypterade kopplingar mellan klient och server, t.ex via HTTPS, eller SSH
import ssl

# Denna innehåller funktioner för att ladda (load, loads) och skapa (dump, dumps) JSON från python-variabler
import json

# Vi använder pandas för att arbeta med data i tabell-form. 
# Ett mycket kraftfullt ramverk för data-manipulation som vi bara skrapar på ytan av i denna kurs.
import pandas as pd


def json_url_to_html_table(data_url, columns=None):
    context = ssl._create_unverified_context()
    try:
        json_data = request.urlopen(data_url, context=context).read()
        data = json.loads(json_data)
        df = pd.DataFrame(data)
        if columns==None:
            table_data = df.to_html(classes="table p-5", justify="left")    
        else:
            table_data = df.to_html(columns=columns,classes="table p-5", justify="left")
        return table_data
    except Exception as err:
        return err

def xml_url_to_html_table(data_url, xpath="", columns=None):
    context = ssl._create_unverified_context()
    try:
        xml = request.urlopen(data_url, context=context).read()
        df = pd.read_xml(xml, xpath=xpath)
        if columns==None:
            table_data = df.to_html(classes="table p-5", justify="left")    
        else:
            table_data = df.to_html(columns=columns,classes="table p-5", justify="left")
        return table_data
    except Exception as e:
        return e
