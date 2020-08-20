import math
import cv2
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal
from sklearn.cluster import KMeans
from scipy.stats import norm


# 通过bbox得到中心点
def getCentre(bbox: list):
    cx = int((bbox[0]+bbox[2])/2)
    cy = int((bbox[1]+bbox[3])/2)
    return [cx, cy]


# 计算向量模长
def vLen(v:list):
    s = 0
    for i in v:
        s += i*i
    return pow(s, 0.5)


# 投影操作，返回v投影模长
def projection(v, d):
    return v[0] * math.cos(d) + v[1] * math.sin(d)


# 得到向量方向
def getDirection(v:list):
    if len(v) == 2:
        if v[0] != 0:
            return math.atan(v[1]/v[0])
        elif v[1] != 0:
            return math.pi/2 * v[1]/abs(v[1])
        else:
            return 0


# 得到平均bbox长
def getAvgBbox(bbox):
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    return (w+h)/2


# 得到速度方向的聚类中心
def getAxis(speedDirs, coreNam=2):
    k = KMeans(n_clusters=coreNam)
    k.fit(speedDirs)
    axis = []
    for c in k.cluster_centers_:
        axis.append(c[0])
    return axis

# 将路径缕直，存储在'zipDots'中
def straighten(path, stepTh):
    dots = path['dots']
    indexs = path['indexs']
    tDots = []
    tIndexs = []
    dot0 = dots[0]
    index0 = indexs[0]
    tDots.append(dot0)
    tIndexs.append(index0)
    for i in range(1, len(dots)):
        dot1 = dots[i]
        index1 = indexs[i]
        tStep = vLen([dot1[0]-dot0[0], dot1[1]-dot0[1]])
        if tStep > stepTh:
            tDots.append(dot1)
            tIndexs.append(index1)
            dot0 = dot1
            index0 = index1
    path['zipDots'] = tDots
    path['indexs'] = tIndexs
    return path

# 将路径转化为特征路径，存储在'fun_dots'中
def pathFitting(path, transformMat):
    dots = path['zipDots']
    dots = np.array(dots)

    # 将路径表示为基坐标下的形式
    baseDots = np.dot(dots, transformMat)

    # 对数据进行函数去噪
    x = np.array(baseDots[:, 0])
    y = np.array(baseDots[:, 1])
    t = np.arange(len(x))
    txArg = np.polyfit(t, x, 4)
    tyArg = np.polyfit(t, y, 4)
    txFun = np.poly1d(txArg)
    tyFun = np.poly1d(tyArg)
    tx = txFun(t)
    ty = tyFun(t)
    # if tx[-1] - tx[1] > 200:
        # plt.plot(tx)
        # plt.plot(ty)


    # 将去噪后的数据保存为fun_dots
    tx = tx[:, np.newaxis]
    ty = ty[:, np.newaxis]
    fDots = np.concatenate((tx, ty), axis=1)
    path['fun_dots'] = fDots

    # bg = cv2.imread('lot_15.png')
    # bg = cv2.resize(bg, (1920, 1080))
    # drawDot(fDots,bg,(255,0,0))
    return path

# 高斯聚类函数，得到聚类后的波峰状况
def gaussianCumulative(valus, var):
    max = np.max(valus)
    min = np.min(valus)
    tMax = max + (max-min)/2
    tMin = min - (max-min)/2
    # valus = (valus - tMin)/(tMax - tMin)
    # var = np.var(valus)
    tAxis = np.arange(tMin, tMax)
    y = np.zeros(tAxis.shape, dtype=np.float)
    for v in valus:
        ty = norm.pdf(tAxis, v, var)
        y = y+ty
    max_peak = signal.find_peaks(y, 0)
    return len(max_peak[0]), max_peak[0]

# 已弃用
def differenceDirection(dots,benchmarkDir):
    diffDirs = []
    for i in range(1, len(dots)):
        dot1 = dots[i - 1]
        dot2 = dots[i]
        tDir = getDirection([dot2[0]-dot1[0], dot2[1]-dot1[1]])
        diffDir = tDir - benchmarkDir
        diffDirs.append(diffDir)
    plt.plot(diffDirs)
    plt.show()
    return diffDirs

