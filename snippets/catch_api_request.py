from flask import Flask, request
import csv
import time


app = Flask(__name__)
save_file_path = "./logs/api_requests_archer_dummy.csv"


@app.route("/sumbit-opportunity", methods=["POST"])
def hello_world():
    data = dict(request.args)
    data["recvTimestamp"] = int(time.time())
    with open(save_file_path, "a") as stats_file:
        writer = csv.DictWriter(stats_file, fieldnames=data.keys())
        writer.writerow(data)
    return "Success!"


app.run(debug=1)

