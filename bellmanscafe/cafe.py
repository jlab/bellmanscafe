import sys
import subprocess
import os
import logging


def log(msg, level='debug', verbose=sys.stderr):
    if isinstance(verbose, logging.Logger):
        if level=='info':
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
    log('obtain gapc version number via "%s" = %s' % (cmd, version))

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
    log('obtain repo (%s) commit hash via "%s" = %s' % (fp_repo, cmd, version))

    return version


def obtain_cafe_settings(fp_cache, fp_gapc_programs, verbose=sys.stderr):
    settings = dict()

    # obtain gapc version number to prefix cache prefix. Thus, updated gapc
    # compiler will automatically lead to new cache
    settings['versions'] = dict()
    settings['versions']['gapc'] = get_gapc_version(verbose)
    settings['versions']['ADP_collection'] = get_repo_commithash(fp_gapc_programs, verbose)
    settings['versions']['cafe'] = get_repo_commithash("./", verbose)

    settings['paths'] = dict()
    settings['paths']['prefix_cache'] = os.path.join(fp_cache, 'gapc_v%s' % settings['versions']['gapc'])
    settings['paths']['gapc_programs'] = fp_gapc_programs

    return settings
