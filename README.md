# bellmanscafe
Interactive GAPc Website: [bellmanscafe.jlab.bio](bellmanscafe.jlab.bio)


$ pip install Flask

In einen Ordner das Python Skript einfügen und einen weiteren Ordner "templates" anlegen. In den Ordner "templates" die HTML Skripte einfügen. Das Python Skript ausführen, Website über Lokal Host starten.

All html files are now stored in the templates folder, html files in the base folder are no longer used.
To run the website on your local machine clone the git (alternatively download Bellmansgap.py and the "templates" folder in the same location). 

Prerequisites:
You will need python3 and Flask in order for this to work. 

In Ubuntu 20.04 you can install them using the following commands: 

sudo apt-get update <br> sudo apt-get install python3.8 python3-pip <br> sudo pip install Flask 

In your Linux terminal navigate to the folder that Bellmansgap.py and the templates folder have been downloaded to and run Bellmansgap.py by typing: 

python3 Bellmansgap.py

In the terminal hold CTRL and click on "http://127.0.0.1:5000/", the website should open as a new tab in your browser (we tested this on Google Chrome).

You can now use the website as you wish.

Packages on the Ubuntu 20.04.3 server (Feb 17 2022), installed via apt/apt-get (except flask, which was install via pip3):

git 2.25.1

python3 3.8.10

pip 20.0.2 (Python 3.8)

flask 2.0.3 (pip3)

nginx 1.18.0

gunicorn 20.0.4
