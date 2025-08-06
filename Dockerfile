FROM python:latest

ENV DIR_PROBLEMS="/src/ADPproblems"
ENV DIR_LOGS="/LOGS"
ENV DIR_CACHE="/CACHE"
ENV PORT="8000"
ENV NUMWORKERS="8"

RUN apt-get -y update

# dependencies needed for gapc: flex bison make libboost-all-dev libgsl-dev build-essential
# time: to measure run-times of compilation and execution steps
# graphviz: draw grammars
# texlive-latex-extra & ghostscript: to draw candidate trees, i.e. convert tikz into jpgs
# cron: to hourly check for updates in ADP_collection & fold-grammars repo
RUN apt-get -y install \
        flex bison make libboost-all-dev libgsl-dev build-essential \
        time \
        graphviz \
        texlive-latex-extra ghostscript \
        cron

RUN pip install gunicorn flask markdown

# download, compile and install gapc from sources of master branch
RUN mkdir -p src && git clone -b master https://github.com/jlab/gapc.git /src/gapc && cd /src/gapc && ./configure && make -j && make install

# clone ADP example problems
RUN git clone -b master https://github.com/jlab/ADP_collection.git ${DIR_PROBLEMS}
# a hacky solution to also add problems from the fold-grammars repository into the cafe
RUN git clone -b master https://github.com/jlab/fold-grammars.git `dirname ${DIR_PROBLEMS}`/fold-grammars
RUN cd ${DIR_PROBLEMS} && for f in `echo "Algebras Extensions Grammars Signatures macrostate.gap microstate.gap nodangle.gap overdangle.gap pKiss.gap rnahybrid.gap"`; do ln -s ../fold-grammars/$f $f; done

# clone cafe code
RUN git clone -b main https://github.com/jlab/bellmanscafe.git /src/bellmanscafe
WORKDIR /src/bellmanscafe

# create directory for log and cache files. 
# Mount external dir if you want to make logs and/or cache persistent.
RUN mkdir -p ${DIR_LOGS} ${DIR_CACHE}

# create flask configuration file from template
# COPY instance/example_secret_config.py instance/example_secret_config.py
# COPY Bellmansgap.py Bellmansgap.py
RUN cp instance/example_secret_config.py instance/secret_config.py
RUN bash -c 'sed -i "s|DIR_LOGS|${DIR_LOGS}|g" instance/secret_config.py'
RUN bash -c 'sed -i "s|DIR_CACHE|${DIR_CACHE}|g" instance/secret_config.py'
RUN bash -c 'sed -i "s|DIR_PROBLEMS|${DIR_PROBLEMS}|g" instance/secret_config.py'
RUN bash -c 'sed -i "s|PORT|${PORT}|g" instance/secret_config.py'
RUN bash -c 'sed -i "s|\"NUMWORKERS\"|${NUMWORKERS}|g" instance/secret_config.py'

EXPOSE ${PORT}/tcp

# allow ImageMagic to create PDFs for candidate trees
RUN sed -i 's#<policy domain="coder" rights="none" pattern="PDF" />#<policy domain="coder" rights="read|write" pattern="PDF" />#' /etc/ImageMagick-6/policy.xml || true

# create a secret for the server
RUN tr -dc A-Za-z0-9 </dev/urandom | head -c 30> HELP; bash -c 'sed -i "s|only set in server copy of this file|`cat HELP`|g" instance/secret_config.py'; rm -f HELP

## setup a cron job, that checks every hour if changes in the ADP_collection or fold-grammars repositories have been made and pull updates if this is the case
# create script for cron job which should regularly pull updates in both ADP problem repositories
ARG SCRIPT_UPDATE="/update_adp_repos.sh"
RUN echo "#!/bin/bash" > ${SCRIPT_UPDATE} &&\
    echo 'echo "Checking for source code updates at $(date)"' >> ${SCRIPT_UPDATE} && \
    echo "cd $DIR_PROBLEMS" >> ${SCRIPT_UPDATE} && \
    echo "git pull" >> ${SCRIPT_UPDATE} && \
    echo "cd `dirname ${DIR_PROBLEMS}`/fold-grammars" >> ${SCRIPT_UPDATE} && \
    echo "git pull" >> ${SCRIPT_UPDATE} && \
    chmod +x ${SCRIPT_UPDATE}
# register the above script as cronjob
ARG SCRIPT_CRON="/cron_job.sh"
RUN echo "0 * * * * ${SCRIPT_UPDATE} >> ${DIR_LOGS}/cron.log 2>&1" > ${SCRIPT_CRON}
RUN crontab ${SCRIPT_CRON}

# create a script that starts cron in background and the flask server in foregroud
ARG SCRIPT_STARTUP="/startup.sh"
RUN echo "#!/bin/bash" > ${SCRIPT_STARTUP} && \
    echo "cron" >> ${SCRIPT_STARTUP} && \
    echo "exec gunicorn -c instance/secret_config.py Bellmansgap:app" >> ${SCRIPT_STARTUP} && \
    chmod +x ${SCRIPT_STARTUP}

CMD ["/startup.sh"]