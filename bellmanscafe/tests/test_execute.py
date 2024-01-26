import sys
sys.path.append('../')

from io import StringIO  # noqa: E402
import os  # noqa: E402
from unittest import TestCase, main  # noqa: E402
from bellmanscafe.execute import compile_and_run_gapc  # noqa: E402


class ParseGAPLTests(TestCase):
    def setUp(self):
        self.gapl_programs = {'alignments': {'imports': ["ext_alignment.hh"]}}

        self.user_input = {'select_program': 'alignments',
                           'select_grammar': 'gra_needlemanwunsch',
                           'plot_grammar': '1',
                           'algebra_1': 'alg_similarity',
                           'product_1': '*',
                           'algebra_2': 'alg_count',
                           'userinput_1': 'FREIZEIT',
                           'userinput_2': 'ZEITGEIST'}

        self.settings = {'paths': {'gapc_programs': 'bellmanscafe/tests/data/',
                                   'prefix_cache': './cache_dir/'},
                         'versions': {'gapc': 'kalle',
                                      'ADP_collection': 'heinz'},
                         'max_algebras': 5,
                         'max_output_lines': 5000,
                         'max_cpu_time': 100}

    def test_compile_and_run_gapc(self):
        obs = compile_and_run_gapc(
            self.gapl_programs, self.user_input, self.settings)
        self.assertEqual('( -3 , 4 )', obs['run']['stdout'][-1].strip())

    def test_concurrency(self):
        ERRMSG = ('looks like another process is trying to build '
                  'the same instan')
        # first execution
        log = StringIO("")
        obs = compile_and_run_gapc(
            self.gapl_programs, self.user_input, self.settings, verbose=log)
        self.assertEqual('( -3 , 4 )', obs['run']['stdout'][-1].strip())
        self.assertTrue(ERRMSG not in log.getvalue())

        # remove indicator file of first execution
        os.remove(os.path.join(self.settings['paths']['prefix_cache'],
                               obs['gapc']['cache'],
                               'binary.ready'))

        # second execution
        log = StringIO("")
        obs = compile_and_run_gapc(
            self.gapl_programs, self.user_input, self.settings,
            retry=1, waitfor=1, verbose=log)
        self.assertTrue(ERRMSG in log.getvalue())


if __name__ == '__main__':
    main()