# 得到坐标转换矩阵
def getTransformMat(axis):
    m = axis[0]
    tanM = math.tan(m)
    mLen = vLen([1, tanM])
    s = axis[1]
    tanS = math.tan(s)
    sLen = vLen([1, tanS])
    transformMat = np.array(
        [[1/mLen, tanM/mLen],
         [1/sLen, tanS/sLen]]
    )
    invTransformMat = np.linalg.inv(transformMat)
    return transformMat, invTransformMat

# 得到关于路径的停止图和速度图
def getMap(paths, mapSize, stopTh):
    stopMap = np.zeros(mapSize, dtype=float)
    speedMap = np.zeros(mapSize, dtype=float)
    for path in paths:
        speeds = path['speeds']
        bboxs = path['bboxs']
        for i in range(1, len(speeds)):
            speedMap = bboxAdd(bboxs[i], speeds[i][2], speedMap, t=0.7)
            if speeds[i][2] < stopTh:
                stopMap = bboxAdd(bboxs[i], 1, stopMap, t=0.2)
    return stopMap, speedMap

# 内部使用函数，被getMap调用
def bboxAdd(bbox, speed, map, t=0.7):
        c = getCentre(bbox)
        h = bbox[3] - bbox[1]
        w = bbox[2] - bbox[0]
        h = h * t / 2
        w = w * t / 2

        map[int(c[1] - h):int(c[1] + h), int(c[0] - h):int(c[0] + h)] += speed
        return map

# 在命令行下不可使用
def showMap(map, bg, th):
    th = np.max(map) * th
    tMap = np.zeros([map.shape[0], map.shape[1], 3], dtype=np.uint8)
    tMap[map >= th, :] = 255
    showImg = cv2.addWeighted(tMap, 0.5, bg, 0.5, 1)
    cv2.imshow('map', showImg)
    cv2.waitKey()

# 在命令行下不可使用
def drawPaths(paths, backgrand, color):
    for path in paths:
        dots = path['dots']
        drawDot(dots, backgrand, color)

# 在命令行下不可使用
def drawDot(dots,backgrand,color):
    for i in range(1, len(dots)):
        dot1 = dots[i - 1]
        dot2 = dots[i]
        cv2.line(backgrand, (int(dot1[0]), int(dot1[1])), (int(dot2[0]), int(dot2[1])), color, 4)
    # cv2.imshow('bg', backgrand)
    # cv2.waitKey()

# 已弃用
def getLanNum(speedMap, core):
    index = np.argmax(speedMap)
    i0 = index // speedMap.shape[1]
    profile = speedMap[i0, :]
    profile = signal.medfilt(profile, int(core//2)*2 + 1)
    max_peak = signal.find_peaks(profile, core)
    print(max_peak)
    return len(max_peak[0])

# 已弃用
def pathCluster(paths, direction, coreNum):
    startDots = []
    for path in paths:
        tStartDot = projection(path['dots'][0], direction)
        startDots.append([tStartDot])
    k = KMeans(coreNum)
    k.fit(startDots)
    tPaths = {}
    for i in range(coreNum):
        tPaths[i] = []
    for i in range(len(paths)):
        tPaths[k.labels_[i]].append(paths[i])
    return tPaths


# 得到山峰线，已弃用
def peakLine(speedMap, starRow, endRow, core, lanNum):
    peakLines = {}
    for i in range(lanNum):
        peakLines[i] = []
    for i in range(starRow, endRow):
        profile = speedMap[i, :]
        profile = signal.medfilt(profile, int(core // 2) * 2 + 1)
        max_peak = signal.find_peaks(profile, core)
        print(max_peak)
        print(i)
        plt.plot(profile)
        plt.show()
        if len(max_peak[0]) == lanNum:
            for j in range(lanNum):
                peakLines[j].append([max_peak[0][j],i])
    print(len(peakLines[0]))
    return peakLines

# 得到一个以th为阈值的蒙版
def getMapMask(map, th):
    th = 0.5
    th = np.max(map) * th
    return map >= th

