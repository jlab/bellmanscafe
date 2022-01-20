import os, subprocess, signal, glob, json
from flask import Flask, redirect, url_for, render_template, request, session
from gapfilesparser import parsegapfiles

app = Flask(__name__)
app.secret_key = "xasdqfghuioiuwqenjdcbjhawbuomcujeq1217846421kopNSJJGWmc8u29"

#Variablen
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
program=""
gramdict={}
algdict={}
infotextsdict={}
returndict={}

returndict = parsegapfiles(gapfiles)

gramdict = returndict["gramdict"]
algdict = returndict["algdict"]
infotextsdict = returndict["infotextsdict"]

@app.route("/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form["nm"]
        session["user"] = user
        return redirect(url_for("home"))
    else:
        if "user" in session:
            return redirect(url_for("home"))
        else:       
            return render_template("login.html")


@app.route("/home")
def home():
    if "user" in session:
        user = session["user"]
        return render_template("index.html", usr=user)
    else: 
        return redirect(url_for("login"))


@app.route("/bellman", methods=["GET", "POST"])
def bellman():
    if request.method == 'POST':
        global ex
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
        
        ex= request.form.get('ex')
        program= request.form.get('program')
        gra= request.form.get('gra')
        alg1= request.form.get('alg1')
        operator= request.form.get('operator')
        alg2= request.form.get('alg2')
    
    #Algebra
    if ex != "" and program != "" and gra != "" and alg1 != "" and alg2 == "":
        
        command = ""+alg1
        name= ""+alg1
        res = calculategapc(program, command, name)
        
        return render_template("bellman.html", result=res, program=program, gra=gra, gapfiles=json.dumps(gapfiles), gramdict=json.dumps(gramdict), algdict=json.dumps(algdict), infotextsdict=json.dumps(infotextsdict))
        
        #Algebraprodukt
    elif ex != "" and program != "" and gra != "" and alg1 != "" and operator != "" and alg2 != "":
        
        command = ""+alg1+operator+alg2
        name= alg1+"_"+alg2
        res = calculategapc(program, command, name)
        
        return render_template("bellman.html", result=res, program=program, gra=gra, gapfiles=json.dumps(gapfiles), gramdict=json.dumps(gramdict), algdict=json.dumps(algdict), infotextsdict=json.dumps(infotextsdict))


    return render_template("bellman.html", program=program, gra=gra, gapfiles=json.dumps(gapfiles), gramdict=json.dumps(gramdict), algdict=json.dumps(algdict), infotextsdict=json.dumps(infotextsdict))


def calculategapc(program, command, name):
    dirstr="computed_"+program
    res = []
    
    commandstring = 'gapc -p '+command+' -o '+dirstr+'/'+name+'_gapc.cc '+program+'.gap'+' 2>&1'
    if not os.path.exists (dirstr+"/"+name+"_gapc.cc"):
        if not os.path.exists(dirstr):
            os.makedirs(dirstr)
        pro1 = subprocess.run(commandstring, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        list1 = pro1.stdout.splitlines()
        list1.insert(0, "Output of Command: " + commandstring)
        res.append(list1)
    else:
    	list1 = []
    	list1.append("Command: " + commandstring)
    	infostring = "The file " + name + "_gapc.cc" + " already exists on the server, therefore computing it again using the gapc command is omitted."
    	list1.append(infostring)
    	res.append(list1)
    
    os.chdir("./"+dirstr)
    
    commandstring = "make -f "+name+"_gapc.mf"+" 2>&1"
    pro2 = subprocess.run(commandstring, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    list2 = pro2.stdout.splitlines()
    list2.insert(0, "Output of Command: " + commandstring)
    res.append(list2)
    
    commandstring = "./"+name+"_gapc "+ex+" 2>&1"
    pro3 = subprocess.run(commandstring, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    list3 = pro3.stdout.splitlines()
    list3.insert(0, "Output of Command: " + commandstring)
    res.append(list3)
    
    os.chdir("..")
    return res

@app.route("/result")
def result():
    return render_template('result.html', result=res)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)






