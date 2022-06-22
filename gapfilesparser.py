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

        gramdict[grafile.split(".")[0]] = gramlist
        algdict[grafile.split(".")[0]] = alglist
        infotextsdict[grafile.split(".")[0]] = commentslist
        inputstringsnumberdict[grafile.split(".")[0]] = number_of_inputstrings
        headersdict[grafile.split(".")[0]] = headerslist
    outputdict["gramdict"] = gramdict
    outputdict["algdict"] = algdict
    outputdict["infotextsdict"] = infotextsdict
    outputdict["inputstringsnumberdict"] = inputstringsnumberdict
    outputdict["headersdict"] = headersdict
    return outputdict
