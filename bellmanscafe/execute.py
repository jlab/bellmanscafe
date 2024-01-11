import sys
import hashlib
import shutil
import subprocess
import base64
import os
import glob

from bellmanscafe.cafe import get_gapc_version, get_repo_commithash, log, get_codefiles_hash

def read_exit_status_file(fp):
    """Read a file into which the exit code has been written.

    Parameters
    ----------
    fp : str
        Filepath to file containing the numeric exit status.

    Returns
    -------
    int = the exit status

    Note
    ----
    Also returns 1, i.e. error, if
        - file path does not exist
        - file exists, but has no content
    """
    if not os.path.exists(fp):
        return 1
    with open(fp, 'r') as f:
        lines = f.readlines()
        if len(lines) < 1:
            return 1
        else:
            try:
                return int(lines[0].strip())
            except ValueError:
                return 1


def modify_tikz_file(fp_orig, fp_limited, max_candidates=20):
    with open(fp_orig, 'r') as fR:
        candidate_counter = 0
        with open(fp_limited, 'w') as fW:
            for line in fR.readlines():
                if line.startswith("\\end{tikzpicture}"):
                    candidate_counter += 1
                fW.write(line)
                if candidate_counter >= max_candidates:
                    fW.write('\\end{document}\n')
                    break


