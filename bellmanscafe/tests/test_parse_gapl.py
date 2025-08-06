import os
import sys
sys.path.append('../')

from unittest import TestCase, main  # noqa: E402
from bellmanscafe.parse_gapl import _extract_comments, _parse_gapl_header, \
    _merge, _parse_gapl_signature, parse_gapl, _include_code, \
    _extract_example_inputs, _header_includes, get_gapc_programs   # noqa: E402


class ParseGAPLTests(TestCase):
    def test_extract_comments(self):
        exp = (['this is codeA',
                'codeB // inline comment1',
                'codeC  more codeD',
                'this is',
                '',
                'a test',
                'codeLeft  codeRight'],
               [' comment2 ',
                ' line one',
                'line two',
                'line three ',
                ' comment in the middle with http://url '])

        obs = _extract_comments([
            "this is codeA",
            "codeB // inline comment1",
            "codeC /* comment2 */ more codeD",
            "this is",
            "/* line one",
            "line two",
            "line three */",
            "a test",
            "codeLeft /* comment in the middle with http://url */ codeRight"])

        self.assertEqual(exp, obs)

        with self.assertRaisesRegex(ValueError, 'Delimiter #FUSE# in block!'):
            obs = _extract_comments(['Hello#FUSE#World'])

    def test_merge(self):
        obs = _merge(dict(),
                     dict())
        self.assertEqual({'comments': dict()}, obs)

        obs = _merge({'algebras': ['alg_mfe']},
                     {'grammars': ['fold']})
        self.assertEqual({'algebras': ['alg_mfe'],
                          'grammars': ['fold'], 'comments': {}}, obs)

        obs = _merge({'algebras': ['alg_mfe'], 'comments': {'a': 'Hallo'}},
                     {'grammars': ['fold']})
        self.assertEqual({'algebras': ['alg_mfe'], 'comments': {'a': 'Hallo'},
                          'grammars': ['fold']}, obs)

        obs = _merge({'algebras': ['alg_mfe'], 'comments': {'a': 'Hallo'}},
                     {'grammars': ['fold'], 'comments': {'b': 'Welt'}})
        self.assertEqual({
            'algebras': ['alg_mfe'],
            'comments': {'a': 'Hallo', 'b': 'Welt'},
            'grammars': ['fold']}, obs)

        with self.assertRaisesRegex(ValueError, 'Conflicting'):
            _merge({'algebras': ['alg_mfe'], 'comments': {'a': 'Hallo'}},
                   {'grammars': ['fold'], 'comments': {'a': 'Welt'}})

        obs = _merge({}, {'imports': [], 'inputs': ['rna'],
                          'comments': {'header': 'kurt'}})
        self.assertEqual({'imports': [], 'inputs': ['rna'],
                          'comments': {'header': 'kurt'}}, obs)

    def test_parse_gapl_header(self):
        obs = _parse_gapl_header(['import rna\n', 'input rna\n', '\n',
                                  'type Rope = extern\n', '\n'])
        # skip rna as this belongs to the rtlib
        self.assertEqual([], obs['imports'])
        self.assertEqual(['rna'], obs['inputs'])

        obs = _parse_gapl_header([
            'import "ext_alignment.hh"\n', '\n',
            'input <raw, raw>\n', 'type Rope = extern\n',
            'type typ_ali = (Rope first, Rope second)\n', '\n'])
        self.assertEqual(['ext_alignment.hh'], obs['imports'])
        self.assertEqual(['raw,', 'raw'], obs['inputs'])

        obs = _parse_gapl_header([
            '/*\n', "# Calif El Mamun's Caravan\n",
            ('<img src="http://www.tabsir.net/images/'
             'Kadhimiya.gif" style="di...'),
            '...ity over `+`.\n', '\n', '*/\n', '\n',
            'type Rope = extern\n', '\n'])
        self.assertEqual(['raw'], obs['inputs'])
        self.assertEqual(5, len(obs['header']['comments']))

        obs = _parse_gapl_header(['import "1.hh" //"2.hh"\n'])
        self.assertEqual(obs['imports'], ['1.hh'])

        obs = _parse_gapl_header(['import "1.hh" "2.hh"\n'])
        self.assertEqual(obs['imports'], ['1.hh'])

    def test_parse_gapl_signature(self):
        obs = _parse_gapl_signature([
            'signature sig_rna(alphabet, answer) {\n',
            '  answer nil(void);\n',
            '  answer unpaired(Subsequence, answer);\n',
            '  answer split(answer, answer);\n',
            '  answer pair(Subsequence, answer, Subsequence);\n',
            '  choice [answer] h([answer]);\n', '}\n', '\n'])
        self.assertEqual(['sig_rna'], list(obs['signatures'].keys()))

    def test_parse_gapl(self):
        obs = parse_gapl('bellmanscafe/tests/data/alignments.gap')
        self.assertEqual([
            'algebras',
            'codelines',
            'example_inputs',
            'footer',
            'grammars',
            'header',
            'imports',
            'include_files',
            'inputs',
            'instances',
            'signatures'], sorted(obs.keys()))

        self.assertEqual([
            'alg_count',
            'alg_countmanual',
            'alg_editops',
            'alg_enum',
            'alg_pretty',
            'alg_pretty_onegap',
            'alg_similarity',
            'alg_tikz'], sorted(obs['algebras'].keys()))
        self.assertEqual(0, obs['algebras']['alg_enum']['position'])
        self.assertTrue(
            'cmt: alg enum' in obs['algebras']['alg_enum']['comments'][0])
        self.assertEqual(7, obs['algebras']['alg_editops']['position'])
        self.assertTrue('cmt: alg editops' in obs[
            'algebras']['alg_editops']['comments'][-1])

        self.assertEqual([
            'gra_endgapfree',
            'gra_gotoh',
            'gra_needlemanwunsch',
            'gra_semiglobal',
            'gra_smithwaterman',
            'gra_traces'], sorted(obs['grammars'].keys()))
        self.assertEqual(0, obs['grammars']['gra_needlemanwunsch']['position'])
        self.assertTrue('cmt: gra needlemanwunsch' in obs[
            'grammars']['gra_needlemanwunsch']['comments'][-1])
        self.assertEqual(5, obs['grammars']['gra_gotoh']['position'])
        self.assertTrue(
            'cmt: gra gotoh' in obs['grammars']['gra_gotoh']['comments'][-1])

        self.assertEqual(['ext_alignment.hh'], obs['imports'])

        self.assertEqual(['raw,', 'raw'], obs['inputs'])

        self.assertEqual(24, len(obs['instances']))
        self.assertEqual(True, all(
            ['example_inputs' not in x
             for x in obs['instances'][
                'ins_needlemanwunsch_count']['comments']]))

        self.assertEqual(17, len(obs['signatures']['sig_alignments']['code']))

        self.assertEqual(['ZEITGEIST', 'FREIZEIT'], obs['example_inputs'])

    def test__include_code(self):
        fp_root = 'bellmanscafe/tests/data/elmamun_include.gap'
        with open(fp_root, "r") as f:
            obs = _include_code(f.readlines(), fp_root)
        exp_files = [os.path.join(os.path.dirname(fp_root), x)
                     for x in ['sub_algebra.subgap', 'sub_sub_choice.subgap']]
        self.assertEqual(obs[1], exp_files)

        self.assertTrue('instance pp = gra_elmamun(alg_pretty);\n' in obs[0])
        self.assertTrue(('algebra alg_pretty implements sig_elmamun('
                         'alphabet=char, answer=Rope) {\n') in obs[0])
        self.assertTrue('  choice [Rope] h([Rope] candidates) {\n' in obs[0])

    def test__extract_example_inputs(self):
        obs = _extract_example_inputs({'example_inputs': ['foo']})
        self.assertEqual(obs, ['foo'])

        gapl = {'instances': {'foo': {'comments': [
            'example inputs: 1+2*3*4+5']}}}
        self.assertEqual(_extract_example_inputs(gapl), ['1+2*3*4+5'])

    def test__header_includes(self):
        fp_root = 'bellmanscafe/tests/data/elmamun_include.gap'
        gapl = parse_gapl(fp_root)
        self.assertEqual(gapl['imports'], ['ext_1.hh', 'ext_sub_1.hh'])

        obs = _header_includes('bellmanscafe/tests/data/', ['ext_1.hh'])
        self.assertEqual(obs, ['ext_1.hh', 'ext_sub_1.hh'])

    def test_get_gapc_programs(self):
        self.assertEqual(
            len(get_gapc_programs('bellmanscafe/tests/data/', verbose=None)),
            5)


if __name__ == '__main__':
    main()
