# 智慧交通场景应用

 * [智慧交通场景应用](#智慧交通场景应用)
    * [简介](#简介)
       * [支持功能](#支持功能)
    * [主要特点](#主要特点)
    * [部署](#部署)
       * [要求](#要求)
       * [预训练权重](#预训练权重)
       * [Windows部署](#windows部署)
             * [1.自行安装CUDA和CUDNN](#1自行安装cuda和cudnn)
             * [2.在项目根目录执行如下安装命令](#2在项目根目录执行如下安装命令)
             * [3.安装指定版本的opencv](#3安装指定版本的opencv)
             * [4.安装支持RTMP的Nginx](#4安装支持rtmp的nginx)
       * [Linux部署](#linux部署)
          * [基于Docker部署](#基于docker部署)
          * [自行编译环境部署](#自行编译环境部署)
             * [1.自行安装CUDA和CUDNN](#1自行安装cuda和cudnn-1)
             * [2.在项目根目录执行如下安装命令](#2在项目根目录执行如下安装命令-1)
             * [3.安装指定版本的opencv](#3安装指定版本的opencv-1)
             * [4.编译支持RTMP的Nginx](#4编译支持rtmp的nginx)
    * [使用](#使用)
       * [开启后端服务器](#开启后端服务器)
    * [附录](#附录)
       * [Opencv编译说明](#opencv编译说明)
## 简介

​		基于计算机视觉技术实现的，支持多种交通场景下的自动车道环境建模以及车流量，违章停车，违章占用车道监测。

### 支持功能

- [x] 过往车辆的流量统计 
- [ ] 车速检测 
- [ ] 路口交通的饱和度以及拥堵情况
- [ ] 闯红灯的机动车检测 
- [ ] 不礼让行人检测  优先级C 图像列表刷新
- [x] 机动车违章停车监测 
- [x] 违法占用车道检测 
- [x] 车牌识别 

## 主要特点

- 模块化设计，支持自定义组件，支持自定义构建视频处理Task
- 并行设计，Task中的各个模块采取多进程并行设计
- 简易部署，支持Docker部署进行开发或使用

## 部署

### 要求

- Windows or Linux
- CUDA == 10.1.243
- cuDNN >= 7.4 for CUDA 10.1
- python >= 3.6
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

### Windows部署

Note: Windows无法使用Docker部署

##### 1.自行安装CUDA和CUDNN

##### 2.在项目根目录执行如下安装命令

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

##### 3.安装指定版本的opencv

```bash
# 需要安装指定版本的opencv-python
(venv) pip install opencv-python==3.4.1.15
(venv) pip install opencv-contrib-python==3.4.1.15
```

##### 4.安装支持RTMP的Nginx

[Nginx安装配置和FFmpeg安装配置](https://blog.csdn.net/qq_41210304/article/details/106054737)

### Linux部署

####  基于Docker部署

Note: 基于docker部署无需自行安装CUDA和CUDNN，但需要Docker>=19.03且Linux系统安装有英伟达驱动

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
docker build -t ${USER}/itsa-develop .
# 将容器放置在宿主机器网段落使得宿主机可以通过ssh进行连接（第一次初始化需要自行设定密码和安装sshserver以及开放ssh连接）
# start your container and expose a ssh port for develop IDE to use
docker run -it --gpus all --network host  ${USER}/itsa-develop
# 然后就可以使用IDE连接进行开发了
```

#### 自行编译环境部署

##### 1.自行安装CUDA和CUDNN

##### 2.在项目根目录执行如下安装命令

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

##### 3.安装指定版本的opencv

```bash
# 需要安装指定版本的opencv-python
(venv) pip install opencv-python==3.4.1.15
(venv) pip install opencv-contrib-python==3.4.1.15
```

**Note: 以这种方式安装的opencv在Linux上不支持h264编码的视频输出，所以如果需要在Linux上减小视频输出的大小，请按照附录的opencv编译的说明进行操作**

##### 4.编译支持RTMP的Nginx

```bash
# 安装必要的编译dev
sudo apt-get install build-essential
sudo apt-get install libtool
sudo apt-get install libpcre3 libpcre3-dev zlib1g-dev openssl libssl-dev
# 下载nginx和rtmp推流模块
wget http://nginx.org/download/nginx-1.15.5.tar.gz
tar -zxvf nginx-1.13.10.tar.gz
#下载RTMP
git clone https://github.com/arut/nginx-rtmp-module.git
cd nginx-1.15.5/
# 编译
./configure --prefix=/usr/local/nginx --add-module=../nginx-rtmp-module --with-http_ssl_module
make -j<cpu core number>
make install
# 编辑/usr/local/nginx/conf/nginx.conf,在文件末尾添加如下内容
rtmp {
    server {
        listen 1935;
        chunk_size 4000;
        application live {
             live on;

             # record first 1K of stream
             record all;
             record_path /tmp/av;
             record_max_size 1K;
 
             # append current timestamp to each flv
             record_unique on;
 
             # publish only from localhost
             allow publish 127.0.0.1;
             deny publish all;
 
             #allow play all;
        }
    }
}
# 对/usr/local/nginx/conf/nginx.conf中的http按照如下进行修改
http {
    include       mime.types;
    default_type  application/octet-stream;
 
    sendfile        off;
 
    server_names_hash_bucket_size 128;
 
    client_body_timeout   10;
    client_header_timeout 10;
    keepalive_timeout     30;
    send_timeout          10;
    keepalive_requests    10;
 
    server {
        listen       80;
        server_name  localhost;
 
 
        location /stat {
            rtmp_stat all;
            rtmp_stat_stylesheet stat.xsl;
        }
        location /stat.xsl {
            root nginx-rtmp-module/;
        }
        location /control {
            rtmp_control all;
        }
# For Naxsi remove the single # line for learn mode, or the ## lines for full WAF mode
        location / {
            root   html;
            index  index.html index.htm;
        }
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   html;
        }
    }
}
# 运行如下命令检查是否配置成功
ffmpeg  -i [video file] -f flv rtmp://localhost:1935/live
```



## 使用

### 开启后端服务器

```python
# 运行如下命令即可开启网页后端服务器
/usr/local/nginx/sbin/nginx
PYTHONUNBUFFERED=1
DJANGO_SETTINGS_MODULE=ITrafficSceneApplication.settings
python3 manage.py runserver 8000
```

## 附录

### Opencv编译说明

**Note: 下面的编译过程只适用于python3.7，如果你在编译另一个版本的python，请修改第一条语句**

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
$ cmake -D CMAKE_BUILD_TYPE=Release -D WITH_FFMPEG=ON WITH_GTK=ON -D CMAKE_INSTALL_PREFIX=/usr/local PYTHON3_EXECUTABLE = /usr/bin/python3 PYTHON_INCLUDE_DIR = /usr/include/${PYTHON_VERSION} PYTHON_INCLUDE_DIR2 = /usr/include/x86_64-linux-gnu/${PYTHON_VERSION}m PYTHON_LIBRARY = /usr/lib/x86_64-linux-gnu/lib${PYTHON_VERSION}m.so PYTHON3_NUMPY_INCLUDE_DIRS = /usr/lib/python3/dist-packages/numpy/core/include/ -D OPENCV_ENABLE_NONFREE=ON -DOPENCV_EXTRA_MODULES_PATH=/home/${USER}/opencv_contrib/modules/ ..
$ make -j<cpu core number>
$ sudo make install
```

