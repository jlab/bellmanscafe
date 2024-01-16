import "ext_alignment.hh"

/* cmt: header */
input <raw, raw>
type Rope = extern
type typ_ali = (Rope first, Rope second)
/* cmt: signature */
signature sig_alignments(alphabet, answer) {
  answer Ins(<alphabet, void>, answer);
  answer Del(<void, alphabet>, answer);
  answer Ers(<alphabet, alphabet>, answer);
  answer Sto(<void, void>);
	
  answer Region(<Rope, void>, answer, <Rope, void>);
  answer Region_Pr(<Rope, void>, answer, <void, Rope>);
  answer Region_Pr_Pr(<void, Rope>, answer, <void, Rope>);
	
  answer Insx(<alphabet, void>, answer);
  answer Delx(<void, alphabet>, answer);

  choice [answer] h([answer]);
}

/* cmt: alg enum */
algebra alg_enum auto enum;
/* cmt: alg count */
algebra alg_count auto count;
/* cmt: alg tikz */
algebra alg_tikz auto tikz;

/* cmt: alg similarty */
algebra alg_similarity implements sig_alignments(alphabet=char, answer=int) {
  int Ins(<alphabet a, void>, int x) {
    return x -2;
  }
  int Del(<void, alphabet b>, int x) {
    return x -2;
  }
  int Ers(<alphabet a, alphabet b>, int x) {
    if (a == b) {
      return x +1;
    } else {
      return x -1;
    }
  }
  int Sto(<void, void>) {
    return 0;
  }
	
  int Region(<Rope aleft, void>, int x, <Rope aright, void>) {
    return x;
  }
  int Region_Pr(<Rope aleft, void>, int x, <void, Rope bright>) {
    return x;
  }
  int Region_Pr_Pr(<void, Rope bleft>, int x, <void, Rope bright>) {
    return x;
  }
	
  // this is slightly different form http://rna.informatik.uni-freiburg.de/Teaching/index.jsp?toolName=Gotoh#
  // as there Ins + Insx is computed for first blank, we here score Ins for first blank and Insx for all following ones
  int Insx(<alphabet a, void>, int x) {
    return x -1;
  }
  int Delx(<void, alphabet b>, int x) {
    return x -1;
  }

  choice [int] h([int] candidates) {
    return list(maximum(candidates));
  }
}


/* cmt: alg countmanual */
algebra alg_countmanual implements sig_alignments(alphabet=char, answer=int) {
  int Ins(<alphabet a, void>, int x) {
    return x;
  }
  int Del(<void, alphabet b>, int x) {
    return x;
  }
  int Ers(<alphabet a, alphabet b>, int x) {
    return x;
  }
  int Sto(<void, void>) {
    return 1;
  }
	
  int Region(<Rope aleft, void>, int x, <Rope aright, void>) {
    return x;
  }
  int Region_Pr(<Rope aleft, void>, int x, <void, Rope bright>) {
    return x;
  }
  int Region_Pr_Pr(<void, Rope bleft>, int x, <void, Rope bright>) {
    return x;
  }
	
  int Insx(<alphabet a, void>, int x) {
    return x;
  }
  int Delx(<void, alphabet b>, int x) {
    return x;
  }

  choice [int] h([int] candidates) {
    return list(sum(candidates));
  }
}

