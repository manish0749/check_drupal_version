import csv
from urllib.parse import urlparse
import model

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
            version = "D" if len(item['versions']) == 0 else "D{}".format(item['versions'][0])
            app.logger.info("wappalyzer found drupal version : {}".format(version))
            return version


def check_drupal_version(url, api, headers,ip):
    turl = urlparse(url)
    if turl.scheme == "":
        url = "http://{}".format(url)
    try:
        req = requests.get(url, timeout=REQUEST_TIMEOUT, headers=headers)
        version=None
        if req.status_code < 400:
            app.logger.info("wappalyzer request to: {}".format(url))
            req = requests.get(api, params={"url": url}, headers=headers)
            app.logger.info("wappalyzer reponded with status code: {}".format(req.status_code))
            if req.status_code == 200:
                version=wapp(req.json())
                # return url, version, req.status_code
        model.insert(ip,url,version,req.status_code)
        return url, version, req.status_code
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
        cnt=0
        ip=request.environ['REMOTE_ADDR']
        for url in urls:
            for item in url.split(' '):
                cnt+=1
                item = item.strip()
                if len(item) == 0:
                    continue
                version.append(check_drupal_version(item, api, headers,ip))
                writer.writerow(version[-1])
            if cnt>=50:
                break
        file.close()
    return render_template("index.html", urls=version)


@app.route('/return-files', methods=['GET'])
def return_file():
    return send_from_directory(app.config["FILE_LOCATION"], as_attachment=True,
                               filename="{}.csv".format(request.remote_addr))


if __name__ == '__main__':
    app.run(debug=True)
