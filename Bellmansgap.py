import os, subprocess, signal, glob, json
from flask import Flask, redirect, url_for, render_template, request, session
from gapfilesparser import parsegapfiles

app = Flask(__name__)
app.secret_key = "xasdqfghuioiuwqenjdcbjhawbuomcujeq1217846421kopNSJJGWmc8u29"

#Variablen
exlist=[]
ex=""
gapfiles=""
gra=""
alg1=""
operator=""
alg2=""
res=""
dirstr=""
gapfiles= glob.glob('*.gap')
sortedgapfiles= sorted(gapfiles)
gra=""
program="p"
gramdict={}
algdict={}
infotextsdict={}
returndict={}

returndict = parsegapfiles(gapfiles)

gramdict = returndict["gramdict"]
algdict = returndict["algdict"]
infotextsdict = returndict["infotextsdict"]
inputstringsnumberdict = returndict["inputstringsnumberdict"]

inputreminderlist=[]

operator_letter = ""

selected_values_dict = []

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/bellman", methods=["GET", "POST"])
def bellman():
    
    global selected_values_dict
    selected_values_dict = {
        "program":"",
        "gra":"",
        "alg1":"",
        "operator":"",
        "alg2":""
        }
    
    if request.method == 'POST':
        global ex
        global exlist
        global program
        global gra
        global alg1
        global operator
        global alg2
        global res
        global gapfiles
        global dirstr
        global algdict
        global infotextsdict
        global inputstringsnumberdict
        global inputreminderlist
        global operator_letter
        
        program= request.form.get('program')
        exlist=[]
        n=inputstringsnumberdict[program]
        for i in range(1,n+1):
        	requeststring = "ex"+str(i)
        	exlist.append(request.form.get(requeststring))
        gra= request.form.get('gra')
        alg1= request.form.get('alg1')
        operator= request.form.get('operator')
        alg2= request.form.get('alg2')
        
        selected_values_dict["program"] = request.form["program"]
        for i in range(1,n+1):
            requeststring = "ex"+str(i)
            selected_values_dict[requeststring] = request.form.get(requeststring)
        selected_values_dict["gra"] = request.form["gra"]
        selected_values_dict["alg1"] = request.form["alg1"]
        selected_values_dict["operator"] = request.form["operator"]
        selected_values_dict["alg2"] = request.form["alg2"]
        
        print("dictionary Inhalt:")
        print(selected_values_dict)
        
        inputreminderlist = []
        inputreminderlist.append("Your program was: " + program)
        inputreminderlist.append("Your grammar was: " + gra)
        inputreminderlist.append("Your first algebra was: " + alg1)
        inputreminderlist.append("Your operator was: " + operator)
        inputreminderlist.append("Your second algebra was: " + alg2)
    
    #Algebra
    if len(exlist) != 0 and program != "" and gra != "" and alg1 != "" and alg2 == "":
        
        command = ""+alg1
        name= ""+alg1
        res = calculategapc(program, command, name, exlist)
        
        return render_template("bellman.html", result=res, program=program, gra=gra, gapfiles=json.dumps(gapfiles), gramdict=json.dumps(gramdict), algdict=json.dumps(algdict), infotextsdict=json.dumps(infotextsdict), inputstringsnumberdict = inputstringsnumberdict, inputreminderlist=inputreminderlist, exlist=exlist, selected_values_dict=json.dumps(selected_values_dict))
        
    #Algebraprodukt
    elif len(exlist) != 0 and program != "" and gra != "" and alg1 != "" and operator != "" and alg2 != "":
        
        #"*" "/" "%" "^" "." "|"
        if operator == "*":
        	operator_letter="l"
        elif operator == "/":
        	operator_letter = "i"
        elif operator == "%":
        	operator_letter = "c"
        elif operator == "^":
        	operator_letter = "p"
        elif operator == ".":
        	operator_letter = "t"
        elif operator == "|":
        	operator_letter = "o"
        
        command = ""+alg1+operator+alg2
        name= alg1+"_"+operator_letter+"_"+alg2
        res = calculategapc(program, command, name, exlist)
        
        return render_template("bellman.html", result=res, program=program, gra=gra, gapfiles=json.dumps(gapfiles), gramdict=json.dumps(gramdict), algdict=json.dumps(algdict), infotextsdict=json.dumps(infotextsdict), inputstringsnumberdict = inputstringsnumberdict, inputreminderlist=inputreminderlist, exlist=exlist, selected_values_dict=json.dumps(selected_values_dict))


    return render_template("bellman.html", program=program, gra=gra, gapfiles=json.dumps(gapfiles), gramdict=json.dumps(gramdict), algdict=json.dumps(algdict), infotextsdict=json.dumps(infotextsdict), inputstringsnumberdict = inputstringsnumberdict, inputreminderlist=inputreminderlist, exlist=exlist, selected_values_dict=json.dumps(selected_values_dict))


def calculategapc(program, command, name, exlist):
    dirstr="computed_"+program
    res = []
    print("Program: ",program," Exlist: ",exlist)
    
    commandstring = 'gapc -p '+command+' -o '+dirstr+'/'+name+'_gapc.cc '+program+'.gap'+' 2>&1'
    pro1_returncode = 0
    if not os.path.exists (dirstr+"/"+name+"_gapc.cc"):
        if not os.path.exists(dirstr):
            os.makedirs(dirstr)
        pro1 = subprocess.run(commandstring, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        pro1_returncode = pro1.returncode
        list1 = pro1.stdout.splitlines()
        list1.insert(0, "<b>Command</b>: " + commandstring)
        res.append(list1)
    else:
    	list1 = []
    	list1.append("<b>Command</b>: " + commandstring)
    	res.append(list1)
    
    
    os.chdir("./"+dirstr)
    
    
    commandstring = "make -f "+name+"_gapc.mf"+" 2>&1"
    if pro1_returncode != 0:
    	errorstring = "There was an error"
    else:
        pro2 = subprocess.run(commandstring, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        list2 = pro2.stdout.splitlines()
        list2.insert(0, "<b>Command</b>: " + commandstring)
        res.append(list2)
	    
        commandlist = []
        ex = ""
        commandlist.append("./"+name+"_gapc")
        for exstring in exlist:
            commandlist.append(exstring)
            ex += '"'
            ex += exstring
            ex += '"'
            ex+= " "
        #commandlist.append("2>&1")
        
        commandstring = "./"+name+"_gapc "+ex+" 2>&1"
        #( ulimit -t 1; ./a.out )
        commandstring = "( ulimit -t 0; " + commandstring + " )"
	   
        if pro2.returncode != 0:
            erororororor = ""
        else :
        
            pro3 = subprocess.run(commandlist, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            list3 = pro3.stdout.splitlines()
            list3.insert(0, "<b>Command</b>: " + commandstring)
            list3.insert(1, "<b>Output</b> :")
            res.append(list3)
	    
    os.chdir("..")
    return res

@app.route("/result")
def result():
    return render_template('result.html', result=res)


if __name__ == "__main__":
    app.run(debug=True)






