from flask import Flask, request
import csv
import time


app = Flask(__name__)
save_file_path = "./logs/api_requests.csv"


@app.route("/submit", methods=["POST"])
def hello_world():
    data = {"timestamp": int(time.time()), 
            "senderId": request.form.get("id"), 
            "byteload": request.form.get("byteload")}
    with open(save_file_path, "a") as stats_file:
        writer = csv.DictWriter(stats_file, fieldnames=data.keys())
        writer.writerow(data)
    return "Success!"


app.run(debug=1)

