import sys
import hashlib
import shutil
import subprocess
import base64
import os
import glob
import time

from bellmanscafe.cafe import get_gapc_version, get_repo_commithash, log, \
    get_codefiles_hash
from bellmanscafe.parse_gapl import _include_code


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
    within_maximum = True
    candidate_counter = 0
    with open(fp_orig, 'r') as fR:
        with open(fp_limited, 'w') as fW:
            for line in fR.readlines():
                if line.startswith("\\end{tikzpicture}"):
                    candidate_counter += 1
                if within_maximum:
                    fW.write(line)
                    if candidate_counter >= max_candidates:
                        fW.write('\\end{document}\n')
                        within_maximum = False
    return candidate_counter


def compile_and_run_gapc(gapl_programs, user_input, settings,
                         verbose=sys.stderr, retry=10, waitfor=20):
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
    settings['versions']['ADP_collection'] = get_repo_commithash(
        settings['paths']['gapc_programs'], verbose)

    # the instance is the application of the algebra product to the grammar
    instance = user_input['select_grammar'] + '('
    for idx in range(1, settings['max_algebras']+1):
        if 'algebra_%i' % idx not in user_input.keys():
            break
        if user_input['algebra_%i' % idx] != 'empty':
            instance += user_input['algebra_%i' % idx]
        if ((idx < settings['max_algebras']) and
           ('algebra_%i' % (idx+1) in user_input.keys()) and
           (user_input['algebra_%i' % (idx+1)] != 'empty')):
            instance += user_input['product_%i' % idx]
        else:
            break
    instance += ')'

    hash_instance = hashlib.md5(("%s_%s_%s_%s" % (
        user_input['select_program'], instance, user_input['plot_grammar'],
        'outside_grammar' in user_input)).encode('utf-8')).hexdigest()
    fp_workdir = os.path.join(settings['paths']['prefix_cache'], hash_instance)
    log('working directory for instance "%s" is "%s"\n' % (
        instance, fp_workdir), "info", verbose)

    param_outside = ""
    if 'outside_grammar' in user_input:
        param_outside = " --outside_grammar ALL "

    inputstrings = []
    for key, value in user_input.items():
        if key.startswith('userinput_'):
            inputstrings.append((int(key.split('_')[-1]), value))
    inputstrings = [value
                    for (pos, value)
                    in sorted(inputstrings, key=lambda x: x[0])]

    fp_gapfile = os.path.join(settings['paths']['gapc_programs'],
                              user_input['select_program']+'.gap')
    # since an original gapc file might contain includes of sub-files,
    # we first recursively combine the gapc file and store it in the working
    # directory
    fp_gapfile_combined = os.path.join(fp_workdir,
                                       user_input['select_program']+'.gap')

    # list of tuples for src and dst file paths
    fps_headerfiles = list(map(
        lambda x: (os.path.join(settings['paths']['gapc_programs'], x), x),
        gapl_programs[user_input['select_program']]['imports']))
    steps = {
        # 0) inject instance bcafe to original *.gap source file (as it might
        #    not be defined)
        # 1) transpiling via gapc
        'gapc': {'cmds': ('echo "\ninstance bcafe=%s;" >> "%s" '
                          '&& gapc -i "bcafe" --plot-grammar %s %s %s ') % (
            instance, os.path.basename(fp_gapfile_combined),
            user_input['plot_grammar'],
            param_outside,
            os.path.basename(fp_gapfile_combined))},

        # 2) convert grammar plot into gif
        'dot': {'cmds': 'dot -Tgif out.dot -o grammar.gif'},

        # 3) compiling c++ into binary
        'make': {'cmds': 'make -f out.mf'},

        # 4) create a file to indicate that binary execution (or abortion) is
        #    complete. This avoids concurrency issues, where two users are
        #    triggering execution of the same instance
        'flag_ready_binary': {'cmds': 'touch binary.ready'},

        # 5) run the compiled binary with user input (not cached)
        'run': {'cmds': '../out %s' % ' '.join(map(lambda x: '"%s"' % x,
                                                   inputstrings))},

        # 6) OPTIONAL: if algebra product uses tikZ, images will be rendered
        'tikz': {
            'cmds':
                '/usr/bin/time -v -o pdflatex.benchmark pdflatex tikz.tex '
                '2>> tikz.err && '
                '/usr/bin/time -v -o pdfmake.benchmark make -f tikz.makefile '
                '2>> tikz.err && '
                'mv -v tikz.log tikz.out 2>> tikz.err',
            'benchmarks': ['pdflatex.benchmark', 'pdfmake.benchmark']}
    }

    # add default benchmarking to steps (except tikz)
    for name in steps.keys():
        if name not in ['tikz']:
            steps[name]['cmds'] = ('ulimit -t %s; '  # limit CPU time
                                   'time -v -o "%s.benchmark" %s'
                                   ' > %s.out 2> %s.err') % (
                                   settings['max_cpu_time'], name,
                                   steps[name]['cmds'], name, name)
            steps[name]['benchmarks'] = ["%s.benchmark" % name]
    # steps = {name: 'time -v -o "%s.benchmark" %s > %s.out 2> %s.err' % (
    #          name, cmd, name, name) if name not in ['tikz'] else cmd
    #          for name, cmd
    #          in steps.items()}

    if os.path.exists(fp_workdir):
        # if a matching cache dir exists, we test if the source file contents
        # has changed.
        hash_program = get_codefiles_hash(
            [fp_gapfile_combined] + [tpl[0] for tpl in fps_headerfiles])
        invalid_cache = not os.path.exists(
            os.path.join(fp_workdir, '%s.codehash' % hash_program))
        # due to concurrency, another process might be in the status of
        # building this instance at this moment. Instance building should at
        # the very end create an empty file "binary.ready". If this file is NOT
        # there, the cache should not be used
        if (invalid_cache is False) and \
           (not os.path.exists(os.path.join(fp_workdir, 'binary.ready'))):
            # we now assume that another process is currently building the
            # binary. Thus, we wait for X seconds and double check again
            for i in range(retry):
                log('looks like another process is trying to build the same'
                    ' instance. Wait for it for %isec ... %i\n' % (waitfor, i),
                    'info', verbose)
                time.sleep(waitfor)
                if os.path.exists(os.path.join(fp_workdir, 'binary.ready')):
                    break
            # if waiting for 20sec, 10 times did not suffice to generate
            # binary, something might have gone wrong and we try to build it
            # here again!
            invalid_cache = True
        # if cache is invalid, due to program file changes OR previous attempts
        # failed, delete the cache and try again.
        if invalid_cache:
            shutil.rmtree(fp_workdir)
            log('delete outdated cache dir "%s"\n' % fp_workdir, 'info',
                verbose)

    if not os.path.exists(fp_workdir):
        os.makedirs(fp_workdir, exist_ok=True)
        log('create working directory "%s"\n' % fp_workdir, 'info', verbose)

        # create a gap file that contains all includes in working directory
        with open(fp_gapfile, 'r') as f:
            with open(fp_gapfile_combined, 'w') as w:
                w.write(''.join(_include_code(f.readlines(), fp_gapfile)))

        hash_program = get_codefiles_hash(
            [fp_gapfile_combined] + [tpl[0] for tpl in fps_headerfiles])
        with open(os.path.join(fp_workdir,
                               '%s.codehash' % hash_program), 'w') as f:
            f.write('\n'.join(
                [fp_gapfile_combined] + [tpl[0] for tpl in fps_headerfiles]))

        # copy header source files into working directory
        for (fp_src, fp_relative_dst) in fps_headerfiles:
            if os.path.dirname(fp_relative_dst) != "":
                os.makedirs(os.path.join(
                    fp_workdir, os.path.dirname(fp_relative_dst)),
                    exist_ok=True)
            fp_dst = os.path.join(fp_workdir, fp_relative_dst)
            print(fp_src, fp_dst)
            shutil.copy(fp_src, fp_dst)
            log('copy file "%s" to %s\n' % (fp_src, fp_dst), 'info', verbose)

        for name in steps.keys():
            if name in ["run", "tikz"]:
                # don't run the compiled binary in here since it shall not be
                # part of the cache
                continue
            child = subprocess.run(steps[name]['cmds'], shell=True,
                                   text=True, cwd=fp_workdir)
            # we explicitly store the exit status into an extra file ... to
            # better indicate errors in the webpage
            with open(os.path.join(fp_workdir,
                                   '%s.exitstatus' % name), 'w') as f:
                f.write('%i\n' % child.returncode)
            log('executing (in %s) "%s"\n' % (
                fp_workdir, steps[name]['cmds']), 'info', verbose)

    inputs_hash = hashlib.md5(
        ''.join(inputstrings).encode('utf-8')).hexdigest()
    fp_binary_workdir = os.path.join(fp_workdir, 'run_%s' % inputs_hash)
    uses_tikz = False
    if not os.path.exists(fp_binary_workdir):
        os.makedirs(fp_binary_workdir, exist_ok=True)

        # execute the binary with user input(s)
        child = subprocess.run(steps['run']['cmds'], shell=True, text=True,
                               cwd=fp_binary_workdir)
        log('no cached results found, thus executing (in %s) "%s"\n' % (
            fp_binary_workdir, steps['run']['cmds']),
            'info', verbose)
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
                    num_candidates = modify_tikz_file(
                        os.path.join(fp_binary_workdir, 'run.out'),
                        os.path.join(fp_binary_workdir, 'tikz.tex'),
                        settings['limit_candidate_trees'])
                    with open(os.path.join(fp_binary_workdir,
                                           'num_candidates.txt'), 'w') as N:
                        N.write(str(num_candidates))

                    child = subprocess.run(steps['tikz']['cmds'], shell=True,
                                           text=True, cwd=fp_binary_workdir)
                    log('executing (in %s) "%s"\n' % (
                        fp_binary_workdir, steps['tikz']['cmds']),
                        'info', verbose)
                    with open(os.path.join(fp_binary_workdir,
                                           'tikz.exitstatus'), 'w') as f:
                        f.write('%i\n' % child.returncode)
    else:
        uses_tikz = os.path.exists(os.path.join(fp_binary_workdir, 'tikz.tex'))
        log('found cached binary results.\n', 'info', verbose)

    report = {'versions': settings['versions']}
    for name in steps.keys():
        fp_cache = fp_workdir
        if name in ["run", "tikz"]:
            fp_cache = fp_binary_workdir
        rep = {'command': steps[name]['cmds'], 'stdout': [], 'stderr': [],
               'cache': os.path.basename(fp_cache), 'runtime': 0, 'memory': 0}
        if (name not in ['tikz', 'dot']):
            with open(os.path.join(fp_cache, '%s.out' % name)) as f:
                for i, line in enumerate(f.readlines()):
                    rep['stdout'].append(line)
                    if i >= settings['max_output_lines']:
                        rep['stdout_warning'] = \
                            'output was limited to first %i lines' % settings[
                                'max_output_lines']
                        break
        if (name not in ['tikz']) or uses_tikz:
            with open(os.path.join(fp_cache, '%s.err' % name)) as f:
                rep['stderr'].extend(f.readlines())
            # read exit status of step
            rep['exit_status'] = read_exit_status_file(
                os.path.join(fp_cache, '%s.exitstatus' % name))
        if (name == 'tikz') and uses_tikz:
            tikz_imgs = sorted(
                glob.glob(os.path.join(fp_cache, 'tikz-figure*.png')),
                key=lambda x: int(x.split('figure')[1].split('.')[0]))
            for rank, fp_candidate in enumerate(tikz_imgs):
                if (os.stat(fp_candidate).st_size > 0):
                    with open(fp_candidate, "rb") as image:
                        rep['stdout'].append(
                            base64.b64encode(image.read()).decode('utf-8'))
                if rank+1 >= settings['limit_candidate_trees']:
                    log(('number of candidates exceeds displaying limit of '
                         'top %i!\n') % settings['limit_candidate_trees'],
                        'info', verbose)
                    break
            with open(os.path.join(fp_cache, 'num_candidates.txt'), 'r') as N:
                rep['total_number_tikz_candidates'] = int(
                    ''.join(N.readlines()))

        for fp_benchmark in steps[name]['benchmarks']:
            try:
                with open(os.path.join(fp_cache, fp_benchmark), 'r') as f:
                    for line in f.readlines():
                        if (('User time (seconds):' in line) or
                           ('System time (seconds):' in line)):
                            rep['runtime'] += float(
                                line.strip().split(': ')[-1])
                        elif 'Maximum resident set size (kbytes):' in line:
                            rep['memory'] += float(
                                line.strip().split(': ')[-1])
            except FileNotFoundError:
                pass
        # convert KB to MB
        rep['memory'] = '%.1f' % (rep['memory'] / 1024)
        rep['runtime'] = '%.1f' % rep['runtime']

        report[name] = rep

    # a bit hacky, but this is to serve dynamically generated images from cache
    # which is not directly exposed to the web. We load the GIF content as
    # base64 encoded string and paste this directly as src="" into an image tag
    # Note: previous compile errors might lead to a missing out.dot file!
    fp_plot = os.path.join(fp_workdir, "grammar.gif")
    if os.path.exists(fp_plot) and (os.stat(fp_plot).st_size > 0):
        with open(fp_plot, "rb") as image:
            report['dot']['stdout'] = [base64.b64encode(
                image.read()).decode('utf-8')]
    else:
        report['dot']['exit_status'] = 1

    report['program'] = user_input['select_program']
    return report
