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


def compile_and_run_gapc(grammar: str, algproduct: str, fp_gapfile: str,
                         prefix_cache, userinputs: [str],
                         plot_grammar_level: int = 1, outside: bool = False,
                         fps_headerfiles: [str] = [],
                         limit_candidate_trees: int = 20):
    """Compiles a binary for a given instance (aka algebra product).

    Parameters
    ----------
    grammar : str
        The user selected grammar.

    algproduct : str
        The algebra product to be compiled, e.g. "alg_score * alg_enum".

    fp_gapfile : str
        File path location of the user gap source file.

    prefix_cache : str
        Directory to used to cache compile product.

    userinputs : [str]
        List of user input(s) for tracks of grammar.

    plot_grammar_level : int
        Determines the level of detail when plotting the grammar.

    outside : bool
        Activates automatic generation of outside grammar generation.

    fps_headerfiles : [str]
        List of additional user header files, necessary for C++ compilation.
    """
    # update the global gapc version number as the according ubuntu package
    # might have changed during server execution time
    global GAPC_VERSION
    GAPC_VERSION = get_gapc_version(app)

    # update global commit hash of user repository as it might change during
    # server run time through cron jobs
    global REPO_VERSION
    REPO_VERSION = get_repo_commithash(app, PREFIX_GAPUSERSOURCES)

    # the instance is the application of the algebra product to the grammar
    instance = '%s(%s)' % (grammar, algproduct)
    hash_instance = hashlib.md5(("%s_%i_%s" % (
        instance, plot_grammar_level, outside)).encode('utf-8')).hexdigest()
    fp_workdir = os.path.join(prefix_cache, hash_instance)
    app.logger.info('working directory for instance "%s" is "%s"' % (
        instance, fp_workdir))

    param_outside = " --outside_grammar ALL " if outside else ""
    steps = {
        # 0) inject instance bcafe to original *.gap source file (as it might
        #    not be defined)
        # 1) transpiling via gapc
        'gapc': ('echo "instance bcafe=%s;" >> "%s" '
                 '&& gapc -i "bcafe" --plot-grammar %i %s %s ') % (
            instance, os.path.basename(fp_gapfile), plot_grammar_level,
            param_outside,
            os.path.basename(fp_gapfile)),

        # 2) convert grammar plot into gif
        'dot': 'dot -Tgif out.dot -o grammar.gif',

        # 3) compiling c++ into binary
        'make': 'make -f out.mf',

        # 4) run the compiled binary with user input (not cached)
        'run': '../out %s' % ' '.join(map(lambda x: '"%s"' % x, userinputs)),

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
        # has changed. This might be due to updates in the ADP_collections repo
        invalid_cache = False
        for fp_src in [fp_gapfile] + fps_headerfiles:
            fp_dst = os.path.join(fp_workdir, os.path.basename(fp_src))
            if os.path.exists(fp_dst):
                dst = fp_dst
                if fp_src == fp_gapfile:
                    # ignore last line of gap source file, since this is the
                    # injected instance
                    dst = '<(head %s -n -1)' % fp_dst
                p_diff = subprocess.run(
                    'diff %s %s' % (fp_src, dst), shell=True, text=True,
                    executable='/bin/bash')
                if p_diff.returncode != 0:
                    invalid_cache = True
        if invalid_cache:
            shutil.rmtree(fp_workdir)
            app.logger.info('delete outdated cache dir "%s"' % fp_workdir)

    if not os.path.exists(fp_workdir):
        os.makedirs(fp_workdir, exist_ok=True)
        app.logger.info('create working directory "%s"' % fp_workdir)

        # copy *.gap and header source files into working directory
        for fp_src in [fp_gapfile] + fps_headerfiles:
            fp_dst = os.path.join(fp_workdir, os.path.basename(fp_src))
            shutil.copy(fp_src, fp_dst)
            app.logger.info('copy file "%s" to %s' % (fp_src, fp_dst))

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
            app.logger.info('executing (in %s) "%s"' % (fp_workdir, cmd))

    inputs_hash = hashlib.md5(''.join(userinputs).encode('utf-8')).hexdigest()
    fp_binary_workdir = os.path.join(fp_workdir, 'run_%s' % inputs_hash)
    uses_tikz = False
    if not os.path.exists(fp_binary_workdir):
        os.makedirs(fp_binary_workdir, exist_ok=True)

        # execute the binary with user input(s)
        child = subprocess.run(steps['run'], shell=True, text=True,
                               cwd=fp_binary_workdir)
        app.logger.info('no cached results found, thus executing (in %s) "%s"'
                        % (fp_binary_workdir, steps['run']))
        with open(os.path.join(fp_binary_workdir, 'run.exitstatus'), 'w') as f:
            f.write('%i\n' % child.returncode)

        if child.returncode == 0:
            with open(os.path.join(fp_binary_workdir, 'run.out'), 'r') as f:
                if 'documentclass' in f.readlines()[0]:
                    uses_tikz = True
                    app.logger.info('found tikZ tree descriptions.')

                    # modify original binary stdout such that it contains
                    # at most limit_candidate_trees many trees to limit server
                    # workload when compiling individual candidate PNGs
                    modify_tikz_file(
                        os.path.join(fp_binary_workdir, 'run.out'),
                        os.path.join(fp_binary_workdir, 'tikz.tex'),
                        limit_candidate_trees)

                    child = subprocess.run(steps['tikz'], shell=True,
                                           text=True, cwd=fp_binary_workdir)
                    app.logger.info(
                        'executing (in %s) "%s"' % (fp_binary_workdir,
                                                    steps['tikz']))
                    with open(os.path.join(fp_binary_workdir,
                                           'tikz.exitstatus'), 'w') as f:
                        f.write('%i\n' % child.returncode)
    else:
        uses_tikz = os.path.exists(os.path.join(fp_binary_workdir, 'tikz.tex'))
        app.logger.info('found cached binary results.')

    report = []
    for name, cmd in steps.items():
        fp_cache = fp_workdir
        if name in ["run", "tikz"]:
            fp_cache = fp_binary_workdir
        if (name == "tikz") and (uses_tikz is False):
            report.append([[], 0])
            continue
        exit_status = None
        rep = []
        rep.append('<b>Command</b>: %s' % cmd)
        with open(os.path.join(fp_cache, '%s.out' % name)) as f:
            rep.extend(f.readlines())
        with open(os.path.join(fp_cache, '%s.err' % name)) as f:
            rep.extend(f.readlines())
        # read exit status of step
        exit_status = read_exit_status_file(
            os.path.join(fp_cache, '%s.exitstatus' % name))
        if (name == 'tikz') and uses_tikz:
            rep = []
            for rank, fp_candidate in enumerate(sorted(
                    glob.glob(os.path.join(fp_cache, 'tikz-figure*.png')),
                    key=lambda x: int(x.split('figure')[1].split('.')[0]))):
                if (os.stat(fp_candidate).st_size > 0):
                    with open(fp_candidate, "rb") as image:
                        rep.append(base64.b64encode(image.read()).decode(
                            'utf-8'))
                if rank+1 >= limit_candidate_trees:
                    app.logger.info(
                        ('number of candidates exceeds displaying limit of '
                         'top %i!') % limit_candidate_trees)
                    break

        # don't add dot execution to report, since there is no tab yet on the
        # website
        if name not in ['dot']:
            report.append([rep, exit_status])

    # a bit hacky, but this is to serve dynamically generated images from cache
    # which is not directly exposed to the web. We load the GIF content as
    # base64 encoded string and paste this directly as src="" into an image tag
    # Note: previous compile errors might lead to a missing out.dot file!
    fp_plot = os.path.join(fp_workdir, "grammar.gif")
    if os.path.exists(fp_plot) and (os.stat(fp_plot).st_size > 0):
        with open(fp_plot, "rb") as image:
            report.append([base64.b64encode(image.read()).decode('utf-8'), 0])
    else:
        report.append(["error", 1])

    return report
