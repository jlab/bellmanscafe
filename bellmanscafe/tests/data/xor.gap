signature sig_dfn(alphabet, answer) {
  answer lI(int);
  answer lH1(alphabet, answer, alphabet, answer);
  answer lO(answer);
  choice [answer] h([answer]);
}

algebra alg_enum auto enum;
algebra alg_count auto count;
algebra alg_tikz auto tikz;

grammar gra_dfn uses sig_dfn(axiom=y) {
  y = lO(h1) | lO(h2) # h;
  h1 = lH1(CONST_CHAR('1'), x1, CHAR(','), x2) # h;
  h2 = lH1(CONST_CHAR('2'), x1, CHAR(','), x2) # h;
  x1 = lI(INT);
  x2 = lI(INT);
}

instance test = gra_dfn(alg_enum);
