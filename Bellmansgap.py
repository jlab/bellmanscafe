import glob
import json
import os
import shutil
import subprocess
import hashlib
import logging
import base64

from flask import Flask, render_template, request, send_file

from gapfilesparser import parsegapfiles, get_gapc_version, \
                           get_repo_commithash


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

# obtain gapc version number to prefix cache prefix. Thus, updated gapc
# compiler will automatically lead to new cache
GAPC_VERSION = get_gapc_version(app)
PREFIX_CACHE = os.path.join(PREFIX_CACHE, 'gapc_v%s' % GAPC_VERSION)
REPO_VERSION = get_repo_commithash(app, PREFIX_GAPUSERSOURCES)
CAFE_VERSION = get_repo_commithash(app, "./")

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
        for i in range(1, len(inputstringsnumberdict[program]) + 1):
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
        for i in range(1, len(inputstringsnumberdict[program]) + 1):
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

        user_form_input['plot_grammar'] = request.form.get('plot_grammar')
        user_form_input['outside_grammar'] = request.form.get(
                'outside_grammar')

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
                gra,
                command, os.path.join(PREFIX_GAPUSERSOURCES,
                                      program + ".gap"),
                PREFIX_CACHE,
                exlist,
                int(request.form.get('plot_grammar'))
                if request.form.get('plot_grammar') is not None else 1,
                bool(request.form.get('outside_grammar')),
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
                repo_hash=REPO_VERSION,
                cafe_hash=CAFE_VERSION,
                plot_grammar_level=request.form.get('plot_grammar'),
                outside_grammar=request.form.get('outside_grammar'))

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
                gra,
                command,
                os.path.join(PREFIX_GAPUSERSOURCES, program + ".gap"),
                PREFIX_CACHE,
                exlist,
                int(request.form.get('plot_grammar'))
                if request.form.get('plot_grammar') is not None else 1,
                bool(request.form.get('outside_grammar')),
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
                repo_hash=REPO_VERSION,
                cafe_hash=CAFE_VERSION)

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
        repo_hash=REPO_VERSION,
        cafe_hash=CAFE_VERSION)


def read_exit_status_file(fp):
    """Read a file into which the exit code has been written.

    Parameters
    ----------
    fp : str
        Filepath to file containing the numeric exit status.

    Returns
    -------
    int = the exit status

    Note
    ----
    Also returns 1, i.e. error, if
        - file path does not exist
        - file exists, but has no content
    """
    if not os.path.exists(fp):
        return 1
    with open(fp, 'r') as f:
        lines = f.readlines()
        if len(lines) < 1:
            return 1
        else:
            try:
                return int(lines[0].strip())
            except ValueError:
                return 1


def modify_tikz_file(fp_orig, fp_limited, max_candidates=20):
    with open(fp_orig, 'r') as fR:
        candidate_counter = 0
        with open(fp_limited, 'w') as fW:
            for line in fR.readlines():
                if line.startswith("\\end{tikzpicture}"):
                    candidate_counter += 1
                fW.write(line)
                if candidate_counter >= max_candidates:
                    fW.write('\\end{document}\n')
                    break


