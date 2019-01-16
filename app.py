import csv
import os
from urllib.parse import urlparse

import requests
from flask import Flask, render_template, request, send_from_directory, send_file

app = Flask(__name__)
app.config["FILE_LOCATION"] = os.path.join(os.getcwd(), "csv_files")
API_KEY = "wappalyzer.api.demo.key"


def check_drupal(jsn):
    if len(jsn) == 0:
        return None
    for item in jsn[0]['applications']:
        if item['name'] == 'Drupal':
            return item['versions'][0]


@app.route("/", methods=["POST", "GET"])
def is_drupal():
    version = []
    if request.method == "POST":
        urls = request.form['urls'].split(',')
        if len(urls) > 50:
            return "max length exceeds. Only 50 urls allowed at a time.", 400
        api = "https://api.wappalyzer.com/lookup/v1/"
        headers = {"X-Api-Key": API_KEY}
        filename = os.path.join(app.config["FILE_LOCATION"], f"{request.remote_addr}.csv")
        file = open(filename, 'w')
        writer = csv.writer(file)
        writer.writerow(["URL", "Drupal Version", "Status Code"])
        for url in urls:
            turl = urlparse(url)
            if turl.scheme == "":
                url = f"http://{url}"
            try:
                req = requests.get(url)
                req = requests.get(api, params={"url": url}, headers=headers)
                if req.status_code == 200:
                    version.append((url, check_drupal(req.json()), req.status_code))
                else:
                    version.append((url, None, req.status_code))
            except Exception as e:
                version.append((url, None, "Invalid url."))
            writer.writerow(version[-1])
    return render_template("index.html", urls=version)


@app.route('/return-files', methods=['GET'])
def return_file():
    return send_from_directory(app.config["FILE_LOCATION"], as_attachment=True, filename=f"{request.remote_addr}.csv")


if __name__ == '__main__':
    app.run(debug=True)
