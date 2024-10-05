import requests
import time


url_w = "https://api.openweathermap.org/data/2.5/weather?lat=44.34&lon=10.99&appid=65030af63ddfd98a4bd20d0fc5c6251d"
url_oaq = "https://api.openaq.org/v2/locations?parameters=pm25"


while True:
	response = requests.get(url_oaq)
	print(response.json())
	response = requests.get(url_w)
	print(response.json())
	time.sleep(10)