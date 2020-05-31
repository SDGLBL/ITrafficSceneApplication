FROM sdglbl/itsa-runtime

# Install ITrafficSceneApplication
ENV LANG C.UTF-8
COPY . /ITrafficSceneApplication
WORKDIR /ITrafficSceneApplication
RUN apt-get update && apt-get clean && apt autoremove -y redis-server \
    && echo "[easy_install]" >> ~/.pydistutils.cfg \
    && echo "index_url = https://pypi.tuna.tsinghua.edu.cn/simple" >> ~/.pydistutils.cfg \
    && python3 setup.py develop \
    && pip3 uninstall -y opencv-python