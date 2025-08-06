[![Tests_pass](https://github.com/jlab/bellmanscafe/actions/workflows/codestyle.yml/badge.svg?branch=main)](https://github.com/jlab/bellmanscafe/actions/workflows/codestyle.yml)

[![Coverage Status](https://coveralls.io/repos/github/jlab/bellmanscafe/badge.svg?branch=main)](https://coveralls.io/github/jlab/bellmanscafe?branch=main)

# Bellman's Cafe

Interactive web-pages to explore Algebraic Dynamic Programming with live examples. Online version at [bellmanscafe.jlab.bio](http://bellmanscafe.jlab.bio)

# Install

1. I suggest you follow the instructions of the Dockerfile to see what dependencies need to be installed. In summary (but this list might be incomplete), you need
  - gapc (to compile ADP)
  - time (for benchmarking)
  - graphviz, texlive-latex-extra ghostscript (for grammar- and candidate tree drawings)
  - gunicorn flask markdown (for the server)
2. Once all dependencies have been installed, get some ADP example code, e.g. clone https://github.com/jlab/ADP_collection.git
3. Adapt the configuration file. Start from `instance/example_secret_config.py` and create a copy `instance/config.py` and change variables to your needs, especially
  - `bind`: try `'0.0.0.0:8000'`
  - `workers`: try `1` (1 is nice for debugging as you avoid concurrency, otherwise use higher numbers)
  - `accesslog` & `errorlog`: adapt the `DIR_LOGS` infix to an actually existing path
     - `FP_CACHE`: also replace `DIR_CACHE` with an actual path
  - `FP_GAPC_PROGRAMS`: should point to the ADP example code
4. start the server via `gunicorn -c instance/config.py Bellmansgap:app`
