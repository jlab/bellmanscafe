import os, subprocess, glob, json
from flask import Flask, redirect, url_for, render_template, request, session

app = Flask(__name__)
app.secret_key = "xasdqfghuioiuwqenjdcbjhawbuomcujeq1217846421kopNSJJGWmc8u29"

#Variablen
ex=""
grafiles=""
gra=""
alg1=""
operator=""
alg2=""
res=""
grafiles= sorted(glob.glob('*.gap'))
gra= grafiles[0].split(".")[0]
print(grafiles)
print(gra+"!")
algebras=[]
for grafile in grafiles:
	#newlist = []
	with open(grafile) as myfile:
	    for myline in myfile:
	    	splitline = myline.split(" ")
	    	if splitline[0] == "algebra":
	    		algebras.append(splitline[1])
	    		#newlist.append(splitline[1])
	#algebras.append(newlist)
algebras = sorted(algebras)
print(algebras)

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
        global gra
        global alg1
        global operator
        global alg2
        global res
        global grafiles
        global algebras
        
        ex= request.form.get('ex')
        gra= request.form.get('gra')
        alg1= request.form.get('alg1')
        operator= request.form.get('operator')
        alg2= request.form.get('alg2')
    
    #Algebra
    if ex != "" and gra != "" and alg1 != "" and operator == "" and alg2 == "":
        
        dirstr="computed"
        if not os.path.exists (dirstr+"/"+alg1+"_gapc.cc"):
            if not os.path.exists(dirstr):
                os.makedirs(dirstr)
            subprocess.run('gapc -p '+'alg_'+alg1+' -o '+dirstr+'/'+alg1+'_gapc.cc '+gra+'.gap'+' 2>&1', shell=True)
        os.chdir("./computed")
        
        subprocess.run("make -f "+alg1+"_gapc.mf"+" 2>&1", shell=True)
        res = subprocess.run("./"+alg1+"_gapc "+ex+" 2>&1", shell=True, capture_output=True)
        
        return redirect(url_for("result"))
        
        #Algebraprodukt
    elif ex != "" and gra != "" and alg1 != "" and operator != "" and alg2 != "":
        
        
        if not os.path.exists ("computed/"+alg1+"_"+alg2+"_gapc.cc"):
            if not os.path.exists("computed"):
                os.makedirs("computed")
            subprocess.run('gapc -p '+'alg_'+alg1+operator+alg2+' -o '+dirstr+'/'+alg1+'_'+alg2+'_gapc.cc '+gra+'.gap'+' 2>&1', shell=True)
        os.chdir("./computed")

        subprocess.run("make -f "+alg1+"_"+alg2+"_gapc.mf"+" 2>&1", shell=True)
        res = subprocess.run("./"+alg1+"_"+alg2+"_gapc "+ex+" 2>&1", shell=True, capture_output=True)
        
        return redirect(url_for("result"))


    return render_template("bellman.html", gra=gra, grafiles=json.dumps(grafiles), algebras=json.dumps(algebras))

@app.route("/result")
def result():
        return render_template('result.html', result=res)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)






