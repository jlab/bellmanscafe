import os

from tempfile import mkstemp
from flask import Flask, render_template, request, send_file
import logging

from bellmanscafe.cafe import obtain_cafe_settings, log
from bellmanscafe.parse_gapl import (get_gapc_programs, parse_gapl)
from bellmanscafe.execute import compile_and_run_gapc


app = Flask(__name__)

logging.basicConfig(
    # filename='bellmansgap.log',
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s')

for fp_config in ['gunicorn.conf.py',
                  os.path.join('instance', 'secret_config.py')]:
    if os.path.exists(fp_config):
        app.config.from_pyfile(fp_config)
log('\nFlask settings:\n' + ('-' * 80) + '\n' +
    '\n'.join(['\t%s: %s' % (_key, app.config[_key])
               for _key
               in sorted(app.config.keys())]) +
    '\n' + ('-' * 80) + '\n', verbose=app.logger, level="info")

# see file bellmanscafe/cafe.py
settings = obtain_cafe_settings(app.config, verbose=app.logger)
log('Cafe settings: %s' % settings, verbose=app.logger, level="info")

# parse *.gap files
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
@app.route("/<path:filename>/download")
def download_file(filename):
    p = filename
    fp_codefile = os.path.join(settings['paths']['gapc_programs'], p)
    if fp_codefile.endswith(".gap"):
        gapl = parse_gapl(fp_codefile)
        if gapl['include_files'] != []:
            # original code file 'includes' from further files
            # produce a combined version for download here
            _, fp_codefile = mkstemp()
            with open(fp_codefile, 'w') as f:
                f.write(''.join(gapl['codelines']))

    return send_file(fp_codefile,
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


# route for downloading a stderr / stdout file of a compilation task
@app.route("/downloadchannel/<cmp_cache>/<run_cache>/<task_channel>")
def download_channel(cmp_cache, run_cache, task_channel):
    path_components = [settings['paths']['prefix_cache']] + \
        [p for p in [cmp_cache, run_cache] if p != '__'] + \
        [task_channel]
    fp_file = os.path.join(*path_components)
    return send_file(fp_file,
                     as_attachment=False, mimetype="text/plain")


# # route for the support page
# @app.route("/support")
# def support():
#     return render_template('support.html')


if __name__ == "__main__":
    app.run(debug=False)
