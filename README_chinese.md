# 智慧交通场景应用

### 依赖

- Windows or Linux
- CUDA == 10.1.243
- cuDNN >= 7.4 for CUDA 10.1
- python3.7
- opencv-python==3.4.1.15
- opencv-contrib-python==3.4.1.15

### 预训练权重

- [Download weights for vanilla YOLOv3](https://pjreddie.com/media/files/yolov3.weights)
- [Download weights for tiny YOLOv3](https://pjreddie.com/media/files/yolov3-tiny.weights)
- [Download weights for backbones network](https://pjreddie.com/media/files/darknet53.conv.74)

然后将它们放置在 components/detector/yolov3/weights

- [Download weights for yolov4](https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.weights)

然后将它们放置在 components/detector/yolov4/weight,如果weight文件夹不存在请自行创建


- [Download ckpt.t7 for DeepSort](https://drive.google.com/drive/folders/1xhG0kRH1EX5B9_Iz8gQJb7UNnn_riXi6)

然后将它放置在 components/tracker/deep_sort_pytorch/deep_sort/deep/checkpoint/

### Docker部署

### 基于Docker部署 (只支持Linux和Docker版本为最新版本)

基于docker部署不需要自行安装cuda和cudnn

```bash
# 首先需要安装 NVIDIA Container Runtime
curl -s -L https://nvidia.github.io/nvidia-container-runtime/gpgkey | \
  sudo apt-key add -
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-container-runtime/$distribution/nvidia-container-runtime.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-runtime.list
sudo apt-get update
# 安装 NVIDIA Container Runtime
apt-get install nvidia-container-runtime
# 构建开发用 image
cd docker && docker build -t ${USER}/itsa-develop ..
# 开启容器并将8022端口暴露给宿主机，使得宿主机可以通过ssh进行连接（第一次初始化需要自行设定密码和安装sshserver以及开放ssh连接）
# start your container and expose a ssh port for develop IDE to use
docker run -it -p 8022:22 --gpus all  ${USER}/itsa-develop
# 然后就可以使用IDE连接进行开发了
```

----

### 非Docker部署

#### Linux ( 需要自行安装cuda和cudnn )

```bash
# 安装 virtualenv
$ sudo pip3 install -U virtualenv
# 创建 virtual env
$ virtualenv --system-site-packages -p python3 ./venv
# 激活 virtual env
$ source venv/bin/activate
# 自行安装 pytorch-cuda10.1
(venv) $ pip install torch==1.5.0+cu101 torchvision==0.6.0+cu101 -f https://download.pytorch.org/whl/torch_stable.html
# setup project
(venv) $ python setup.py develop
```

#### Windows ( 需要自行安装cuda和cudnn )

```cmd
# 安装 virtualenv
pip3 install -U virtualenv
# 创建 virtual env
virtualenv --system-site-packages -p python3 ./venv
# 激活 virtual env
venv/Scripts/activate
# 自行安装 pytorch-cuda10.1
(venv)pip install torch==1.5.0+cu101 torchvision==0.6.0+cu101 -f https://download.pytorch.org/whl/torch_stable.html
# setup project
(venv) python setup.py develop
```

#### 最后一步

```
# 需要安装指定版本的opencv-python
(venv) pip install opencv-python==3.4.1.15
(venv) pip install opencv-contrib-python==3.4.1.15
```

**但是，以这种方式安装的opencv在Linux上不支持h264编码的视频输出，所以如果需要在Linux上减小视频输出的大小，请按照opencv编译的说明进行操作**

-----

### How to start

----------



### opencv编译说明

- 下面的编译过程只适用于python3.7，如果你在编译另一个版本的python，请修改第一个语句

```bash
$ export PYTHON_VERSION="python3.7"
$ wget https://launchpad.net/ubuntu/+archive/primary/+sourcefiles/ffmpeg/7:3.4.6-0ubuntu0.18.04.1/ffmpeg_3.4.6.orig.tar.xz
$ tar -xf ffmpeg_3.4.6.orig.tar.xz
$ cd ffmpeg-3.4.6
$ sudo apt-get install ${PYTHON_VERSION}
$ sudo apt-get install python3-dev
$ sudo apt-get install python3-numpy
$ sudo apt-get install yasm
$ ./configure --enable-shared --prefix=/usr
$ make
$ sudo make install
$ cd ..
$ sudo apt-get install build-essential git
$ sudo apt-get install cmake
$ sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev
$ sudo apt-get install libgstreamer-plugins-base1.0-dev libgstreamer1.0-dev libgtk2.0-dev
$ git clone https://github.com/opencv/opencv.git
$ git clone https://github.com/opencv/opencv_contrib
$ cd opencv_contrib
$ git checkout 3.4 && git pull origin 3.4
$ cd ..
$ cd opencv
$ git checkout 3.4 && git pull origin 3.4
$ mkdir build && cd build
$ cmake -D CMAKE_BUILD_TYPE=Release -D WITH_FFMPEG=ON WITH_GTK=ON -D CMAKE_INSTALL_PREFIX=/usr/local PYTHON3_EXECUTABLE = /usr/bin/python3 PYTHON_INCLUDE_DIR = /usr/include/python PYTHON_INCLUDE_DIR2 = /usr/include/x86_64-linux-gnu/${PYTHON_VERSION}m PYTHON_LIBRARY = /usr/lib/x86_64-linux-gnu/lib${PYTHON_VERSION}m.so PYTHON3_NUMPY_INCLUDE_DIRS = /usr/lib/python3/dist-packages/numpy/core/include/ -D OPENCV_ENABLE_NONFREE=ON -DOPENCV_EXTRA_MODULES_PATH=/home/${USER}/opencv_contrib/modules/ ..
$ make -j<cpu core number>
$ sudo make install
```

### 引用

- https://github.com/eriklindernoren/PyTorch-YOLOv3
- https://github.com/Tianxiaomo/pytorch-YOLOv4
- https://github.com/ZQPei/deep_sort_pytorch
- https://github.com/zeusees/HyperLPR
  ``