with open("/Users/carlf/Downloads/chromedriver_win32/chromedriver.exe", "rb") as f:
    data = f.read()
    
data = data.replace(b"cdc_", b"not_")

with open("/Users/carlf/Downloads/chromedriver_win32/chromedriver.exe", "wb") as f:
    f.write(data)