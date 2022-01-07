# bellmanscafe
Interactive GAPc Website


$ pip install Flask

In einen Ordner das Python Skript einfügen und einen weiteren Ordner "templates" anlegen. In den Ordner "templates" die HTML Skripte einfügen. Das Python Skript ausführen, Website über Lokal Host starten.

All html files are now stored in the templates folder, html files in the base folder are no longer used (we could delete them?).
To run the website on your local machine clone the git (alternatively download Bellmansgap.py and the "templates" folder in the same location). 

Prerequisites:
You will need python3 and Flask in order for this to work. 

In Ubuntu 20.04 you can install them using the following commands: 

sudo apt-get update 

sudo apt-get install python3.8 python3-pip 

sudo pip install Flask 

In your Linux terminal navigate to the folder that Bellmansgap.py and the templates folder have been downloaded to and run Bellmansgap.py by typing: 

python3 Bellmansgap.py

In the terminal hold CTRL and click on "http://127.0.0.1:5000/", the website should open as a new tab in your browser (we tested this on Google Chrome).

You can now use the website as you wish.
