import glob
import json
import os
import shutil
import subprocess

from flask import Flask, render_template, request, send_file

from gapfilesparser import parsegapfiles

app = Flask(__name__)
app.secret_key = "xasdqfghuioiuwqenjdcbjhawbuomcujeq1217846421kopNSJJGWmc8u29"

# Variablen
exlist = []
ex = ""
gra = ""
alg1 = ""
operator1 = ""
alg2 = ""
operator2 = ""
alg3 = ""
algslist = []
operatorslist = []
res = []
dirstr = ""
# glob.glob('*.gap') returns a list of names of
# all files in the directory that end on ".gap"
# the list is then sorted
gapfiles = sorted(glob.glob('*.gap'))
program = ""

returndict = parsegapfiles(gapfiles)

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
    return send_file(p, as_attachment=True)


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
        global alg1
        global operator1
        global alg2
        global operator2
        global alg3
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
        n = inputstringsnumberdict[program]
        for i in range(1, n + 1):
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

        alg1 = request.form.get('alg1')
        operator1 = request.form.get('operator1')
        alg2 = request.form.get('alg2')
        operator2 = request.form.get('operator2')
        alg3 = request.form.get('alg3')

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
        for i in range(1, n + 1):
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
            command = "" + algslist[not_empty_algs_indices[0]]
            name = "" + algslist[not_empty_algs_indices[0]]
            res = calculategapc(program, command, name, exlist)

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
                user_form_input=json.dumps(user_form_input))

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
            res = calculategapc(program, command, name, exlist)

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
                user_form_input=json.dumps(user_form_input))

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
        user_form_input=json.dumps(user_form_input))


'''
this function executes three commands in the shell
and returns the result of the last command
the first command is the gapc tool itself,
the second is the make command
and the third is the executable
that was generated by the previous command
'''


def calculategapc(program, command, name, exlist):
    # dirstr is the string of the directory
    # where generated files regarding this program are safed
    dirstr = "computed_" + program
    res = []

    # this is the executed commandstring
    commandstring = 'gapc -p ' + command \
                    + ' -o ' + dirstr + '/' + name + '_gapc.cc ' \
                    + program + '.gap' + ' 2>&1'
    pro1_returncode = 0

    # gapc Command
    # if this combination of algebras and operator
    # has not been computed for this program yet it will be computed
    if not os.path.exists(dirstr + "/" + name + "_gapc.cc"):
        # if the directory that holds the created files
        # does not exist yet for this program, it will be created
        if not os.path.exists(dirstr):
            os.makedirs(dirstr)
        # the commandstring is executed with subprocess.run()
        pro1 = subprocess.run(
            commandstring, shell=True, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # the returncode will be used to check
        # if the process has run successfully
        pro1_returncode = pro1.returncode
        # the result of the process is saved
        # in list1 and appended to the res list
        list1 = pro1.stdout.splitlines()
        list1.insert(0, "<b>Command</b>: " + commandstring)
        res.append(list1)
    # if this combination of algebras and operator has
    # already been computed, it will not be computed again
    else:
        list1 = []
        list1.append("<b>Command</b>: " + commandstring)
        res.append(list1)
        list2 = ["An error has occured during "
                 "the execution of the gapc command."]
        res.append(list2)
        list3 = ["An error has occured during "
                 "the execution of the gapc command."]
        res.append(list3)

    # The header files necessary for execution will be
    # copied to the destination folder (and overwritten).

    for f in headersdict[program]:
        shutil.copy(f, dirstr)
    # further commands will be executed
    # from within the directory to which
    # the files have been saved
    os.chdir("./" + dirstr)

    # the commandstring is now rebuild as a make command
    commandstring = "make -f " + name + "_gapc.mf" + " 2>&1"
    # if the returncode was not 0, an error must have occured,
    # this is however not handled yet,
    # rather the rest of the code is just not executed in that case
    if pro1_returncode != 0:
        list2 = ["An error has occured during the "
                 "execution of the gapc command."]
        res.append(list2)
        list3 = ["An error has occured during the "
                 "execution of the gapc command."]
        res.append(list3)
    else:
        # if no error occured in process 1,
        # process 2 is started via subprocess.run
        pro2 = subprocess.run(
            commandstring, shell=True, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # the results of the make command are saved
        # in list2, which is appended to the res list
        list2 = pro2.stdout.splitlines()
        list2.insert(0, "<b>Command</b>: " + commandstring)
        res.append(list2)

        # since the third command takes in a string input
        # directly typed in by the user
        # a commandlist is built instead of the commandstring
        commandlist = []
        ex = ""
        commandlist.append("./" + name + "_gapc")
        for exstring in exlist:
            commandlist.append(exstring)
            ex += '"'
            ex += exstring
            ex += '"'
            ex += " "
        # commandlist.append("2>&1")

        # the commandstring will also be built,
        # but will only be displayed in the result section of the page
        # and is not directly used for executing the subprocess
        commandstring = "./" + name + "_gapc " + ex + " 2>&1"
        # ( ulimit -t 1; ./a.out )
        # commandstring = "( ulimit -t 0; " + commandstring + " )"

        # if an error occured in process 2, then process 3 will not be executed
        if pro2.returncode != 0:
            list3 = ["An error has occured during the execution "
                     "of the make command."]
            res.append(list3)
        else:
            '''
            using a commandlist instead of a commandstring
            is supposed to act as a barrier for hacking attempts,
            with a commandlist the first element
            is interpreted as the program or command,
            while the rest of the elements are interpreted as arguments
            or parameters to that program or command,
            therefore shell commands in the inputstring
            are not interpreted as commands but rather as arguments
            to the executable command here
            this has however not been tested for this server yet
            '''
            pro3 = subprocess.run(
                commandlist, text=True, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            list3 = pro3.stdout.splitlines()
            list3.insert(0, "<b>Command</b>: " + commandstring)
            list3.insert(1, "<b>Output</b> :")
            res.append(list3)
    # after all three commands have been executed,
    # we return to the original folder and
    # the resulting list of strings is returned
    os.chdir("..")
    return res


# route for the support page
@app.route("/support")
def support():
    return render_template('support.html')


if __name__ == "__main__":
    app.run(debug=True)
