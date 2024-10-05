from scipy.ndimage import gaussian_filter
from PIL import Image
import pandas as pd
import numpy as np
import datetime
import math, random

w = 8

def getData():
	d1 = pd.read_csv("docs/data1.csv", sep=";")
	d1 = d1.rename(columns={"Signal Strength" : "ss1", "Distance" : "d1"})
	d2 = pd.read_csv("docs/data2.csv", sep=";")
	d2 = d2.rename(columns={"Signal Strength" : "ss2", "Distance" : "d2"})

	#Average MACs by minute
	d1["Timestamp"] = d1["Timestamp"] // 60
	d2["Timestamp"] = d2["Timestamp"] // 60

	# Average timesteps
	d1 = d1.groupby(['MAC Address', 'Timestamp']).mean().reset_index()
	d1 = d1.drop_duplicates()
	d2 = d2.groupby(['MAC Address', 'Timestamp']).mean().reset_index()
	d2 = d2.drop_duplicates()
	print(d1.head())
	print(d1.duplicated().any())

	print(d2.head())
	print(d2.duplicated().any())

	# Merge sensors data
	data = pd.merge(d1, d2, on=["MAC Address", "Timestamp"])
	data = data.drop_duplicates()
	print(data.info())
	# Timestamp to datetime
	data[["year", "month", "day", "day_week", "hour", "minute"]] = data.apply(lambda row: pd.Series(timestamp2datetime(row["Timestamp"])), axis=1)
	
	return data


def get_start_timestamp():
	date_time = f"{pd.to_datetime(data[['year', 'month', 'day', 'hour', 'minute']]).min()}"
	return date_time.split(" ")[0] + "-" + date_time.split(" ")[1].split(":")[0] + "-" + date_time.split(" ")[1].split(":")[1]


def timestamp2datetime(time):
	dt_object = datetime.datetime.fromtimestamp(time * 60)
	year = dt_object.strftime('%Y')
	month = dt_object.strftime('%m')
	day_of_month = dt_object.strftime('%d')
	day_of_week = dt_object.strftime('%A')
	hour = dt_object.strftime('%H')
	minute = dt_object.strftime('%M')
	return year, month, day_of_month, day_of_week, hour, minute


def calc_coodinates(data, w):
	data[["x", "y"]] = data.apply(lambda row: pd.Series(calc_single_coodinates(row["d1"], row["d2"], w)), axis=1)
	return data


def calc_single_coodinates(d1, d2, w):
	try:
		ang_t = math.acos((d1**2 + d2**2 - w**2) / (2*d1*d2))
	except:
		return -1, -1
	area = (d1*d2*math.sin(ang_t)) / 2
	y = (2 * area) / w

	ang_s1 = math.acos((d1**2 + w**2 - d2**2) / (2*d1*w))

	ang = math.asin(y / d1)
	x_dist = math.cos(ang) * d1
	x = -x_dist if ang_s1 > math.pi / 2 else x_dist
	if x > 0 and x < 7 and y < 7:
		return -1, -1
	return x, y


def make_heat_map(data, start_x, start_y, end_x, end_y, len_x_meters, len_y_meters, sigma):
	img = Image.open('images/sala.png')
	img = img.convert("RGBA")
	img_array = np.asarray(img)
	iy = img_array.shape[0]
	ix = img_array.shape[1]
	heatmap = np.zeros((iy, ix))
	#print("aaaaaa", img_array.shape)

	for i, row in data.iterrows():
		x, y = row["x"], row["y"]
		if y > 0:
			img_x = int(start_x + ((end_x - start_x) / len_x_meters) * x)
			img_y = int(start_y + ((end_y - start_y) / len_y_meters) * y)
			#if img_x < 0: img_x = 0
			#if img_x >= ix: img_x = ix-1
			#if img_y >= iy: img_y = iy-1
			if img_x < ix-1 and img_y < iy and img_y > 0 and img_x > 0:
				heatmap[iy-img_y][img_x] = 255

	marker_size = 10
	heatmap = gaussian_filter(heatmap.astype(float), sigma=sigma)
	m = np.max(heatmap)
	heatmap = (heatmap / m) * 255 if m > 0 else heatmap
	nh = np.zeros_like(img)
	nh[:,:,0] = 255
	nh[:,:,1] = 20
	nh[:,:,2] = 20
	nh[:,:,3] = heatmap
	if False:
		nh[iy-start_y-marker_size:iy-start_y,start_x:start_x+marker_size,0] = 0
		nh[iy-start_y-marker_size:iy-start_y,start_x:start_x+marker_size,1] = 255
		nh[iy-start_y-marker_size:iy-start_y,start_x:start_x+marker_size,3] = 255
		nh[iy-end_y, end_x, 0] = 0
		nh[iy-end_y, end_x, 1] = 255
		nh[iy-end_y, end_x, 3] = 255
		nh[iy-start_y-marker_size:iy-start_y, end_x-marker_size:end_x, 0] = 0
		nh[iy-start_y-marker_size:iy-start_y, end_x-marker_size:end_x, 1] = 255
		nh[iy-start_y-marker_size:iy-start_y, end_x-marker_size:end_x, 3] = 255
	nh = np.clip(nh, 0, 255)
	heatmap = Image.fromarray(nh.astype(np.uint8))
	heatmap = heatmap.convert("RGBA")
	result = Image.alpha_composite(img, heatmap)
	result = result.convert('RGBA')
	result.save("images/heatmap.png")


