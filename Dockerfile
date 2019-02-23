FROM datajoint/jupyter:python3.6

ADD . /src/IBL-pipeline

RUN pip install -e /src/IBL-pipeline

RUN pip install globus_sdk

RUN pip install "git+https://github.com/int-brain-lab/ibllib.git@develop#egg=ibllib&subdirectory=python"
RUN pip install globus_sdk
RUN pip install "git+https://github.com/ixcat/djwip.git#egg=djwip"
