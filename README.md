# Intelligent traffic scene application
### Requirements

- Windows or Linux
- CUDA == 10.1.243
- cuDNN >= 7.4 for CUDA 10.1
- python3.7
- opencv-python==3.4.1.15
- opencv-contrib-python==3.4.1.15
CUDA：http://developer.download.nvidia.com/compute/cuda/10.1/Prod/local_installers/cuda_10.1.243_418.87.00_linux.run

### PretrainedWeights

- [Download weights for vanilla YOLOv3](https://pjreddie.com/media/files/yolov3.weights)
- [Download weights for tiny YOLOv3](https://pjreddie.com/media/files/yolov3-tiny.weights)
- [Download weights for backbones network](https://pjreddie.com/media/files/darknet53.conv.74)

Then place them in components/detector/yolov3/weights

- [Download weights for yolov4](https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.weights)

Then place it in components/detector/yolov4/weight,If the path not exist,please mkdir by yourself.


- [Download ckpt.t7 for DeepSort](https://drive.google.com/drive/folders/1xhG0kRH1EX5B9_Iz8gQJb7UNnn_riXi6)

Then place it in components/tracker/deep_sort_pytorch/deep_sort/deep/checkpoint/

### Docker setup
#### If docker setup (only for Linux and Docker==19.03)

**No need to install cuda and cudnn by yourself**

```bash
# At the first of all, you need install NVIDIA Container Runtime
curl -s -L https://nvidia.github.io/nvidia-container-runtime/gpgkey | \
  sudo apt-key add -
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-container-runtime/$distribution/nvidia-container-runtime.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-runtime.list
sudo apt-get update
# install NVIDIA Container Runtime
apt-get install nvidia-container-runtime
# build your develop image
docker build -t ${USER}/itsa-develop .
# start your container and expose a ssh port for develop IDE to use
docker run -it -p 8022:22 --gpus all  --network host ${USER}/itsa-develop
# then use IDE to connect localhost:8022 for develop
```
-----

### None Docker setup

#### If linux (need to install cuda and cudnn by yourselfy )

```bash
# install virtualenv
$ sudo pip3 install -U virtualenv
# create virtual env
$ virtualenv --system-site-packages -p python3 ./venv
# activate virtual env
$ source venv/bin/activate
# first you need install pytorch-cuda10.1
(venv) $ pip install torch==1.5.0+cu101 torchvision==0.6.0+cu101 -f https://download.pytorch.org/whl/torch_stable.html
# setup project
(venv) $ python setup.py develop
```

#### If windows ( need to install cuda and cudnn by yourself)

```cmd
# install virtualenv
pip3 install -U virtualenv
# create virtual en
virtualenv --system-site-packages -p python3 ./venv
# activate virtual env
venv/Scripts/activate
# first you need install pytorch-cuda10.1
(venv)pip install torch==1.5.0+cu101 torchvision==0.6.0+cu101 -f https://download.pytorch.org/whl/torch_stable.html
# setup project
(venv) python setup.py develop
```

#### Last step

```
# you need install opencv by youself
(venv) pip install opencv-python==3.4.1.15
(venv) pip install opencv-contrib-python==3.4.1.15
```

**However, opencv installed in this way does not support h264 encoded video output on Linux, so if you need to reduce the size of the video output on Linux, please follow the instructions of opencv compilation**

----

### How to start



----------



### opencv compilation

- The following compilation procedure is only applicable to python3.7, please modify the first statement if you are compiling in another version of python

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

### References

- https://github.com/eriklindernoren/PyTorch-YOLOv3
- https://github.com/Tianxiaomo/pytorch-YOLOv4
- https://github.com/ZQPei/deep_sort_pytorch
- https://github.com/zeusees/HyperLPR
``