def compile_and_run_gapc(grammar: str, algproduct: str, fp_gapfile: str,
                         prefix_cache, userinputs: [str],
                         plot_grammar_level: int = 1, outside: bool = False,
                         fps_headerfiles: [str] = [],
                         limit_candidate_trees: int = 20):
    """Compiles a binary for a given instance (aka algebra product).

    Parameters
    ----------
    grammar : str
        The user selected grammar.

    algproduct : str
        The algebra product to be compiled, e.g. "alg_score * alg_enum".

    fp_gapfile : str
        File path location of the user gap source file.

    prefix_cache : str
        Directory to used to cache compile product.

    userinputs : [str]
        List of user input(s) for tracks of grammar.

    plot_grammar_level : int
        Determines the level of detail when plotting the grammar.

    outside : bool
        Activates automatic generation of outside grammar generation.

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
    REPO_VERSION = get_repo_commithash(app, PREFIX_GAPUSERSOURCES)

    # the instance is the application of the algebra product to the grammar
    instance = '%s(%s)' % (grammar, algproduct)
    hash_instance = hashlib.md5(("%s_%i_%s" % (
        instance, plot_grammar_level, outside)).encode('utf-8')).hexdigest()
    fp_workdir = os.path.join(prefix_cache, hash_instance)
    app.logger.info('working directory for instance "%s" is "%s"' % (
        instance, fp_workdir))

    param_outside = " --outside_grammar ALL " if outside else ""
    steps = {
        # 0) inject instance bcafe to original *.gap source file (as it might
        #    not be defined)
        # 1) transpiling via gapc
        'gapc': ('echo "instance bcafe=%s;" >> "%s" '
                 '&& gapc -i "bcafe" --plot-grammar %i %s %s ') % (
            instance, os.path.basename(fp_gapfile), plot_grammar_level,
            param_outside,
            os.path.basename(fp_gapfile)),

        # 2) convert grammar plot into gif
        'dot': 'dot -Tgif out.dot -o grammar.gif',

        # 3) compiling c++ into binary
        'make': 'make -f out.mf',

        # 4) run the compiled binary with user input (not cached)
        'run': '../out %s' % ' '.join(map(lambda x: '"%s"' % x, userinputs)),

        # 5) OPTIONAL: if algebra product uses tikZ, images will be rendered
        'tikz': '/usr/bin/time -v -o pdflatex.benchmark pdflatex tikz.tex '
                '2>> tikz.err && '
                '/usr/bin/time -v -o pdfmake.benchmark make -f tikz.makefile '
                '2>> tikz.err && '
                'mv -v tikz.log tikz.out 2>> tikz.err'
    }
    steps = {name: 'time -v -o "%s.benchmark" %s > %s.out 2> %s.err' % (
             name, cmd, name, name) if name not in ['tikz'] else cmd
             for name, cmd
             in steps.items()}

    if os.path.exists(fp_workdir):
        # if a matching cache dir exists, we test if the source file contents
        # has changed. This might be due to updates in the ADP_collections repo
        invalid_cache = False
        for fp_src in [fp_gapfile] + fps_headerfiles:
            fp_dst = os.path.join(fp_workdir, os.path.basename(fp_src))
            if os.path.exists(fp_dst):
                dst = fp_dst
                if fp_src == fp_gapfile:
                    # ignore last line of gap source file, since this is the
                    # injected instance
                    dst = '<(head %s -n -1)' % fp_dst
                p_diff = subprocess.run(
                    'diff %s %s' % (fp_src, dst), shell=True, text=True,
                    executable='/bin/bash')
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
            if name in ["run", "tikz"]:
                # don't run the compiled binary in here since it shall not be
                # part of the cache
                continue
            child = subprocess.run(cmd, shell=True, text=True, cwd=fp_workdir)
            # we explicitly store the exit status into an extra file ... to
            # better indicate errors in the webpage
            with open(os.path.join(fp_workdir,
                                   '%s.exitstatus' % name), 'w') as f:
                f.write('%i\n' % child.returncode)
            app.logger.info('executing (in %s) "%s"' % (fp_workdir, cmd))

    inputs_hash = hashlib.md5(''.join(userinputs).encode('utf-8')).hexdigest()
    fp_binary_workdir = os.path.join(fp_workdir, 'run_%s' % inputs_hash)
    uses_tikz = False
    if not os.path.exists(fp_binary_workdir):
        os.makedirs(fp_binary_workdir, exist_ok=True)

        # execute the binary with user input(s)
        child = subprocess.run(steps['run'], shell=True, text=True,
                               cwd=fp_binary_workdir)
        app.logger.info('no cached results found, thus executing (in %s) "%s"'
                        % (fp_binary_workdir, steps['run']))
        with open(os.path.join(fp_binary_workdir, 'run.exitstatus'), 'w') as f:
            f.write('%i\n' % child.returncode)

        if child.returncode == 0:
            with open(os.path.join(fp_binary_workdir, 'run.out'), 'r') as f:
                if 'documentclass' in f.readlines()[0]:
                    uses_tikz = True
                    app.logger.info('found tikZ tree descriptions.')

                    # modify original binary stdout such that it contains
                    # at most limit_candidate_trees many trees to limit server
                    # workload when compiling individual candidate PNGs
                    modify_tikz_file(
                        os.path.join(fp_binary_workdir, 'run.out'),
                        os.path.join(fp_binary_workdir, 'tikz.tex'),
                        limit_candidate_trees)

                    child = subprocess.run(steps['tikz'], shell=True,
                                           text=True, cwd=fp_binary_workdir)
                    app.logger.info(
                        'executing (in %s) "%s"' % (fp_binary_workdir,
                                                    steps['tikz']))
                    with open(os.path.join(fp_binary_workdir,
                                           'tikz.exitstatus'), 'w') as f:
                        f.write('%i\n' % child.returncode)
    else:
        uses_tikz = os.path.exists(os.path.join(fp_binary_workdir, 'tikz.tex'))
        app.logger.info('found cached binary results.')

    report = []
    for name, cmd in steps.items():
        fp_cache = fp_workdir
        if name in ["run", "tikz"]:
            fp_cache = fp_binary_workdir
        if (name == "tikz") and (uses_tikz is False):
            report.append([[], 0])
            continue
        exit_status = None
        rep = []
        rep.append('<b>Command</b>: %s' % cmd)
        with open(os.path.join(fp_cache, '%s.out' % name)) as f:
            rep.extend(f.readlines())
        with open(os.path.join(fp_cache, '%s.err' % name)) as f:
            rep.extend(f.readlines())
        # read exit status of step
        exit_status = read_exit_status_file(
            os.path.join(fp_cache, '%s.exitstatus' % name))
        if (name == 'tikz') and uses_tikz:
            rep = []
            for rank, fp_candidate in enumerate(sorted(
                    glob.glob(os.path.join(fp_cache, 'tikz-figure*.png')),
                    key=lambda x: int(x.split('figure')[1].split('.')[0]))):
                if (os.stat(fp_candidate).st_size > 0):
                    with open(fp_candidate, "rb") as image:
                        rep.append(base64.b64encode(image.read()).decode(
                            'utf-8'))
                if rank+1 >= limit_candidate_trees:
                    app.logger.info(
                        ('number of candidates exceeds displaying limit of '
                         'top %i!') % limit_candidate_trees)
                    break

        # don't add dot execution to report, since there is no tab yet on the
        # website
        if name not in ['dot']:
            report.append([rep, exit_status])

    # a bit hacky, but this is to serve dynamically generated images from cache
    # which is not directly exposed to the web. We load the GIF content as
    # base64 encoded string and paste this directly as src="" into an image tag
    # Note: previous compile errors might lead to a missing out.dot file!
    fp_plot = os.path.join(fp_workdir, "grammar.gif")
    if os.path.exists(fp_plot) and (os.stat(fp_plot).st_size > 0):
        with open(fp_plot, "rb") as image:
            report.append([base64.b64encode(image.read()).decode('utf-8'), 0])
    else:
        report.append(["error", 1])

    return report


# route for the support page
@app.route("/support")
def support():
    return render_template('support.html')


if __name__ == "__main__":
    app.run(debug=True)
