import sys
import subprocess
import os
import logging
import hashlib


def log(msg, level='debug', verbose=sys.stderr):
    if isinstance(verbose, logging.Logger):
        if level == 'info':
            verbose.info(msg + '\n')
        else:
            verbose.debug(msg)
    else:
        verbose.write(msg)


def get_gapc_version(verbose=sys.stderr):
    """Obtain gapc version number via 'gapc --version' system call.

    Parameters
    ----------
    verbose :
        ???

    Returns
    -------
    str : the gapc version number
    """
    cmd = 'gapc --version | head -n 1 | cut -d " " -f 3'
    p_version = subprocess.run(cmd, shell=True, text=True,
                               stdout=subprocess.PIPE)
    version = p_version.stdout.strip()
    log('obtain gapc version number via "%s" = %s\n' % (cmd, version))

    return version


def get_repo_commithash(fp_repo: str, verbose=sys.stderr):
    """Obtain current commit hash of a Git repository.

    Parameters
    ----------
    fp_repo : str
        Filepath to the repository.
    verbose :
        ???

    Returns
    -------
    str : the Git repo commit hash.
    """
    cmd = 'git show --format="%H" | head -n 1'
    p_version = subprocess.run(cmd, shell=True, text=True,
                               stdout=subprocess.PIPE, cwd=fp_repo)
    version = p_version.stdout.strip()
    log('obtain repo (%s) commit hash via "%s" = %s\n' % (
        fp_repo, cmd, version))

    return version


def obtain_cafe_settings(verbose=sys.stderr):
    settings = dict()

    # the Cafe shall let users interact with a collection of Bellman's GAP
    # programs like Needleman-Wunsch or ElMamun. The FP_GAPUSERSOURCES variable
    # must point to the path containing these sources.
    fp_gapc_programs = "../ADP_collection/"

    # user submission leads to compilation and execution of new algera products
    # if the user re-submits the same algebra product (also called instance) it
    # does not need to be re-computed, therefore we are using a cache. JUST
    # this instance with user inputs have to be run.
    fp_cache = "DOCKER/bcafe_cache/"

    # don't forget to leave a changelog message
    settings['cafe_version'] = "v2.0"

    # obtain gapc version number to prefix cache prefix. Thus, updated gapc
    # compiler will automatically lead to new cache
    settings['versions'] = dict()
    settings['versions']['gapc'] = get_gapc_version(verbose)
    settings['versions']['ADP_collection'] = get_repo_commithash(
        fp_gapc_programs, verbose)
    settings['versions']['cafe'] = get_repo_commithash("./", verbose)

    settings['paths'] = dict()
    settings['paths']['prefix_cache'] = os.path.join(
        fp_cache, 'gapc_v%s' % settings['versions']['gapc'])
    settings['paths']['gapc_programs'] = fp_gapc_programs

    # maximum number of allowed algebras
    settings['max_algebras'] = 5

    # limit tikZ image generation to:
    settings['limit_candidate_trees'] = 20

    # maximum output lines:
    settings['max_output_lines'] = 5000

    return settings


def get_codefiles_hash(fps_gapc_code: [str]):
    content = ""
    for fp_file in fps_gapc_code:
        with open(fp_file, 'r') as f:
            content += ''.join(f.readlines())
    return hashlib.md5(content.encode('utf-8')).hexdigest()
