import sys
import glob
import os
import markdown
import re
from bellmanscafe.cafe import log


def _extract_comments(block: [str]) -> ([str], [str]):
    """Takes a list of code lines and splits them into two new list. The first
       only contains code lines, the second only comment lines.

    Parameters
    ----------
    block : [str]
        List of program lines

    Returns
    -------
    ([str], [str]) : two lists of lines, first containing only code, second
    only comments

    Raises
    ------
    ValueError if lines of block contains the artifical delimiter #FUSE#.
    """
    DELIM = '#FUSE#'

    if any(map(lambda x: DELIM in x, block)):
        raise ValueError('Delimiter %s in block!' % DELIM)

    fused = DELIM.join(block)

    code, comment = "", ""
    in_comment = False
    i = 0
    while i < len(fused):
        if (in_comment is False) and (fused[i:i+2] == '/*'):
            in_comment = True
            i += 2
        elif (in_comment is True) and (fused[i:i+2] == '*/'):
            comment += DELIM
            i += 2
            in_comment = False
            continue
        # keep // comments as part of code to use them as annotations of code,
        # instead of /* */ comments which shall be describe the block as a
        # whole
        # elif (in_comment == False) and (fused[i:i+2] == '//'):
        #     cmt = fused[i+2:].split(DELIM)[0]
        #     comment += cmt + DELIM
        #     i += len(cmt) + 2
        #     continue

        if in_comment:
            comment += fused[i]
        else:
            code += fused[i]

        i += 1

    cmts = comment.split(DELIM)
    if cmts == [""]:
        cmts = []

    return code.split(DELIM), [c for c in cmts if c != ""]


def _merge(a: dict, b: dict, subdicts: [str] = ['comments']):
    """Merge result dicts of _parse_gapl_XXX functions.

    Parameters
    ----------
    a : dict(str, ?)
        A result dictionary of a _parse_gapl_ function.
    b : dict(str, ?)
        Another result dictionary of a _parse_gapl_ function.
    subdicts: [str]
        List of key names for sub-dicts that shall be merged.

    Returns
    -------
    dict(str, ?)

    Raises
    ------
    ValueError if a and b contain the same key in sub-dicts.
    """
    res = a.copy()
    res.update({k: v for k, v in b.items() if k not in subdicts})

    for sub in subdicts:
        res[sub] = dict()
        if (sub in a.keys()) and (sub in b.keys()):
            # check if subdict keys collide
            coll = set(a[sub].keys()) & set(b[sub].keys())
            if len(coll) > 0:
                raise ValueError("Conflicting '%s' keys: %s!" % (
                    sub, ', '.join(coll)))
        for d in [a, b]:
            if (sub in d.keys()):
                if len(res[sub]) == 0:
                    res[sub] = d[sub]
                else:
                    res[sub].update(d[sub])

    return res


def _parse_gapl_header(block: [str]):
    """Extracts imports, inputs and comments from header part of an GAPl
       program.

    Parameters
    ----------
    block : [str]
        The code lines prior to the signature.

    Returns
    -------
    {'imports': [str],
     'inputs': [str],
     'comments': {'header': [str]}}
    """
    gapl_imports = []
    gapl_inputs = []

    code, comments = _extract_comments(block)

    for i in range(len(code)):
        line = code[i].strip()
        if line.startswith('import '):
            for external in line.split()[1:]:
                if '"' in external:
                    # only add external imports, i.e. those not in the rtlib
                    # flagged via double quotes
                    gapl_imports.append(external.replace('"', ''))
                    break  # only import ONE quote enclosed file
                if external.startswith('//'):
                    # once we encounter a comment, stop parsing
                    break
        elif line.startswith('input '):
            # obtain right part of input line
            inp = ' '.join(line.split(' ')[1:])
            if ('<' in inp) and ('>' in inp):
                # check for multi track
                gapl_inputs = list(map(str.strip, inp.replace(
                    '<', '').replace('>', '').split()))
            else:
                # single track
                gapl_inputs = [inp]

    if len(gapl_inputs) == 0:
        # by default, user must NOT specify singletrack raw as input
        gapl_inputs = ['raw']

    return {'imports': gapl_imports, 'inputs': gapl_inputs,
            'header': {'comments': list(map(markdown.markdown, comments)),
                       'code': code}}


def _parse_gapl_signature(block: [str]):
    """Extracts single signatur from according part of GAP-L programs.

    Parameters
    ----------
    block : [str]
        The code lines between the beginning of the signature and first
        algebra.

    Returns
    -------
    {'signatures': {name: [str]},
     'comments': {'signature': [str]}}
    """
    code, comments = _extract_comments(block)

    name = code[0].split()[1].split('(')[0]

    return {'signatures': {name: {'code': code,
                                  'comments': comments,
                                  'position': 0}}}


def _parse_gapl_single_algebra_grammar(block, position=0):
    """Extract code and comments of a single algebra or grammar block"""
    code, comments = _extract_comments(block)

    name = code[0].split()[1].split('(')[0]

    return {'name': name, 'position': position,
            'code': code, 'comments': comments}


