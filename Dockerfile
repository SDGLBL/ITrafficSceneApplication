FROM sdglbl/itswork:lastest

RUN apt-get update && apt-get install -y git\
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install ITrafficSceneApplication
COPY . /ITrafficSceneApplication
WORKDIR /ITrafficSceneApplication
RUN echo "[easy_install]" >> ~/.pydistutils.cfg && echo "index_url = https://pypi.tuna.tsinghua.edu.cn/simple" >> ~/.pydistutils.cfg \
 && pip3 setup.py develop