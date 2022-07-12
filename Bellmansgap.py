import glob
import json
import os
import shutil
import subprocess
import hashlib
import logging

from flask import Flask, render_template, request, send_file

from gapfilesparser import parsegapfiles, get_gapc_version, \
                           get_adpcollection_commithash


# the Cafe shall let users interact with a collection of Bellman's GAP
# programs like Needleman-Wunsch or ElMamun. The FP_GAPUSERSOURCES variable
# must point to the path containing these sources.
PREFIX_GAPUSERSOURCES = "../ADP_collection/"

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

# obtain gapc version number to prefix cache prefix. Thus, updated gapc
# compiler will automatically lead to new cache
GAPC_VERSION = get_gapc_version(app)
PREFIX_CACHE = os.path.join(PREFIX_CACHE, 'gapc_v%s' % GAPC_VERSION)
REPO_VERSION = get_adpcollection_commithash(app, PREFIX_GAPUSERSOURCES)

# Variablen
exlist = []
ex = ""
gra = ""
algslist = []
operatorslist = []
res = []
dirstr = ""
# glob.glob('*.gap') returns a list of names of
# all files in the directory that end on ".gap"
# the list is then sorted
FP_GAPFILES = glob.glob(os.path.join(PREFIX_GAPUSERSOURCES, '*.gap'))
gapfiles = sorted(list(map(os.path.basename, FP_GAPFILES)))
program = ""

returndict = parsegapfiles(FP_GAPFILES)

gramdict = returndict["gramdict"]
algdict = returndict["algdict"]
infotextsdict = returndict["infotextsdict"]
inputstringsnumberdict = returndict["inputstringsnumberdict"]
headersdict = returndict["headersdict"]

inputreminderlist = []

operator_letter = ""
operator_letter2 = ""

user_form_input = []

