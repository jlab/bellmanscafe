import os
import sys

from flask import Flask, render_template, request, send_file
import logging

from bellmanscafe.cafe import obtain_cafe_settings
from bellmanscafe.parse_gapl import get_gapc_programs
from bellmanscafe.execute import compile_and_run_gapc

# the Cafe shall let users interact with a collection of Bellman's GAP
# programs like Needleman-Wunsch or ElMamun. The FP_GAPUSERSOURCES variable
# must point to the path containing these sources.
PREFIX_GAPUSERSOURCES = "../ADP_collection/"

# the ADP_collection repository contains a directory "Resources" which contains
# static content for the cafe, e.g. images. To serve these, we need a symlink
# from flask static dir into the Resources subdir of the repo.
if not os.path.exists("static/Resources"):
    os.symlink("../" + PREFIX_GAPUSERSOURCES + "Resources", "static/Resources")

# user submission leads to compilation and execution of new algera products
# if the user re-submits the same algebra product (also called instance) it
# does not need to be re-computed, therefore we are using a cache. JUST this
# instance with user inputs have to be run.
PREFIX_CACHE = "DOCKER/bcafe_cache/"

app = Flask(__name__)
app.secret_key = "xasdqfghuioiuwqenjdcbjhawbuomcujeq1217846421kopNSJJGWmc8u29"

logging.basicConfig(
    # filename='bellmansgap.log',
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s')

# number of allowed algebras
MAX_ALGEBRAS = 5

settings = obtain_cafe_settings(PREFIX_CACHE, PREFIX_GAPUSERSOURCES, verbose=app.logger)
gapl_programs = get_gapc_programs(settings['paths']['gapc_programs'])


# route for the start page "/"
@app.route("/")
def home():
    return render_template("index.html")


# route for downloading a file
@app.route("/<filename>/download")
def download_file(filename):
    p = filename
    return send_file(os.path.join(PREFIX_GAPUSERSOURCES, p),
                     as_attachment=True)

# route for the bellman page "/bellman"
@app.route("/bellman", methods=["GET", "POST"])
def bellman():
    user_input = dict()

    # This if statement only occurs
    # after the user pressed the submit button
    if request.method == 'POST':
        for (key, value) in request.form.items():
            if key in user_input.keys():
                raise ValueError("key collision")
            user_input[key] = value

        results = compile_and_run_gapc(gapl_programs, user_input, settings, MAX_ALGEBRAS, limit_candidate_trees=20, verbose=app.logger)

    return render_template(
        "bellman.html", programs=gapl_programs, max_algebras=MAX_ALGEBRAS, settings=settings, user_input=user_input)





# route for the support page
@app.route("/support")
def support():
    return render_template('support.html')


if __name__ == "__main__":
    app.run(debug=True)
