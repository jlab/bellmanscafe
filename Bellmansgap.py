import os, subprocess, signal, glob, json
from flask import Flask, redirect, url_for, render_template, request, session

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
for grafile in gapfiles:
    gramlist = []
    alglist = []
    commentslist = []
    with open(grafile) as myfile:
        is_in_comment = False
        current_comment = ""
        # this only works if algebras are separated by new lines in the .gap files
        for myline in myfile:
            
            # Multiline comments need to start with '/*' on one line
            # and end with '*/\n' on another line
            if myline.startswith('/*'):
                is_in_comment = True
                myline = myline.split("/*")[1]
            if myline.endswith('*/\n'):
                is_in_comment = False
                current_comment += myline.split("*/\n")[0]
                commentslist.append(current_comment)
                current_comment = ""
            if is_in_comment:
                current_comment += myline
                continue
            if myline.startswith("//"):
                commentslist.append(myline.split("//")[1])
                continue
            splitline = myline.split(" ")
            if splitline[0] == "grammar":
                gramlist.append(splitline[1])
            if splitline[0] == "algebra":
                alglist.append(splitline[1])
    gramdict[grafile.split(".")[0]] = gramlist
    algdict[grafile.split(".")[0]] = alglist
    infotextsdict[grafile.split(".")[0]] = commentslist

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
        
        dirstr="computed_"+program
        if not os.path.exists (dirstr+"/"+alg1+"_gapc.cc"):
            if not os.path.exists(dirstr):
                os.makedirs(dirstr)
            pro1 = subprocess.run('gapc -p '+alg1+' -o '+dirstr+'/'+alg1+'_gapc.cc '+program+'.gap'+' 2>&1', shell=True)
            #if pro1.returncode != 0:
            	#print(pro1.stderr)
        os.chdir("./"+dirstr)
        print(os. getcwd())
        
        pro2 = subprocess.run("make -f "+alg1+"_gapc.mf"+" 2>&1", shell=True)
        
        pro3 = subprocess.run("./"+alg1+"_gapc "+ex+" 2>&1", shell=True, text=True, stdout=subprocess.PIPE)
        res = pro3.stdout.splitlines()
        os.chdir("..")
        
        return render_template("bellman.html", result=res, program=program, gra=gra, gapfiles=json.dumps(gapfiles), gramdict=json.dumps(gramdict), algdict=json.dumps(algdict), infotextsdict=json.dumps(infotextsdict))
        
        #Algebraprodukt
    elif ex != "" and program != "" and gra != "" and alg1 != "" and operator != "" and alg2 != "":
        
        dirstr="computed_"+program
        if not os.path.exists (dirstr+"/"+alg1+"_"+alg2+"_gapc.cc"):
            if not os.path.exists(dirstr):
                os.makedirs(dirstr)
            pro1 = subprocess.run('gapc -p '+alg1+operator+alg2+' -o '+dirstr+'/'+alg1+'_'+alg2+'_gapc.cc '+program+'.gap'+' 2>&1', shell=True)
            #if pro1.returncode != 0:
            	#print(pro1.stderr)
        os.chdir("./"+dirstr)

        pro2 = subprocess.run("make -f "+alg1+"_"+alg2+"_gapc.mf"+" 2>&1", shell=True)
        pro3 = subprocess.run("./"+alg1+"_"+alg2+"_gapc "+ex+" 2>&1", shell=True, text=True, stdout=subprocess.PIPE)
        res = pro3.stdout.splitlines()
        os.chdir("..")
        
        return render_template("bellman.html", result=res, program=program, gra=gra, gapfiles=json.dumps(gapfiles), gramdict=json.dumps(gramdict), algdict=json.dumps(algdict), infotextsdict=json.dumps(infotextsdict))


    return render_template("bellman.html", program=program, gra=gra, gapfiles=json.dumps(gapfiles), gramdict=json.dumps(gramdict), algdict=json.dumps(algdict), infotextsdict=json.dumps(infotextsdict))

@app.route("/result")
def result():
        return render_template('result.html', result=res)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)