/* cmt: alg pretty */
algebra alg_pretty implements sig_alignments(alphabet=char, answer=typ_ali) {
  typ_ali Ins(<alphabet a, void>, typ_ali x) {
    typ_ali res;
    append(res.first, a);
    append(res.first, x.first);
    append(res.second, '-');
    append(res.second, x.second);
    return res;
  }
  typ_ali Del(<void, alphabet b>, typ_ali x) {
    typ_ali res;
    append(res.first, '-');
    append(res.first, x.first);
    append(res.second, b);
    append(res.second, x.second);
    return res;
  }
  typ_ali Ers(<alphabet a, alphabet b>, typ_ali x) {
    typ_ali res;
    append(res.first, a);
    append(res.first, x.first);
    append(res.second, b);
    append(res.second, x.second);
    return res;
  }
  typ_ali Sto(<void, void>) {
    typ_ali res;
    return res;
  }
	
  typ_ali Region(<Rope afirst, void>, typ_ali x, <Rope asecond, void>) {
    typ_ali res;
    append(res.first, afirst);
    append(res.first, x.first);
    append(res.first, asecond);
	  
    append(res.second, '_', size(afirst));
    append(res.second, x.second);
    append(res.second, '_', size(asecond));
    return res;
  }
  typ_ali Region_Pr(<Rope afirst, void>, typ_ali x, <void, Rope bsecond>) {
    typ_ali res;
    append(res.first, afirst);
    append(res.first, x.first);
    append(res.first, '_', size(bsecond));
	  
    append(res.second, '_', size(afirst));
    append(res.second, x.second);
    append(res.second, bsecond);
    return res;
  }
  typ_ali Region_Pr_Pr(<void, Rope bfirst>, typ_ali x, <void, Rope bsecond>) {
    typ_ali res;
    append(res.first, '_', size(bfirst));
    append(res.first, x.first);
    append(res.first, '_', size(bsecond));
	  
    append(res.second, bfirst);
    append(res.second, x.second);
    append(res.second, bsecond);
    return res;
  }
	
  // this is slightly different form http://rna.informatik.uni-freiburg.de/Teaching/index.jsp?toolName=Gotoh#
  // as there Ins + Insx is computed for first blank, we here score Ins for first blank and Insx for all following ones
  typ_ali Insx(<alphabet a, void>, typ_ali x) {
    typ_ali res;
    append(res.first, a);
    append(res.first, x.first);
    append(res.second, '=');
    append(res.second, x.second);
    return res;
  }
  typ_ali Delx(<void, alphabet b>, typ_ali x) {
    typ_ali res;
    append(res.first, '=');
    append(res.first, x.first);
    append(res.second, b);
    append(res.second, x.second);
    return res;
  }

  choice [typ_ali] h([typ_ali] candidates) {
    return candidates;
  }
}

/* a special pretty print algebra that uses the same symbol '-' for all types of gapc
 * this illustrates semantic ambiguity and is e.g. used as the introductory example
 * in the lecture slides.
 * cmt: alg pretty onegap */
algebra alg_pretty_onegap extends alg_pretty {
  typ_ali Region(<Rope afirst, void>, typ_ali x, <Rope asecond, void>) {
    typ_ali res;
    append(res.first, afirst);
    append(res.first, x.first);
    append(res.first, asecond);
	  
    append(res.second, '-', size(afirst));
    append(res.second, x.second);
    append(res.second, '-', size(asecond));
    return res;
  }
  typ_ali Region_Pr(<Rope afirst, void>, typ_ali x, <void, Rope bsecond>) {
    typ_ali res;
    append(res.first, afirst);
    append(res.first, x.first);
    append(res.first, '-', size(bsecond));
	  
    append(res.second, '-', size(afirst));
    append(res.second, x.second);
    append(res.second, bsecond);
    return res;
  }
  typ_ali Region_Pr_Pr(<void, Rope bfirst>, typ_ali x, <void, Rope bsecond>) {
    typ_ali res;
    append(res.first, '-', size(bfirst));
    append(res.first, x.first);
    append(res.first, '-', size(bsecond));
	  
    append(res.second, bfirst);
    append(res.second, x.second);
    append(res.second, bsecond);
    return res;
  }
  typ_ali Insx(<alphabet a, void>, typ_ali x) {
    typ_ali res;
    append(res.first, a);
    append(res.first, x.first);
    append(res.second, '-');
    append(res.second, x.second);
    return res;
  }
  typ_ali Delx(<void, alphabet b>, typ_ali x) {
    typ_ali res;
    append(res.first, '-');
    append(res.first, x.first);
    append(res.second, b);
    append(res.second, x.second);
    return res;
  }
}