def new_view(date, time, start_x, start_y, end_x, end_y, len_x_meters, len_y_meters, sigma, window):
	global w
	global data
	print(date, time)
	if len_x_meters != w:
		w = len_x_meters
		data = getData()
		data = calc_coodinates(data, w)

	date = date.split("/")
	time = time.split(":")
	year, month, day = date[2], date[1].zfill(2), date[0].zfill(2)
	hour, minute = time[0].zfill(2), time[1].zfill(2)
	start_minute = str(int(minute) - window).zfill(2)
	end_minute = str(int(minute) + window).zfill(2)
	this_data = data[(data["year"] == year) & (data['month'] == month) & (data['day'] == day) & (data['hour'] == hour) & (data['minute'].between(start_minute,  end_minute))]#(data['minute'] == minute)
	this_data = this_data.groupby(['MAC Address', 'day_week', 'Device', 'Area']).mean().reset_index()
	make_heat_map(this_data, start_x, start_y, end_x, end_y, len_x_meters, len_y_meters, sigma)


def extract_vendor(mac_address):
    vendor = mac_address[:8]
    if vendor.startswith(('00', '08', '02', '03', '04', '05')):
        return 'PC'
    else:
        return 'Phone'


def zones(row):
	x = row["x"]
	y = row["y"]
	# Verde escuro
	if x < -2.022 and x > -5.8855 and y > 6.55 and y < 16.78:
		return "Estatistica Socialogia Politica e Direito"
	# Verde claro
	elif x > 1.5183 and x < 5.7849 and y > 10.6348 and y < 14.2969:
		return "Dicionarios e Enciclopedias"
	# Vermelho
	elif x > 8.2172 and x < 12.0808 and y > 5.8216 and y < 10.0440:
		return "Historia Biografias e Literatura"
	# Azul
	elif x > 1.5183 and x < 6.2885 and y > 18.7943 and y < 22.4061:
		return "Literatura Linguas e Arte"
	# Roxo
	elif x > 0.3599 and x < 7.0440 and y > 2.2738 and y < 5.9359:
		return "Filosofia Teologia Psicologia"
	# Cabines esquerda
	elif x < -6.2959 and y > 6.6988 and y < 15.8657:
		return "Cabines de Estudo"
	# Cabines cima
	elif x > 0.8058 and x < 7.1521 and y > 22.6652:
		return "Cabines de Estudo"
	else:
		return "Zona Estudo"

data = getData()
data = calc_coodinates(data, w)
data['Device'] = data['MAC Address'].apply(extract_vendor)

data["Area"] = data.apply(zones, axis=1)
outputfile = data
outputfile = outputfile.rename(columns={"ss1" : "S1 Signal Strength", "ss2" : "S2 Signal Strength", "d1" : "Distance to S1", "d2" : "Distance to S2", 
					"day" : "Day", "day_week" : "Day of the Week", "year" : "Year", "month" : "Month", "hour" : "Hour", "minute" : "Minute", "x" : "X", "y" : "Y"})
outputfile.to_csv('docs/data.csv', index=False, sep=",")
