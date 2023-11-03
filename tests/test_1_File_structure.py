import os

def test_All_folders_and_files_available():
    assert "application" in os.listdir(os.curdir)    
    assert "__init__.py" in os.listdir(os.curdir+"/application")    
    assert "app.py" in os.listdir(os.curdir+"/application")    
    assert "static" in os.listdir(os.curdir+"/application")    
    assert "js" in os.listdir(os.curdir+"/application/static/")
    assert "bootstrap.min.js" in os.listdir(os.curdir+"/application/static/js")
    assert "css" in os.listdir(os.curdir+"/application/static/")    
    assert "bootstrap.min.css" in os.listdir(os.curdir+"/application/static/css")
    assert "IMG" in os.listdir(os.curdir+"/application/static/")    
    assert "templates" in os.listdir(os.curdir+"/application")    
    assert "layout.html" in os.listdir(os.curdir+"/application/templates/")       
    assert "tests" in os.listdir(os.curdir)    
    assert "__init__.py" in os.listdir(os.curdir+"/tests")    
    assert "docs" in os.listdir(os.curdir)    
    assert "requirements.txt" in os.listdir(os.curdir)    

