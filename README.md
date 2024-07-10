# Stefan's Infos
  - when developing, start server via `gunicorn  Bellmansgap:app --error-logfile=- --workers=1` otherwise 8 workers will be started and stderr is redirected into logfile
  - IP of virtual server is 134.176.31.227
ping
Additional Information of the server

# bellmanscafe
Interactive GAPc Website: [bellmanscafe.jlab.bio](http://bellmanscafe.jlab.bio)


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

--------------------------------------------------------------------------------------------------------------------------------------------------------

How to work on the Bellman's Café Website on http://bellmanscafe.jlab.bio/ (with Linux)

I personally work on Linux and would highly recommend you to do the same.
Since I never tried this on Windows, I can't inform you about how to do this on Windows or Mac.

1. Set up the website under your account on the server

The BCF should have provided you with an account on the server.

1.1 Jump to lummerland.
To reach the server you need to ssh to lummerland first.

(Optional):
    To make it easier you can create a file named config in your .ssh directory (if it doesn't already exist).
    Edit the config file and add the lines:

    Host lummerland
        HostName lummerland.computational.bio.uni-giessen.de
        User username
        IdentityFile ~/.ssh/id_rsa_bcf
        ForwardAgent yes
        IdentitiesOnly yes

    It is important that all the lines except the first one are indented.
    Instead of username you should put your own username (For example Daniel Mustermann would put dmustermann as his username).
    Next to IdentityFile you should put the location of your private key.
    And the corresponding public key would also need to be under your account on lummerland already.
    If you don't know what that means or need a refresher, check out (the explanation for linux is on the bottom):
    https://dokuwiki.computational.bio.uni-giessen.de/doku.php?id=system:beginners:remoteaccess

    With the config file set up you can use ssh lummerland to connect to lummerland from your Linux-Terminal.

If you don't want to set up the config file you can also use:
ssh username@lummerland.computational.bio.uni-giessen.de
(If both options don't work, possibly your ssh service isn't working correctly.
sudo service ssh restart and other commands might help.
This website might also be helpful: https://phoenixnap.com/kb/ssh-to-connect-to-remote-server-linux-or-windows)

1.2 Jump to the server
From lummerland you can ssh to the server under the ip-address 134.176.31.227.
If no public key has been deposited on the server yet and you need to access it via your username and password, use:
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no 134.176.31.227
or
ssh username:@134.176.31.227 (with username being your own username on the server (e.g. dmustermann for Daniel Mustermann)
(Don't forget the : in this command!)

1.2.1 Deposit your public key on the server
If this works and you are on the server you can:
Navigate to the ssh directory: cd .ssh
If that directory doesn't exist yet you need to create it: mkdir .ssh
Check if the authorized_keys file already exists: ls -a
Create it, if it doesn't exist yet: touch authorized_keys
Edit the authorized_keys file: nano authorized_keys
In a different terminal copy the content of your public key file from the .ssh directory on lummerland (use SHIFT+CTRL+C to copy from the terminal)
In the original terminal paste the content of your public key to the authorized_keys file (use SHIFT+CTRL+V to paste into the terminal)
Create a new file that is named the same as your public key file on lummerland (e.g. id_rsa_bellman.pub): touch id_rsa_bellman.pub
Edit the newly created file: nano id_rsa_bellman.pub (or vi id_rsa_bellman.pub)
Paste the contents of the public key to the file (use SHIFT+CTRL+V to paste into the terminal)

(Recommended):
If your public key is already deposited on the server,
you can again create (or edit) a config file in ~/.ssh on lummerland, this time adding the following lines:

Host bellmanscafe
    HostName 134.176.31.227
    User username
    IdentityFile ~/.ssh/id_rsa_bellman
    IdentitiesOnly yes

Again take care to indent every line except the first.
Also username should be exchanged with your own username on the server this time (probably again something like dmustermann)
and the IdentityFile should be your private key.

With this you can use ssh bellmanscafe to jump to the server from lummerland.

Now you should be able to access the server without having to type your username or password:
ssh bellmanscafe


Whenever you connect to the server you might need to type bash and press Enter in order to obtain the terminal interface you are familiar with.
(If bash is already activated you would see: username@bellmanscafe:/$, where username is your username on the server.
If bash is not yet activated it just shows: $, then you would need to type bash and press Enter.)

1.3 Download repositories bellmanscafe and ADP_collection

In order to clone bellmanscafe, since it is a private repository, we need to set up ssh authentication to our github account.

1.3.1 Deposit a public key on github account
If you don't own a github account or want to use a new one, check this out: https://github.com/join or https://github.com/signup

Now create a ssh-keypair in your .ssh directory (e.g.: ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa_github_account).
On the github website log into your account and navigate to Settings -> SSH and GPG Keys.
Click on "New ssh key", then enter a title (e.g. Bellman's Server) and paste the content of the public key (ending on .pub)
of your newly created keypair. (You can check the content using cat id_rsa_github_account and copy it by selecting with the mouse
and pressing SHIFT+CTRL+C)
Confirm by clicking Add SSH key.

1.3.2 Clone the bellmanscafe and ADP_collection repositories
Now we have access to our github account from the server.
On the server navigate to your home directory: cd ~ or just cd
Now clone the bellmanscafe repository using:            git clone git@github.com:jlab/bellmanscafe.git
(If that doesn't work, try: git clone https://github.com/jlab/bellmanscafe.git)
And then clone the ADP_collection repository using:     git clone git@github.com:jlab/ADP_collection.git
(If that doesn't work, try: git clone https://github.com/jlab/ADP_collection.git)
Navigate to the bellmanscafe directory: cd bellmanscafe
Make the shell script executable: chmod u+x pull_and_copy_ADP_collection.sh
Execute the shell script to (update and) copy the .gap files from ADP_collection to the bellmanscafe directory: bash pull_and_copy_ADP_collection.sh

1.3.3 Add a cronjob to crontab that automatically executes the shell script once a day (to keep ADP_collection up to date on the server)
Start crontab in the terminal: crontab -e
If you haven't used crontab before on the server it will ask you which editor you want to use,
you can choose the recommended (probably nano) or any other editor that is already  installed on the server.
A file will be opened in the editor. Paste (SHIFT+CTRL+V) the following line to the end of the file:
45 11 * * * /bin/bash /home/username/bellmanscafe/pull_and_copy_ADP_collection.sh

where username is again your username on the server (e.g. dmustermann) and 45 are the minutes and 11 the hour at which
ADP_collection will be automatically updated each day.
If you want ADP_collection to be updated manually you can execute the shell script in bellmanscafe with: bash pull_and_copy_ADP_collection.sh

1.4 Start the website from the directory bellmanscafe
Navigate to bellmanscafe: cd ~/bellmanscafe
Start the website using gunicorn: gunicorn --workers=9 Bellmansgap:app --daemon
Open http://bellmanscafe.jlab.bio/ in a browser to see if the website is up and running.
If it is not use: gunicorn --workers=9 Bellmansgap:app
And check the error messages. Fix the issue and try again.

The --daemon flag is responsible for running the server in the background even after you have closed the terminal.
To kill this background-process use: sudo pkill -f gunicorn
Since this command needs sudo rights, you will need to enter your password.
If you are certain that don't have sudo rights, ask Stefan, Katharina or someone from the BCF to give them to your account on the server.

The website should now be running on http://bellmanscafe.jlab.bio/
Success!

2. Editing and updating the website
In order to work on the website you need to a clone of bellmanscafe on your local machine (e.g. on your laptop).

2.1 Setting up access to github from your local machine
Just like before we need to create a keypair in our .ssh directory: ssh-keygen ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa_github_account
And again we need to copy the content of the new public key to our github account under Settings-> SSH and GPG Keys.
(Alternatively we could copy and paste the content of our github private key on the server
to a new file with the exact same name in the .ssh directory of our local machine (e.g. laptop),
then we wouldn't have to add a new public key to our github account.)

2.2 Cloning bellmanscafe and ADP_collection to local machine
Now we can clone bellmanscafe and ADP_collection to our local machine (e.g. laptop):
In the terminal of your local machine (e.g. laptop),
navigate to the directory you want to clone the repositories to (e.g. our home directory): cd ~
Clone bellmanscafe: git clone git@github.com:jlab/bellmanscafe.git
Then clone ADP_collection: git clone git@github.com:jlab/ADP_collection.git

2.3 Making changes and checking the results
When working on a new version of bellmanscafe it is recommended to create a new branch.
For example if you want to start working on version 2.0:
Navigate to bellmanscafe: cd ~/bellmanscafe
Create (and switch to) a new branch called v2.0: git checkout -b v2.0
Check if it was successful with: git branch
When making changes you can check which files you have changed in the bellmanscafe directory by using: git status
To view the results of your changes you can:
Navigate to bellmanscafe: cd ~/bellmanscafe
Run the python script: python3 Bellmansgap.py
Shift+Click on the link http://127.0.0.1:5000/ or open http://127.0.0.1:5000/ in the browser.
This is a local offline version of the website. To stop it you can use CTRL+C in the terminal.
Be sure to write a short notion about this version into the CHANGELOG file and also change the version in bellman.html.

2.4 Uploading changes
When you are content with your changes you can:
Check which files you have changed: git status
Add the changed files you want to commit: git add Bellmansgap.py templates/bellman.html
Commit all added files with a commit message: git commit -m "This is a commit messages added with the -m flag."
push the commit to the git repository using: git push origin v2.0
On the github website in the jlab/bellmanscafe repository a pop-up will ask you if you want to create a pull request,
click the pop-up to create the pull request and add a title to it.
The codestyle checker for python will automatically start analyzing the style of your python code and show you an error message if
your code isn't matching the codestyle guidelines.
Whenever you push commits to an existing pull request they will appear one after another in the pull request.
For example if you now edit your python code to match the codestyle guidelines and add, commit and push it again with the commit message
"Fixed codestyle issues.", that commit will appear at the bottom of your pull request on the jlab/bellmanscafe github website.
Stefan, Katharina and other members of the AG can review your code and add comments to it.
You can continue to add, committing and pushing changes that are relevant to the current version of bellmanscafe (don't forget to
update the CHANGELOG file).
If you are sure that you don't want to add anything further to this version of bellmanscafe and want to create a new verison,
you should click on merge pull request on the github website of jlab/bellmanscafe.
Most of the time the merge will go without issues.
If there are merge conflicts edit the files and add, commit and push them again to resolve the conflicts.
Then create a new branch like described in 2.3.

2.5 Updating the website
After having merged the pull request successfully, the main branch should now include the changes you have made on your branch.
Navigate to the server again (using ssh lummerland and then ssh bellmanscafe, and possibly typing bash and pressing Enter).
Now navigate to the bellmanscafe directory (cd bellmanscafe).
Download the changes you have merged: git pull
In order for these changes to take effect on the server you need to kill the gunicorn process in the background and restart it afterwards.
Kill background gunicorn process: sudo pkill -f gunicorn
Start process in the background: gunicorn --workers=9 Bellmansgap:app --daemon
Check if the website works in the browser: http://bellmanscafe.jlab.bio/
If it doesn't, try starting the process on the terminal instead (obmitting the --daemon flag): gunicorn --workers=9 Bellmansgap:app

If you want to check if your changes work on the live website even before you have merged the version to the main branch, you can:
Create a new branch on the server with the name of the version: git checkout -b v2.0
Check if you have successfully switched to that branch: git branch
Pull that branch from the github repository: git pull origin v2.0
Kill background gunicorn process: sudo pkill -f gunicorn
Start process in the background: gunicorn --workers=9 Bellmansgap:app --daemon
