FROM sdglbl/itsa-runtime

# Install ITrafficSceneApplication
ENV LANG C.UTF-8
COPY . /ITrafficSceneApplication
WORKDIR /ITrafficSceneApplication
RUN echo "[easy_install]" >> ~/.pydistutils.cfg \
    && echo "index_url = https://mirrors.aliyun.com/pypi/simple" >> ~/.pydistutils.cfg \
    && python3 setup.py develop \
    && pip3 uninstall -y opencv-python \
    && /usr/local/nginx/sbin/nginx