def _parse_gapl_algebras(block):
    """Extracts algebras(s) from according part of GAP-L programs.

    Parameters
    ----------
    block : [str]
        The code lines between beginning of the first algebra and the beginning
        of the first grammar.

    Returns
    -------
    {'algebras': {alg_name1: {'code': [str], 'comments': [str],
                              position: int},
                  alg_name2: {'code': [str], 'comments': [str],
                              position: int}}}
    """
    # subdivide into individual algebras
    alg_blocks = []
    blk = []
    for line in block:
        if line.startswith('algebra '):
            if ((' auto ' in line) or
               (' implements ' in line) or
               (' extends ' in line)):
                if len(blk) > 0:
                    alg_blocks.append(blk)
                blk = [line]
        else:
            blk.append(line)
    if len(blk) > 0:
        alg_blocks.append(blk)

    # iterate sub-blocks and parse algebra
    res = dict()
    for i, alg in enumerate(alg_blocks):
        alg_dict = _parse_gapl_single_algebra_grammar(alg, i)
        res[alg_dict['name']] = {k: v
                                 for k, v
                                 in alg_dict.items()
                                 if k != 'name'}

    return {'algebras': res}


def _parse_gapl_grammars(block):
    """Extracts grammar(s) from according part of GAP-L programs.

    Parameters
    ----------
    block : [str]
        The code lines between beginning of the first grammar and the beginning
        of the first instance.

    Returns
    -------
    {'grammars': {gra_name1: {'code': [str], 'comments': [str], position: int},
                  gra_name2: {'code': [str], 'comments': [str], position: int},
    }}
    """
    # subdivide into individual grammars
    gra_blocks = []
    blk = []
    for line in block:
        if line.startswith('grammar '):
            if (' uses ' in line) and ('axiom' in line):
                if len(blk):
                    gra_blocks.append(blk)
                blk = [line]
        else:
            blk.append(line)
    if len(blk) > 0:
        gra_blocks.append(blk)

    # iterate sub-blocks and parse grammar
    res = dict()
    for i, gra in enumerate(gra_blocks):
        gra_dict = _parse_gapl_single_algebra_grammar(gra, i)
        res[gra_dict['name']] = {k: v
                                 for k, v
                                 in gra_dict.items()
                                 if k != 'name'}

    return {'grammars': res}


def _parse_gapl_footer(block):
    """Extracts instances(s) from according part of GAP-L programs.

    Parameters
    ----------
    block : [str]
        The code lines between beginning of the first instance and the end of
        the program.

    Returns
    -------
    {'instances': {ins_name1: {'code': [str], 'comments': [str],
                   position: int},
                   ins_name2: {'code': [str], 'comments': [str],
                   position: int},
    }}
    """
    # subdivide into individual instances
    ins_blocks = []
    blk = []
    for line in block:
        if line.startswith('instance '):
            if ('=' in line) and (';' in line):
                if len(blk) > 0:
                    ins_blocks.append(blk)
                blk = [line]
        else:
            blk.append(line)
    if len(blk) > 0:
        ins_blocks.append(blk)

    # iterate sub-blocks and parse instance
    res = dict()
    for i, ins in enumerate(ins_blocks):
        ins_dict = _parse_gapl_single_algebra_grammar(ins, i)
        res[ins_dict['name']] = {k: v
                                 for k, v
                                 in ins_dict.items()
                                 if k != 'name'}

    return {'instances': res}


def _shift_comments(gapl):
    """All comments are by now associated to the "wrong" program component,
       i.e. the component ABOVE the comment. However, if makes semantically
       more sense to assign it to the component BELOW the comment.
    """
    srt_instances = sorted(gapl['instances'].items(),
                           key=lambda item: (item[1]['position']),
                           reverse=True)

    # store last comment in a new field calles "footer"
    gapl['footer'] = {'comments':
                      gapl['instances'][srt_instances[0][0]]['comments']}

    # move every comment one component "down"
    for _next, curr in zip(srt_instances, srt_instances[1:]):
        gapl['instances'][_next[0]]['comments'] = \
            gapl['instances'][curr[0]]['comments']

    srt_grammars = sorted(gapl['grammars'].items(),
                          key=lambda item: (item[1]['position']), reverse=True)
    gapl['instances'][srt_instances[-1][0]]['comments'] = \
        gapl['grammars'][srt_grammars[0][0]]['comments']
    for _next, curr in zip(srt_grammars, srt_grammars[1:]):
        gapl['grammars'][_next[0]]['comments'] = \
            gapl['grammars'][curr[0]]['comments']

    srt_algebras = sorted(gapl['algebras'].items(),
                          key=lambda item: (item[1]['position']),
                          reverse=True)
    gapl['grammars'][srt_grammars[-1][0]]['comments'] = \
        gapl['algebras'][srt_algebras[0][0]]['comments']
    for _next, curr in zip(srt_algebras, srt_algebras[1:]):
        gapl['algebras'][_next[0]]['comments'] = \
            gapl['algebras'][curr[0]]['comments']

    srt_signatures = sorted(gapl['signatures'].items(),
                            key=lambda item: (item[1]['position']),
                            reverse=True)
    gapl['algebras'][srt_algebras[-1][0]]['comments'] = \
        gapl['signatures'][srt_signatures[0][0]]['comments']
    for _next, curr in zip(srt_signatures, srt_signatures[1:]):
        gapl['signatures'][_next[0]]['comments'] = \
            gapl['signatures'][curr[0]]['comments']

    gapl['signatures'][srt_signatures[-1][0]]['comments'] = \
        gapl['header']['comments']


