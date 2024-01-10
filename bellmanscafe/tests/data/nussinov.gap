import rna
input rna

type Rope = extern

signature sig_rna(alphabet, answer) {
  answer nil(void);
  answer unpaired(Subsequence, answer);
  answer split(answer, answer);
  answer pair(Subsequence, answer, Subsequence);
  choice [answer] h([answer]);
}

algebra alg_enum auto enum;
algebra alg_count auto count;
algebra alg_tikz auto tikz;

algebra alg_bpmax implements sig_rna(alphabet=char, answer=int) {
  int nil(void) {
    return 0;
  }
  int unpaired(Subsequence b, int x) {
    return x;
  }
  int split(int x, int y) {
    return x+y;
  }
  int pair(Subsequence lb, int x, Subsequence rb) {
    return x+1;
  }
  choice [int] h([int] candidates) {
    return list(maximum(candidates));
  }
}

algebra alg_dotBracket implements sig_rna(alphabet=char, answer=Rope) {
  Rope nil(void) {
    Rope r;
    return r;
  }
  Rope unpaired(Subsequence b, Rope x) {
    return '.' + x;
  }
  Rope split(Rope x, Rope y) {
    return x + y;
  }
  Rope pair(Subsequence lb, Rope x, Subsequence rb) {
    return '(' + x + ')';
  }
  choice [Rope] h([Rope] candidates) {
    return candidates;
  }
}


grammar gra_nussinov uses sig_rna(axiom=MMS) {
  MMS = nil(EMPTY)
      | unpaired(BASE, MMS)
      | split(pair(BASE, MMS, BASE) with basepairing, MMS)
      # h;
}

instance count = gra_nussinov(alg_count);
