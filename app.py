from flask import Flask, render_template, request, abort, jsonify
import requests

app = Flask(__name__)

API_KEY = "wappalyzer.api.demo.key"


def check_drupal(jsn):
    if len(jsn) == 0:
        return None
    for item in jsn[0]['applications']:
        if item['name'] == 'Drupal':
            return item['versions'][0]


# @app.route('/')
# def index():
#     return render_template("index.html")


@app.route("/", methods=["POST", "GET"])
def is_drupal():
    version = []
    if request.method == "POST":
        urls = request.form['urls'].split(',')
        if len(urls) > 50:
            return "max length exceeds. Only 50 urls allowed at a time.",400
        api = "https://api.wappalyzer.com/lookup/v1/"
        headers = {"X-Api-Key": API_KEY}
        for url in urls:
            req = requests.get(api, params={"url": url}, headers=headers)
            if req.status_code == 200:
                version.append((url, check_drupal(req.json())))
            else:
                version.append((url, None))
    return render_template("index.html", urls=version)
    # abort(400)


if __name__ == '__main__':
    app.run(debug=True)
    var1 = 1