def _extract_example_inputs(gapl):
    if 'example_inputs' in gapl.keys():
        return gapl['example_inputs']

    example_inputs = []
    for name in gapl['instances'].keys():
        for i in range(len(gapl['instances'][name]['comments'])):
            cmt = gapl['instances'][name]['comments'][i]
            if cmt.startswith('example inputs:'):
                example_inputs = cmt[len('example inputs:'):].strip().split()
                gapl['instances'][name]['comments'].pop(i)
                return example_inputs
    return example_inputs


def _include_code(lines, fp_current):
    """Make sub-file 'include' of gapc explicit by joining all code lines.

    Returns
    -------
    [str], [str]: Tuple of two lists. First list are all code lines combined,
                  second list contains included file paths.
    """
    pattern = re.compile(r'\s*include "(.+)"')

    comb_lines = []
    sub_files = []
    for line in lines:
        hit = pattern.match(line)
        if hit is not None:
            fp_subfile = os.path.join(
                os.path.dirname(fp_current), hit.group(1))
            if os.path.exists(fp_subfile):
                with open(fp_subfile, 'r') as f:
                    sublines = f.readlines()
                    sub_files.append(fp_subfile)
                    res_lines, res_files = _include_code(sublines, fp_current)
                    comb_lines.extend(res_lines)
                    sub_files.extend(res_files)
        else:
            comb_lines.append(line)

    return comb_lines, sub_files


def _header_includes(fp_prefix, imports):
    pattern = re.compile(r'^#include\s+"(\S+\.hh)"')

    include_files = imports.copy()
    for imp in imports:
        with open(os.path.join(fp_prefix, imp), 'r') as f:
            for line in f.readlines():
                hit = pattern.match(line)
                if hit is not None:
                    fp_sub = os.path.join(os.path.dirname(imp), hit.group(1))
                    if os.path.exists(os.path.join(fp_prefix, fp_sub)):
                        include_files.extend(
                            _header_includes(fp_prefix, [fp_sub]))
    return sorted(list(set(include_files)))


def parse_gapl(fp_program):
    """Parses a GAP-L code file and returns elements in a dict structure."""
    gapl = dict()

    with open(fp_program, 'r') as f:
        saw_signature = False
        saw_algebra = False
        saw_grammar = False
        saw_instance = False

        lines, includefiles = _include_code(f.readlines(), fp_program)
        gapl['include_files'] = includefiles
        gapl['codelines'] = lines
        block = []

        for i in range(len(lines)):
            line = lines[i].strip()
            tup = (saw_signature, saw_algebra, saw_grammar, saw_instance)
            if ((tup == (False, False, False, False)) and
               line.startswith('signature ') and
               ('(alphabet, ' in line)):
                saw_signature = True
                gapl.update(_parse_gapl_header(block))
                block = []
            elif ((tup == (True, False, False, False)) and
                  line.startswith('algebra ') and
                  ((' implements ' in line) or
                   (' auto ' in line))):
                saw_algebra = True
                gapl.update(_parse_gapl_signature(block))
                block = []
            elif ((tup == (True, True, False, False)) and
                  line.startswith('grammar ') and
                  (' uses ' in line) and ('axiom' in line)):
                gapl.update(_parse_gapl_algebras(block))
                saw_grammar = True
                block = []
            elif ((tup == (True, True, True, False)) and
                  line.startswith('instance ') and
                  ('=' in line) and (';' in line)):
                gapl.update(_parse_gapl_grammars(block))
                block = []
                saw_instance = True

            block.append(lines[i])

        gapl.update(_parse_gapl_footer(block))

    _shift_comments(gapl)
    gapl['example_inputs'] = _extract_example_inputs(gapl)

    # extend recurvively included header files
    gapl['imports'] = _header_includes(
        os.path.dirname(fp_program), gapl['imports'])

    return gapl


def get_gapc_programs(fp_dir, verbose=sys.stderr):
    res = dict()
    for fp_gapl in sorted(glob.glob(os.path.join(fp_dir, '*.gap'))):
        name = fp_gapl.split('/')[-1][:-1*len('.gap')]
        if verbose:
            log("Parsing '%s' ..." % os.path.basename(fp_gapl),
                'info', verbose)
        res[name] = parse_gapl(fp_gapl)
        if verbose:
            log(" found %i algebras, %i grammars and %i instances\n" % (
                len(res[name]['algebras']), len(res[name]['grammars']),
                len(res[name]['instances'])), 'info', verbose)
    return res
