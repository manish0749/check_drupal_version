import csv
from urllib.parse import urlparse

import requests
from flask import Flask, render_template, request, send_from_directory

from settings import *

app = Flask(__name__)
app.config["FILE_LOCATION"] = CSV_LOCATIONS


def wapp(jsn):
    print(jsn)
    if len(jsn) == 0:
        return None
    for item in jsn[0]['applications']:
        if item['name'] == 'Drupal':
            return item['versions'][0]


def check_drupal_version(url, api, headers):
    turl = urlparse(url)
    if turl.scheme == "":
        url = "http://{}".format(url)
    try:
        req = requests.get(url, timeout=REQUEST_TIMEOUT, headers=headers)
        if req.status_code < 400:
            req = requests.get(api, params={"url": url}, headers=headers)
            if req.status_code == 200:
                return url, wapp(req.json()), req.status_code
        return url, None, req.status_code
    except Exception as e:
        app.logger.error(e)
        return url, None, "Invalid url."


@app.route("/", methods=["POST", "GET"])
def is_drupal():
    version = []
    if request.method == "POST":
        urls = request.form['urls'].split('\n')
        if len(urls) > 50:
            return "max length exceeds. Only 50 urls allowed at a time.", 400
        api = "https://api.wappalyzer.com/lookup/v1/"
        headers = {"X-Api-Key": API_KEY, "User-Agent": USER_AGENT}
        filename = os.path.join(app.config["FILE_LOCATION"], "{}.csv".format(request.remote_addr))
        file = open(filename, 'w')
        writer = csv.writer(file)
        writer.writerow(["URL", "Drupal Version", "Status Code"])
        for url in urls:
            for item in url.split(' '):
                version.append(check_drupal_version(item, api, headers))
                writer.writerow(version[-1])
        file.close()
    return render_template("index.html", urls=version)


@app.route('/return-files', methods=['GET'])
def return_file():
    return send_from_directory(app.config["FILE_LOCATION"], as_attachment=True,
                               filename="{}.csv".format(request.remote_addr))


if __name__ == '__main__':
    app.run(debug=True)