def compile_and_run_gapc(gapl_programs, user_input, settings, max_algebras, limit_candidate_trees: int = 20,
                         verbose=sys.stderr):
    """Compiles a binary for a given instance (aka algebra product).

    Parameters
    ----------
    userinputs : ?
        ?

    """
    # update the global gapc version number as the according ubuntu package
    # might have changed during server execution time
    settings['versions']['gapc'] = get_gapc_version(verbose)

    # update global commit hash of user repository as it might change during
    # server run time through cron jobs
    settings['versions']['ADP_collection'] = get_repo_commithash(settings['paths']['gapc_programs'], verbose)

    # the instance is the application of the algebra product to the grammar
    instance = user_input['select_grammar'] + '('
    for idx in range(1, max_algebras+1):
        if user_input['algebra_%i' % idx] != 'empty':
            instance += user_input['algebra_%i' % idx]
        if (idx == max_algebras) or (user_input['algebra_%i' % (idx+1)] != 'empty'):
            instance += user_input['product_%i' % idx]
        else:
            break
    instance += ')'

    hash_instance = hashlib.md5(("%s_%s_%s_%s" % (
        user_input['select_program'], instance, user_input['plot_grammar'], 'outside_grammar' in user_input)).encode('utf-8')).hexdigest()
    fp_workdir = os.path.join(settings['paths']['prefix_cache'], hash_instance)
    log('working directory for instance "%s" is "%s"\n' % (
        instance, fp_workdir), "info", verbose)

    param_outside = " --outside_grammar ALL " if 'outside_grammar' in user_input else ""

    inputstrings = []
    for key, value in user_input.items():
        if key.startswith('userinput_'):
            inputstrings.append((int(key.split('_')[-1]), value))
    inputstrings = [value for (pos, value) in sorted(inputstrings, key=lambda x: x[0])]

    fp_gapfile = os.path.join(settings['paths']['gapc_programs'], user_input['select_program']+'.gap')
    fps_headerfiles = list(map(lambda x: os.path.join(settings['paths']['gapc_programs'], x), gapl_programs[user_input['select_program']]['imports']))
    steps = {
        # 0) inject instance bcafe to original *.gap source file (as it might
        #    not be defined)
        # 1) transpiling via gapc
        'gapc': ('echo "\ninstance bcafe=%s;" >> "%s" '
                 '&& gapc -i "bcafe" --plot-grammar %s %s %s ') % (
            instance, os.path.basename(fp_gapfile), user_input['plot_grammar'],
            param_outside,
            os.path.basename(fp_gapfile)),

        # 2) convert grammar plot into gif
        'dot': 'dot -Tgif out.dot -o grammar.gif',

        # 3) compiling c++ into binary
        'make': 'make -f out.mf',

        # 4) run the compiled binary with user input (not cached)
        'run': '../out %s' % ' '.join(map(lambda x: '"%s"' % x, inputstrings)),

        # 5) OPTIONAL: if algebra product uses tikZ, images will be rendered
        'tikz': '/usr/bin/time -v -o pdflatex.benchmark pdflatex tikz.tex '
                '2>> tikz.err && '
                '/usr/bin/time -v -o pdfmake.benchmark make -f tikz.makefile '
                '2>> tikz.err && '
                'mv -v tikz.log tikz.out 2>> tikz.err'
    }
    steps = {name: 'time -v -o "%s.benchmark" %s > %s.out 2> %s.err' % (
             name, cmd, name, name) if name not in ['tikz'] else cmd
             for name, cmd
             in steps.items()}

    if os.path.exists(fp_workdir):
        # if a matching cache dir exists, we test if the source file contents
        # has changed.
        hash_program = get_codefiles_hash([fp_gapfile] + fps_headerfiles)
        invalid_cache = not os.path.exists(os.path.join(fp_workdir, '%s.codehash' % hash_program))
        if invalid_cache:
            shutil.rmtree(fp_workdir)
            log('delete outdated cache dir "%s"\n' % fp_workdir, 'info', verbose)

    if not os.path.exists(fp_workdir):
        os.makedirs(fp_workdir, exist_ok=True)
        log('create working directory "%s"\n' % fp_workdir, 'info', verbose)

        hash_program = get_codefiles_hash([fp_gapfile] + fps_headerfiles)
        with open(os.path.join(fp_workdir, '%s.codehash' % hash_program), 'w') as f:
            f.write('\n'.join([fp_gapfile] + fps_headerfiles))

        # copy *.gap and header source files into working directory
        for fp_src in [fp_gapfile] + fps_headerfiles:
            fp_dst = os.path.join(fp_workdir, os.path.basename(fp_src))
            shutil.copy(fp_src, fp_dst)
            log('copy file "%s" to %s\n' % (fp_src, fp_dst), 'info', verbose)

        for name, cmd in steps.items():
            if name in ["run", "tikz"]:
                # don't run the compiled binary in here since it shall not be
                # part of the cache
                continue
            child = subprocess.run(cmd, shell=True, text=True, cwd=fp_workdir)
            # we explicitly store the exit status into an extra file ... to
            # better indicate errors in the webpage
            with open(os.path.join(fp_workdir,
                                   '%s.exitstatus' % name), 'w') as f:
                f.write('%i\n' % child.returncode)
            log('executing (in %s) "%s"\n' % (fp_workdir, cmd), 'info', verbose)

    inputs_hash = hashlib.md5(''.join(inputstrings).encode('utf-8')).hexdigest()
    fp_binary_workdir = os.path.join(fp_workdir, 'run_%s' % inputs_hash)
    uses_tikz = False
    if not os.path.exists(fp_binary_workdir):
        os.makedirs(fp_binary_workdir, exist_ok=True)

        # execute the binary with user input(s)
        child = subprocess.run(steps['run'], shell=True, text=True,
                               cwd=fp_binary_workdir)
        log('no cached results found, thus executing (in %s) "%s"\n'
                        % (fp_binary_workdir, steps['run']), 'info', verbose)
        with open(os.path.join(fp_binary_workdir, 'run.exitstatus'), 'w') as f:
            f.write('%i\n' % child.returncode)

        if child.returncode == 0:
            with open(os.path.join(fp_binary_workdir, 'run.out'), 'r') as f:
                if 'documentclass' in f.readlines()[0]:
                    uses_tikz = True
                    log('found tikZ tree descriptions.\n', 'info', verbose)

                    # modify original binary stdout such that it contains
                    # at most limit_candidate_trees many trees to limit server
                    # workload when compiling individual candidate PNGs
                    modify_tikz_file(
                        os.path.join(fp_binary_workdir, 'run.out'),
                        os.path.join(fp_binary_workdir, 'tikz.tex'),
                        limit_candidate_trees)

                    child = subprocess.run(steps['tikz'], shell=True,
                                           text=True, cwd=fp_binary_workdir)
                    log('executing (in %s) "%s"\n' % (fp_binary_workdir,
                                                    steps['tikz']), 'info', verbose)
                    with open(os.path.join(fp_binary_workdir,
                                           'tikz.exitstatus'), 'w') as f:
                        f.write('%i\n' % child.returncode)
    else:
        uses_tikz = os.path.exists(os.path.join(fp_binary_workdir, 'tikz.tex'))
        log('found cached binary results.\n', 'info', verbose)

    report = {'versions': settings['versions']}
    for name, cmd in steps.items():
        fp_cache = fp_workdir
        if name in ["run", "tikz"]:
            fp_cache = fp_binary_workdir
        rep = {'command': cmd, 'stdout': [], 'stderr': [], 'benchmark': []}
        if (name not in ['tikz', 'dot']):
            with open(os.path.join(fp_cache, '%s.out' % name)) as f:
                rep['stdout'].extend(f.readlines())
        if (name not in ['tikz']) or uses_tikz:
            with open(os.path.join(fp_cache, '%s.err' % name)) as f:
                rep['stderr'].extend(f.readlines())
            # read exit status of step
            rep['exit_status'] = read_exit_status_file(
                os.path.join(fp_cache, '%s.exitstatus' % name))
        if (name not in ['tikz']):
            with open(os.path.join(fp_cache, '%s.benchmark' % name)) as f:
                rep['benchmark'].extend(f.readlines())
        if (name == 'tikz') and uses_tikz:
            for rank, fp_candidate in enumerate(sorted(
                    glob.glob(os.path.join(fp_cache, 'tikz-figure*.png')),
                    key=lambda x: int(x.split('figure')[1].split('.')[0]))):
                if (os.stat(fp_candidate).st_size > 0):
                    with open(fp_candidate, "rb") as image:
                        rep['stdout'].append(base64.b64encode(image.read()).decode(
                            'utf-8'))
                if rank+1 >= limit_candidate_trees:
                    log(('number of candidates exceeds displaying limit of '
                         'top %i!\n') % limit_candidate_trees, 'info', verbose)
                    break

        report[name] = rep

    # a bit hacky, but this is to serve dynamically generated images from cache
    # which is not directly exposed to the web. We load the GIF content as
    # base64 encoded string and paste this directly as src="" into an image tag
    # Note: previous compile errors might lead to a missing out.dot file!
    fp_plot = os.path.join(fp_workdir, "grammar.gif")
    if os.path.exists(fp_plot) and (os.stat(fp_plot).st_size > 0):
        with open(fp_plot, "rb") as image:
            report['dot']['stdout'] = [base64.b64encode(image.read()).decode('utf-8')]
    else:
        report['dot']['exit_status'] = 1

    print("\n\n\nREPORT", report, file=sys.stderr)
    return report
