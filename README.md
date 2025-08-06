[![Tests_pass](https://github.com/jlab/bellmanscafe/actions/workflows/codestyle.yml/badge.svg?branch=main)](https://github.com/jlab/bellmanscafe/actions/workflows/codestyle.yml) [![Coverage Status](https://coveralls.io/repos/github/jlab/bellmanscafe/badge.svg?branch=main)](https://coveralls.io/github/jlab/bellmanscafe?branch=main)

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

# Host Server

1. Hosting bellmanscafe should be easy as you "just" need to pull/build and than run the docker container.
    a) **build**: sudo docker buildx build . -f Dockerfile -t bellmanscafe
    b) **pull**: 
2. Once the image is available (through building or pulling), you can run it as an container via `sudo docker run -p 8000:8000 -it bellmanscafe`
    - note that you have to forward port 8000 from the container to your host. This port can be re-configured in the Dockerfile
    - to make debugging more easy, I suggest you mount two host directories to "/LOGS" and "/CACHE" directories, such that they become persistent even if you restart your container, e.g. by adding `-v /home/sjanssen/bellmanscafe/CACHE/:/CACHE/` and `-v /home/sjanssen/bellmanscafe/LOGS/:/LOGS/` to your `docker build` command. (You need to modify `/home/sjanssen/bellmanscafe` of course!)