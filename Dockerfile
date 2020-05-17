FROM sdglbl/itswork

# Install ITrafficSceneApplication
COPY . /ITrafficSceneApplication
WORKDIR /ITrafficSceneApplication
RUN pip3 install mmcv -i https://pypi.tuna.tsinghua.edu.cn/simple some-package \
    && echo "[easy_install]" >> ~/.pydistutils.cfg \
    && echo "index_url = http://mirrors.aliyun.com/pypi/simple/ " >> ~/.pydistutils.cfg \
    && python3 setup.py develop \
    && pip3 uninstall -y opencv-python