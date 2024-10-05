from flask import Flask, render_template, send_file, request, jsonify
from process import new_view, get_start_timestamp


server = Flask(__name__, template_folder="./")


@server.route("/")
def home():
	return open("site.html", "r").read()

@server.route("/start_time")
def start_time():
	return jsonify(str(get_start_timestamp()))

@server.route("/heatmap", methods=["GET", "POST"])
def heatmap():
	if request.method == "GET":
		return send_file("images/sala.png", mimetype='image/gif')
	elif request.method == "POST":
		date = request.json["date"]
		time = request.json["time"]
		start_x = int(request.json["start_x"])
		start_y = int(request.json["start_y"])
		end_x = int(request.json["end_x"])
		end_y = int(request.json["end_y"])
		len_x = float(request.json["len_x"])
		len_y = float(request.json["len_y"])
		sigma = int(request.json["sigma"])
		window = int(request.json["window"])

		new_view(date, time, start_x, start_y, end_x, end_y, len_x, len_y, sigma, window)
		return send_file("images/heatmap.png", mimetype='image/gif')



server.run(host="0.0.0.0", port=8080)