# number of allowed algebras
MAX_ALGEBRAS = 5


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
    # Values of the combo-boxes that
    # the user had selected when submitting is saved in this variable
    global user_form_input
    user_form_input = {
        "program": "",
        "gra": "",
        "alg1": "",
        "operator1": "",
        "alg2": "",
        "operator2": "",
        "alg3": ""
    }

    # This if statement only occurs
    # after the user pressed the submit button
    if request.method == 'POST':
        # all variables are made global,
        # this is a workaround, since initializing the variables as global
        # did not work for some reason
        # further inspection might be necessary
        global ex
        global exlist
        global program
        global gra
        global algslist
        global operatorslist
        global res
        global gapfiles
        global dirstr
        global algdict
        global infotextsdict
        global inputstringsnumberdict
        global headersdict
        global inputreminderlist
        global operator_letter
        global operator_letter2

        # values from the form/combo-boxes are saved in the variables here
        # some of it might be old and unnecessary by now
        program = request.form.get('program')

        # Since multiple inputs are possible an exlist is created
        # containing all submitted inputs.
        exlist = []
        for i in range(1, inputstringsnumberdict[program] + 1):
            requeststring = "ex" + str(i)
            exlist.append(request.form.get(requeststring))

        gra = request.form.get('gra')

        # Since up to 5 algebras are possible an algslist
        # is created containing all submitted algebras.
        algslist = [""] * MAX_ALGEBRAS

        for i in range(1, len(algslist)+1):
            requeststring = "alg" + str(i)
            if (requeststring in request.form):
                algslist[i-1] = request.form.get(requeststring)

        # Since up to 4 operators are possible an operatorslist
        # is created containing all submitted operators.
        operatorslist = [""] * MAX_ALGEBRAS
        # The operator at position 0 will correspond to algebra1,
        # and is therefore alway an empty string.
        # Otherwise the operator at position 1 will correspond
        # to the algebra at position 1, which is algebra2, and so on.
        # This results in each operator being paired with an algebra,
        # with algebra1 always having an empty operator.
        for i in range(1, len(operatorslist)):
            requeststring = "operator" + str(i)
            if (requeststring in request.form):
                operatorslist[i] = request.form.get(requeststring)
            else:
                operatorslist[i] = ""

        # each of the inputs are saved (again),
        # the dictionary user_form_input
        # is later returned to the html page in order
        # to display the selection that the
        # user had made before pressing submit
        for param in ["program", "gra"]:
            user_form_input[param] = request.form[param]
        for i in range(1, inputstringsnumberdict[program] + 1):
            requeststring = "ex" + str(i)
            user_form_input[requeststring] = request.form.get(requeststring)
        for j in range(1, len(algslist)+1):
            requeststring = "alg" + str(j)
            if requeststring in request.form:
                user_form_input[requeststring] = \
                    request.form.get(requeststring)
        for k in range(1, len(operatorslist)+1):
            requeststring = "operator" + str(k)
            if requeststring in request.form:
                user_form_input[requeststring] = \
                    request.form.get(requeststring)

        # additionally a list of strings is built to display
        # the previous selection (before pressing submit)
        # in the results part of the page
        inputreminderlist = []
        if program != "":
            inputreminderlist.append("Your program was: " + program + "<br>")
        if gra != "":
            inputreminderlist.append("Your grammar was: " + gra + "<br>")

        for i in range(1, len(algslist)+1):
            if i == 1:
                inputreminderlist.append("Your algebra "+str(i)+" was: "
                                         + algslist[i-1] + "<br>")
            elif (algslist[i-1] != "" and operatorslist[i-1] != ""):
                inputreminderlist.append("Your operator "+str(i-1)+" was: "
                                         + operatorslist[i-1] + "<br>")
                inputreminderlist.append("Your algebra " + str(i) + " was: "
                                         + algslist[i - 1] + "<br>")
        if len(inputreminderlist) == 0:
            inputreminderlist.append("You have not selected anything.")

    # List of indices of algs that have been selected
    not_empty_algs_indices = \
        [i for i in range(len(algslist)) if algslist[i] != ""]
    # List of indices of operators that have been selected
    not_empty_operators_indices = \
        [i for i in range(len(operatorslist)) if operatorslist[i] != ""]
    # Since there is never an operator before algebra1, the position 0
    # will never appear in not_empty_operators_indices.

    # For exactly one algebra
    if (len(not_empty_algs_indices) == 1):
        if len(exlist) != 0 and program != "" and gra != "":
            # calculategapc() is used to return the result to the variable res
            command = algslist[not_empty_algs_indices[0]]
            name = algslist[not_empty_algs_indices[0]]
            res = compile_and_run_gapc(
                command, os.path.join(PREFIX_GAPUSERSOURCES,
                                      program + ".gap"),
                PREFIX_CACHE,
                exlist,
                [os.path.join(PREFIX_GAPUSERSOURCES, h)
                    for h in headersdict[program]])

            # variables that are important for building
            # the result part of the page and the previous
            # selection of the combo-boxes
            # are returned back to the html page here
            # some of these variables might be outdated and
            # unnecessary to return by now, further cleanup will follow
            return render_template(
                "bellman.html", result=res,
                program=program, gra=gra,
                gapfiles=json.dumps(gapfiles),
                gramdict=json.dumps(gramdict),
                algdict=json.dumps(algdict),
                infotextsdict=json.dumps(infotextsdict),
                inputstringsnumberdict=inputstringsnumberdict,
                headersdict=json.dumps(headersdict),
                inputreminderlist=inputreminderlist, exlist=exlist,
                user_form_input=json.dumps(user_form_input),
                gapc_version=GAPC_VERSION,
                repo_hash=REPO_VERSION)

    # More than one algebra:
    if (len(not_empty_algs_indices) >= 2
            and len(not_empty_operators_indices) >= 1):

        # Only continue if exercises(which is the input of the user)
        # and program and grammar are selected.
        if len(exlist) != 0 and program != "" and gra != "":
            command = ""
            name = ""

            # Operator letter map for the name
            # "*" "/" "%" "^" "." "|"
            map_operator_letter = {
                '*': 'l',
                '/': 'i',
                '%': 'c',
                '^': 'p',
                '.': 't',
                '|': 'o'
            }

            # Iteration through all indices that correspond
            # to an algebra that is not "" and was therefore
            # selected and assembling command and name.
            for index in not_empty_algs_indices:
                # For the very first algebra in the list,
                # regardless of its predecessing operator,
                # only the algebra is added to command and name.
                if not_empty_algs_indices.index(index) == 0:
                    command += algslist[index]
                    name += algslist[index]
                # Then if the algebras index is in the
                # not_empty_operator_indices the operator
                # and algebra are added to command and name.
                # Otherwise the algebra can not be
                # evaluated (without an operator) and is not added
                # to command or name.
                elif (index in not_empty_operators_indices):
                    command += operatorslist[index]\
                               + algslist[index]
                    # For the name the operator has to be
                    # converted to a letter for the file name.
                    operator_letter = \
                        map_operator_letter.get(
                            operatorslist[index], None)
                    name += "_" + operator_letter\
                            + "_" + algslist[index]

            # Once the command and name are assembled,
            # they are used to calculate the result.
            res = compile_and_run_gapc(
                command,
                os.path.join(PREFIX_GAPUSERSOURCES, program + ".gap"),
                PREFIX_CACHE,
                exlist,
                [os.path.join(PREFIX_GAPUSERSOURCES, h)
                    for h in headersdict[program]])

            # variables that are important for building
            # the result part of the page and the previous
            # selection of the combo-boxes
            # are returned back to the html page here
            # some of these variables might be outdated and
            # unnecessary to return by now, further cleanup will follow
            return render_template(
                "bellman.html", result=res,
                program=program, gra=gra,
                gapfiles=json.dumps(gapfiles),
                gramdict=json.dumps(gramdict),
                algdict=json.dumps(algdict),
                infotextsdict=json.dumps(infotextsdict),
                inputstringsnumberdict=inputstringsnumberdict,
                headersdict=json.dumps(headersdict),
                inputreminderlist=inputreminderlist, exlist=exlist,
                user_form_input=json.dumps(user_form_input),
                gapc_version=GAPC_VERSION,
                repo_hash=REPO_VERSION)

    # if this return statement is reached
    # then at least one combo-box necessary
    # for execution was not selected/left on the default value
    # some of these variables might be outdated
    # and unnecessary to return by now, further cleanup will follow
    return render_template(
        "bellman.html", program=program,
        gra=gra, gapfiles=json.dumps(gapfiles),
        gramdict=json.dumps(gramdict),
        algdict=json.dumps(algdict),
        infotextsdict=json.dumps(infotextsdict),
        inputstringsnumberdict=inputstringsnumberdict,
        headersdict=json.dumps(headersdict),
        inputreminderlist=inputreminderlist, exlist=exlist,
        user_form_input=json.dumps(user_form_input),
        gapc_version=GAPC_VERSION,
        repo_hash=REPO_VERSION)


