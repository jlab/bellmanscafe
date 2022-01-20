
def parsegapfiles(gapfiles):
  tag = "[*]"
  closingtag = "[\*]"
  regex = "[b]*[\b]"
  gramdict={}
  algdict={}
  infotextsdict={}
  outputdict = {}
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
  outputdict["gramdict"] = gramdict
  outputdict["algdict"] = algdict
  outputdict["infotextsdict"] = infotextsdict
  return outputdict
