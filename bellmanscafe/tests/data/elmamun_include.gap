import "ext_1.hh"
type Rope = extern

signature sig_elmamun(alphabet, answer) {
  answer number(int);
  answer add(answer, alphabet, answer);
  answer mult(answer, alphabet, answer);
  answer minus(answer, alphabet, answer);
  choice [answer] h([answer]);
}

include "sub_algebra.subgap"

grammar gra_elmamun uses sig_elmamun(axiom = formula) {
  formula = number(INT)
	  | add(formula, CHAR('+'), formula)
	  | mult(formula, CHAR('*'), formula)
	  | minus(formula, CHAR('-'), formula)
	  # h;
}

/*
example inputs: 1+2*3*4+5
*/

instance pp = gra_elmamun(alg_pretty);