/* an algebra that computes a Trace representation of an Alignment,
 * i.e. we arbitraily say that Insertions cannot preceed Deletions (could be vice versa)
 * cmt: alg editops */
algebra alg_editops implements sig_alignments(alphabet=char, answer=Rope) {
  Rope Ins(<alphabet a, void>, Rope x) {
    Rope res;
    res = trace_pushback('I', x);
    return res;
  }
  Rope Del(<void, alphabet b>, Rope x) {
    Rope res;
    append(res, 'D');
    append(res, x);
    return res;
  }
  Rope Ers(<alphabet a, alphabet b>, Rope x) {
    Rope res;
    append(res, 'E');
    append(res, x);
    return res;
  }
  Rope Sto(<void, void>) {
    Rope res;
    append(res, '.');
    return res;
  }
	
  Rope Region(<Rope aleft, void>, Rope x, <Rope aright, void>) {
    Rope res;
    append(res, '1');
    append(res, x);
    return res;
  }
  Rope Region_Pr(<Rope aleft, void>, Rope x, <void, Rope bright>) {
    Rope res;
    append(res, '2');
    append(res, x);
    return res;
  }
  Rope Region_Pr_Pr(<void, Rope bleft>, Rope x, <void, Rope bright>) {
    Rope res;
    append(res, '3');
    append(res, x);
    return res;
  }
	
  // this is slightly different form http://rna.informatik.uni-freiburg.de/Teaching/index.jsp?toolName=Gotoh#
  // as there Ins + Insx is computed for first blank, we here score Ins for first blank and Insx for all following ones
  Rope Insx(<alphabet a, void>, Rope x) {
    Rope res;
    append(res, 'i');
    append(res, x);
    return res;
  }
  Rope Delx(<void, alphabet b>, Rope x) {
    Rope res;
    append(res, 'd');
    append(res, x);
    return res;
  }

  choice [Rope] h([Rope] candidates) {
    return unique(candidates);
  }
}



/* pair-wise global alignment
 * cmt: gra needlemanwunsch */
grammar gra_needlemanwunsch uses sig_alignments(axiom=A) {
  A = Ins(<CHAR, EMPTY>, A)
    | Del(<EMPTY, CHAR>, A)
    | Ers(<CHAR, CHAR>, A)
    | Sto(<EMPTY, EMPTY>)
    # h;
}

/* a grammar that enumerates all traces but not all alignments
   difference:  X-   and  -X   are two different alignments, but the same trace
                -Y        Y-
   this is because there is no evidence that could tell us if deletion came before insertion
   or vice versa.
*/
/* cmt: gra_traces */
grammar gra_traces uses sig_alignments(axiom=A) {
  A = Ins(<CHAR, EMPTY>, I)
    | Del(<EMPTY, CHAR>, D)
    | R
    # h;

  D = Ins(<CHAR, EMPTY>, I)
    | Del(<EMPTY, CHAR>, D)
    | R
    # h;
    
  I = Ins(<CHAR, EMPTY>, I)
    | R
    # h;

  R = Ers(<CHAR, CHAR>, A)
    | Sto(<EMPTY, EMPTY>)
    # h;
}

/* pair-wise semiglobal alignment, i.e. long in short */
/* cmt: gra_semiglobal */
grammar gra_semiglobal uses sig_alignments(axiom=S) {
  S = Region(<ROPE0, EMPTY>, A, <ROPE0, EMPTY>)
    # h;
	
  A = Ins(<CHAR, EMPTY>, A)
    | Del(<EMPTY, CHAR>, A)
    | Ers(<CHAR, CHAR>, A)
    | Sto(<EMPTY, EMPTY>)
    # h;
}

