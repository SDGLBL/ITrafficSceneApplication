import math

# 通过bbox得到中心点
def get_centre(bbox: list):
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