import os

from flask import Flask, render_template, request, send_file
import logging

from bellmanscafe.cafe import obtain_cafe_settings
from bellmanscafe.parse_gapl import get_gapc_programs
from bellmanscafe.execute import compile_and_run_gapc


app = Flask(__name__)
app.secret_key = "xasdqfghuioiuwqenjdcbjhawbuomcujeq1217846421kopNSJJGWmc8u29"

logging.basicConfig(
    # filename='bellmansgap.log',
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s')

# see file bellmanscafe/cafe.py
settings = obtain_cafe_settings(verbose=app.logger)
gapl_programs = get_gapc_programs(settings['paths']['gapc_programs'])

# the ADP_collection repository contains a directory "Resources" which contains
# static content for the cafe, e.g. images. To serve these, we need a symlink
# from flask static dir into the Resources subdir of the repo.
if not os.path.exists("static/Resources"):
    os.symlink("../" + settings['paths']['gapc_programs'] + "Resources",
               "static/Resources")


# route for the start page "/"
# @app.route("/")
# def home():
#     return render_template("index.html")


# route for downloading a file
@app.route("/<filename>/download")
def download_file(filename):
    p = filename
    return send_file(os.path.join(settings['paths']['gapc_programs'], p),
                     as_attachment=False, mimetype="text/plain")


# route for the bellman page "/bellman"
@app.route("/", methods=["GET", "POST"])
def bellman():
    user_input = dict()
    results = dict()

    # This if statement only occurs
    # after the user pressed the submit button
    if request.method == 'POST':
        for (key, value) in request.form.items():
            if key in user_input.keys():
                raise ValueError("key collision")
            user_input[key] = value

        results = compile_and_run_gapc(gapl_programs, user_input, settings,
                                       verbose=app.logger)

        # update versions collected during compilation
        settings['versions'] = results['versions']

    return render_template(
        "bellman.html", programs=gapl_programs, settings=settings,
        user_input=user_input, results=results)


# # route for the support page
# @app.route("/support")
# def support():
#     return render_template('support.html')


if __name__ == "__main__":
    app.run(debug=True)