/* pair-wise end-gap-free alignment, e.g. for assembly */
/* cmt: gra endgapfree */
grammar gra_endgapfree uses sig_alignments(axiom=S) {
  S = Region_Pr(<ROPE0, EMPTY>, A, <EMPTY, ROPE0>)
    # h;
	
  A = Ins(<CHAR, EMPTY>, A)
    | Del(<EMPTY, CHAR>, A)
    | Ers(<CHAR, CHAR>, A)
    | Sto(<EMPTY, EMPTY>)
    # h;
}

/* pair-wise local alignment, e.g. BLAST */
/* cmt: gra smitwaterman */
grammar gra_smithwaterman uses sig_alignments(axiom=S) {
  S = Region(<ROPE0, EMPTY>, T, <ROPE0, EMPTY>)
    # h;
	
  T = Region_Pr_Pr(<EMPTY, ROPE0>, A, <EMPTY, ROPE0>)
    # h;
	
  A = Ins(<CHAR, EMPTY>, A)
    | Del(<EMPTY, CHAR>, A)
    | Ers(<CHAR, CHAR>, A)
    | Sto(<EMPTY, EMPTY>)
    # h;
}

/* pair-wise global alignment with affine gap costs */
/* cmt: gra gotoh */
grammar gra_gotoh uses sig_alignments(axiom=A) {
  A = Ins(<CHAR, EMPTY>, xIns)
    | Del(<EMPTY, CHAR>, xDel)
    | Ers(<CHAR, CHAR>, A)
    | Sto(<EMPTY, EMPTY>)
    # h;

  xIns = Insx(<CHAR, EMPTY>, xIns)
       | A
       # h;

  xDel = Delx(<EMPTY, CHAR>, xDel)
       | A
       # h;
}

/*
example inputs: ZEITGEIST FREIZEIT
*/

/* cmt: ins needlemanwunsch */
instance ins_needlemanwunsch_count = gra_needlemanwunsch(alg_count);
instance ins_semiglobal_count = gra_semiglobal(alg_count);
instance ins_endgapfree_count = gra_endgapfree(alg_count);
instance ins_smithwaterman_count = gra_smithwaterman(alg_count);
instance ins_gotoh_count = gra_gotoh(alg_count);
instance ins_traces_count = gra_traces(alg_count);

instance ins_needlemanwunsch_similaritycount = gra_needlemanwunsch(alg_similarity * alg_count);
instance ins_semiglobal_similaritycount = gra_semiglobal(alg_similarity * alg_count);
instance ins_endgapfree_similaritycount = gra_endgapfree(alg_similarity * alg_count);
instance ins_smithwaterman_similaritycount = gra_smithwaterman(alg_similarity * alg_count);
instance ins_gotoh_similaritycount = gra_gotoh(alg_similarity * alg_count);

instance ins_needlemanwunsch_similaritypp = gra_needlemanwunsch(alg_similarity * alg_pretty);
instance ins_semiglobal_similaritypp = gra_semiglobal(alg_similarity * alg_pretty);
instance ins_endgapfree_similaritypp = gra_endgapfree(alg_similarity * alg_pretty);
instance ins_smithwaterman_similaritypp = gra_smithwaterman(alg_similarity * alg_pretty);
instance ins_gotoh_similaritypp = gra_gotoh(alg_similarity * alg_pretty);

instance test = gra_smithwaterman(alg_pretty * alg_enum);
instance ins_traces_ppcount = gra_traces(alg_pretty * alg_count);

// used in lecture as example of how to compile:
instance ins_gotoh_pp = gra_gotoh(alg_pretty_onegap);
instance ins_gotoh_ppenum = gra_gotoh(alg_pretty_onegap * alg_enum);
instance ins_gotoh_countmanual = gra_gotoh(alg_countmanual);

instance ins_trace_similarity = gra_traces(alg_similarity);
instance ins_needlemanwunsch_similarity = gra_needlemanwunsch(alg_similarity);

/* cmt: ins nweditopscount */
instance ins_nweditopscount = gra_needlemanwunsch(alg_editops * alg_count);

/* cmt: footer */
