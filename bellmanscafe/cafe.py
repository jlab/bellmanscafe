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


def obtain_cafe_settings(config, verbose=sys.stderr):
    gapc_version = get_gapc_version(verbose)

    settings = {
        'paths': {
            'gapc_programs': config['FP_GAPC_PROGRAMS'],
            'prefix_cache': os.path.join(config['FP_CACHE'],
                                         'gapc_v%s' % gapc_version),
        },
        'versions': {
            'gapc': gapc_version,
            'ADP_collection': get_repo_commithash(config['FP_GAPC_PROGRAMS'],
                                                  verbose),
            'cafe': get_repo_commithash("./", verbose),
            'flask': config['CAFE_VERSION'],
        },
        'max_algebras': config['MAX_ALGEBRAS'],
        'limit_candidate_trees': config['LIMIT_CANDIDATE_TREES'],
        'max_output_lines': config['MAX_OUTPUT_LINES'],
        'max_cpu_time': config['MAX_CPU_TIME'],
    }

    return settings


def get_codefiles_hash(fps_gapc_code: [str]):
    content = ""
    for fp_file in fps_gapc_code:
        with open(fp_file, 'r') as f:
            content += ''.join(f.readlines())
    return hashlib.md5(content.encode('utf-8')).hexdigest()
