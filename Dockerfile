FROM sdglbl/itswork

# Install ITrafficSceneApplication
COPY . /ITrafficSceneApplication
WORKDIR /ITrafficSceneApplication
RUN echo "[easy_install]" >> ~/.pydistutils.cfg && echo "index_url = http://mirrors.aliyun.com/pypi/simple/ " >> ~/.pydistutils.cfg \
    &&  python3 setup.py develop