def compile_and_run_gapc(instance: str, fp_gapfile: str, prefix_cache,
                         userinputs: [str], fps_headerfiles: [str] = []):
    """Compiles a binary for a given instance (aka algebra product).

    Parameters
    ----------
    instance : str
        The algebra product to be compiled, e.g. "alg_score * alg_enum".

    fp_gapfile : str
        File path location of the user gap source file.

    prefix_cache : str
        Directory to used to cache compile product.

    userinputs : [str]
        List of user input(s) for tracks of grammar.

    fps_headerfiles : [str]
        List of additional user header files, necessary for C++ compilation.
    """
    # update the global gapc version number as the according ubuntu package
    # might have changed during server execution time
    global GAPC_VERSION
    GAPC_VERSION = get_gapc_version(app)

    # update global commit hash of user repository as it might change during
    # server run time through cron jobs
    global REPO_VERSION
    REPO_VERSION = get_adpcollection_commithash(app, PREFIX_GAPUSERSOURCES)

    hash_instance = hashlib.md5(instance.encode('utf-8')).hexdigest()
    fp_workdir = os.path.join(prefix_cache, hash_instance)
    app.logger.info('working directory is "%s"' % fp_workdir)

    steps = {
        # 1) transpiling via gapc
        'gapc': 'gapc -p "%s" --plot-grammar 1 %s ' % (
            instance, os.path.basename(fp_gapfile)),

        # 2) convert grammar plot into gif
        'dot': 'dot -Tgif out.dot -o grammar.gif',

        # 3) compiling c++ into binary
        'make': 'make -f out.mf',

        # 4) run the compiled binary with user input (not cached)
        'run': './out %s' % ' '.join(map(lambda x: '"%s"' % x, userinputs))
    }
    steps = {name: '%s > %s.out 2> %s.err' % (cmd, name, name)
             for name, cmd
             in steps.items()}

    if os.path.exists(fp_workdir):
        # if a matching cache dir exists, we test if the source file contents
        # has changed. This might be due to updates in the ADP_collections repo
        invalid_cache = False
        for fp_src in [fp_gapfile] + fps_headerfiles:
            fp_dst = os.path.join(fp_workdir, os.path.basename(fp_src))
            if os.path.exists(fp_dst):
                p_diff = subprocess.run('diff %s %s' % (fp_src, fp_dst),
                                        shell=True, text=True)
                if p_diff.returncode != 0:
                    invalid_cache = True
        if invalid_cache:
            shutil.rmtree(fp_workdir)
            app.logger.info('delete outdated cache dir "%s"' % fp_workdir)

    if not os.path.exists(fp_workdir):
        os.makedirs(fp_workdir, exist_ok=True)
        app.logger.info('create working directory "%s"' % fp_workdir)

        # copy *.gap and header source files into working directory
        for fp_src in [fp_gapfile] + fps_headerfiles:
            fp_dst = os.path.join(fp_workdir, os.path.basename(fp_src))
            shutil.copy(fp_src, fp_dst)
            app.logger.info('copy file "%s" to %s' % (fp_src, fp_dst))

        for name, cmd in steps.items():
            if name == "run":
                # don't run the compiled binary in here since it shall not be
                # part of the cache
                continue
            subprocess.run(cmd, shell=True, text=True, cwd=fp_workdir)
            app.logger.info('executing (in %s) "%s"' % (fp_workdir, cmd))

    # execute the binary with user input(s)
    subprocess.run(steps['run'], shell=True, text=True, cwd=fp_workdir)
    app.logger.info('executing (in %s) "%s"' % (fp_workdir, steps['run']))

    report = []
    for name, cmd in steps.items():
        rep = []
        rep.append('<b>Command</b>: %s' % cmd)
        with open(os.path.join(fp_workdir, '%s.out' % name)) as f:
            rep.extend(f.readlines())
        with open(os.path.join(fp_workdir, '%s.err' % name)) as f:
            rep.extend(f.readlines())
        # don't add dot execution to report, since there is no tab yet on the
        # website
        if name not in ['dot']:
            report.append(rep)

    return report


# route for the support page
@app.route("/support")
def support():
    return render_template('support.html')


if __name__ == "__main__":
    app.run(debug=True)
