import sys
sys.path.append('../')

from unittest import TestCase, main  # noqa: E402
from bellmanscafe.execute import compile_and_run_gapc   # noqa: E402


class ParseGAPLTests(TestCase):
    def test_compile_and_run_gapc(self):
        gapl_programs = {'alignments': {'imports': ["ext_alignment.hh"]}}

        user_input = {'select_program': 'alignments',
                      'select_grammar': 'gra_needlemanwunsch',
                      'plot_grammar': '1',
                      'algebra_1': 'alg_similarity',
                      'product_1': '*',
                      'algebra_2': 'alg_count',
                      'userinput_1': 'FREIZEIT',
                      'userinput_2': 'ZEITGEIST'}

        settings = {'paths': {'gapc_programs': 'bellmanscafe/tests/data/',
                              'prefix_cache': './cache_dir/'},
                    'versions': {'gapc': 'kalle',
                                 'ADP_collection': 'heinz'},
                    'max_algebras': 5,
                    'max_output_lines': 5000,
                    'max_cpu_time': 100}

        obs = compile_and_run_gapc(gapl_programs, user_input, settings)
        print(obs)
        self.assertEqual('( -3 , 4 )', obs['run']['stdout'][-1].strip())


if __name__ == '__main__':
    main()
