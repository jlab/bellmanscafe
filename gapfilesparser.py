import os
import subprocess

'''
This method parses the gap files and returns
a dictionary containing information about the grammars, algebras, number of
inputs and some info-text (from comments in the gap file).
'''


def parsegapfiles(gapfiles):
    gramdict = {}
    algdict = {}
    infotextsdict = {}
    inputstringsnumberdict = {}
    headersdict = {}
    outputdict = {}
    for grafile in gapfiles:
        gramlist = []
        alglist = []
        commentslist = []
        number_of_inputstrings = 1
        headerslist = []
        with open(grafile) as myfile:
            is_in_comment = False
            current_comment = ""
            # this only works if algebras are
            # separated by new lines in the .gap files
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
                if splitline[0] == "input":
                    if "raw" in myline.casefold():
                        number_of_inputstrings = myline.count("raw")
                    elif "rna" in myline.casefold():
                        number_of_inputstrings = myline.count("rna")
                if splitline[0] == "import":
                    if "," in myline:
                        line = "".join(splitline[1:])
                        for header in line.split(","):
                            if header.startswith('"') and \
                                    header.strip(" \t\r\n").endswith(".hh,"):
                                headerslist.append(header.strip(" '\"\t\r\n"))
                    else:
                        if splitline[1].startswith('"') and \
                                splitline[1].strip(" \t\r\n").endswith('.hh"'):
                            headerslist.append(
                                splitline[1].strip(" '\"\t\r\n"))

        # name of the use selected program is basename of the *.gap source file
        # name minus file ending
        programname = os.path.basename(grafile).split(".")[0]
        gramdict[programname] = gramlist
        algdict[programname] = alglist
        infotextsdict[programname] = commentslist
        inputstringsnumberdict[programname] = number_of_inputstrings
        headersdict[programname] = headerslist
    outputdict["gramdict"] = gramdict
    outputdict["algdict"] = algdict
    outputdict["infotextsdict"] = infotextsdict
    outputdict["inputstringsnumberdict"] = inputstringsnumberdict
    outputdict["headersdict"] = headersdict
    return outputdict


def get_gapc_version(app):
    """Obtain gapc version number via 'gapc --version' system call.

    Parameters
    ----------
    app
        The flask app to enable logging.

    Returns
    -------
    str : the gapc version number
    """
    cmd = 'gapc --version | head -n 1 | cut -d " " -f 3'
    p_version = subprocess.run(cmd, shell=True, text=True,
                               stdout=subprocess.PIPE)
    version = p_version.stdout.strip()
    app.logger.debug('obtain gapc version number via "%s" = %s' % (
        cmd, version))
    return version


def get_adpcollection_commithash(app, fp_repo: str):
    """Obtain current commit hash of the ADP_collection repository.

    Parameters
    ----------
    app
        The flask app to enable logging.

    fp_repo : str
        Filepath to the repository.

    Returns
    -------
    str : the ADP_collection commit hash.
    """
    cmd = 'git show --format="%H" | head -n 1'
    p_version = subprocess.run(cmd, shell=True, text=True,
                               stdout=subprocess.PIPE)
    version = p_version.stdout.strip()
    app.logger.debug('obtain repo commit hash via "%s" = %s' % (
        cmd, version))
    return version
