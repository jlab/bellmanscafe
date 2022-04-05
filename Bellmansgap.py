import glob
import json
import os
import subprocess

from flask import Flask, render_template, request

from gapfilesparser import parsegapfiles

app = Flask(__name__)
app.secret_key = "xasdqfghuioiuwqenjdcbjhawbuomcujeq1217846421kopNSJJGWmc8u29"

# Variablen
exlist = []
ex = ""
gra = ""
alg1 = ""
operator = ""
alg2 = ""
operator2 = ""
alg3 = ""
res = ""
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

inputreminderlist = []

operator_letter = ""
operator_letter2 = ""

user_form_input = []


# route for the start page "/"
@app.route("/")
def home():
    return render_template("index.html")


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
        "operator": "",
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
        global operator
        global alg2
        global operator2
        global alg3
        global res
        global gapfiles
        global dirstr
        global algdict
        global infotextsdict
        global inputstringsnumberdict
        global inputreminderlist
        global operator_letter
        global operator_letter2

        # values from the form/combo-boxes are saved in the variables here
        # some of it might be old and unnecessary by now
        program = request.form.get('program')
        exlist = []
        n = inputstringsnumberdict[program]
        for i in range(1, n + 1):
            requeststring = "ex" + str(i)
            exlist.append(request.form.get(requeststring))
        gra = request.form.get('gra')
        alg1 = request.form.get('alg1')
        operator = request.form.get('operator')
        alg2 = request.form.get('alg2')
        operator2 = request.form.get('operator2')
        alg3 = request.form.get('alg3')

        '''
         each of the inputs are saved (again)
         the dictionary user_form_input
         is later returned to the html page in order
         to display the selection that the user had made before pressing submit
        '''
        user_form_input["program"] = request.form["program"]
        for i in range(1, n + 1):
            requeststring = "ex" + str(i)
            user_form_input[requeststring] = request.form.get(requeststring)
        for param in ["gra", "alg1", "operator", "alg2", "operator2", "alg3"]:
            user_form_input[param] = request.form[param]

        '''
        additionally a list of strings is built to display
        the previous selection (before pressing submit)
        in the results part of the page
        '''
        inputreminderlist = []
        if program != "":
            inputreminderlist.append("Your program was: " + program + "<br>")
        if gra != "":
            inputreminderlist.append("Your grammar was: " + gra + "<br>")
        if alg1 != "":
            inputreminderlist.append("Your first algebra was: "
                                     + alg1 + "<br>")
        if operator != "":
            inputreminderlist.append("Your operator was: "
                                     + operator + "<br>")
        if alg2 != "":
            inputreminderlist.append("Your second algebra was: "
                                     + alg2 + "<br>")
        if operator2 != "":
            inputreminderlist.append("Your second operator was: "
                                     + operator2 + "<br>")
        if alg3 != "":
            inputreminderlist.append("Your third algebra was: "
                                     + alg3 + "<br>")

        if len(inputreminderlist) == 0:
            inputreminderlist.append("You have not selected anything.")

    # Algebra (single algebra)
    if len(exlist) != 0 and program != "" and gra != "" \
            and alg1 != "" and alg2 == "" and alg3 == "":

        # calculategapc() is used to return the result to the variable res
        command = "" + alg1
        name = "" + alg1
        res = calculategapc(program, command, name, exlist)

        '''
        variables that are important for building
        the result part of the page and the previous
        selection of the combo-boxes
        is returned back to the html page here
        some of these variables might be outdated and
        unnecessary to return by now, further cleanup will follow
        '''
        return render_template(
            "bellman.html", result=res,
            program=program, gra=gra,
            gapfiles=json.dumps(gapfiles),
            gramdict=json.dumps(gramdict),
            algdict=json.dumps(algdict),
            infotextsdict=json.dumps(infotextsdict),
            inputstringsnumberdict=inputstringsnumberdict,
            inputreminderlist=inputreminderlist, exlist=exlist,
            user_form_input=json.dumps(user_form_input))

    # Algebraprodukt (two algebras)
    elif len(exlist) != 0 and program != "" and gra != "" \
            and alg1 != "" and operator != "" and alg2 != "" and alg3 == "":

        # "*" "/" "%" "^" "." "|"
        map_operator_letter = {
            '*': 'l',
            '/': 'i',
            '%': 'c',
            '': 'p',
            '.': 't',
            '|': 'o'
        }
        operator_letter = map_operator_letter.get(operator, None)

        command = "" + alg1 + operator + alg2
        name = alg1 + "_" + operator_letter + "_" + alg2
        res = calculategapc(program, command, name, exlist)

        '''
        variables that are important for building
        the result part of the page and the previous
        selection of the combo-boxes
        is returned back to the html page here
        some of these variables might be outdated and
        unnecessary to return by now, further cleanup will follow
        '''
        return render_template(
            "bellman.html", result=res,
            program=program, gra=gra,
            gapfiles=json.dumps(gapfiles),
            gramdict=json.dumps(gramdict),
            algdict=json.dumps(algdict),
            infotextsdict=json.dumps(infotextsdict),
            inputstringsnumberdict=inputstringsnumberdict,
            inputreminderlist=inputreminderlist, exlist=exlist,
            user_form_input=json.dumps(user_form_input))

    # Algebraprodukt (three algebras)
    elif len(exlist) != 0 and program != "" and gra != "" \
            and alg1 != "" and operator != "" and alg2 != "" and alg3 != "":

        # "*" "/" "%" "^" "." "|"
        map_operator_letter = {
            '*': 'l',
            '/': 'i',
            '%': 'c',
            '': 'p',
            '.': 't',
            '|': 'o'
        }
        operator_letter = map_operator_letter.get(operator, None)
        operator_letter2 = map_operator_letter.get(operator2, None)

        command = "" + alg1 + operator + alg2 + operator2 + alg3
        name = alg1 + "_" + operator_letter + "_" + alg2 \
            + "_" + operator_letter2 + "_" + alg3
        res = calculategapc(program, command, name, exlist)

        '''
        variables that are important for building
        the result part of the page and the previous
        selection of the combo-boxes
        is returned back to the html page here
        some of these variables might be outdated and
        unnecessary to return by now, further cleanup will follow
        '''
        return render_template(
            "bellman.html", result=res,
            program=program, gra=gra,
            gapfiles=json.dumps(gapfiles),
            gramdict=json.dumps(gramdict),
            algdict=json.dumps(algdict),
            infotextsdict=json.dumps(infotextsdict),
            inputstringsnumberdict=inputstringsnumberdict,
            inputreminderlist=inputreminderlist, exlist=exlist,
            user_form_input=json.dumps(user_form_input))

    '''
    if this return statement is reached
    then at least one combo-box necessary
    for execution was not selected/left on the default value
    some of these variables might be outdated
    and unnecessary to return by now, further cleanup will follow
    '''
    return render_template(
        "bellman.html", program=program,
        gra=gra, gapfiles=json.dumps(gapfiles),
        gramdict=json.dumps(gramdict),
        algdict=json.dumps(algdict),
        infotextsdict=json.dumps(infotextsdict),
        inputstringsnumberdict=inputstringsnumberdict,
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
        print("There was an error")
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
            print("An error has occured at subprocess #2!")
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
