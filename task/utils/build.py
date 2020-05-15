from queue import Empty, Full

import torch
from torch.multiprocessing import Process, Queue

from components.backbones.registry import BACKBONE_COMPONENT
from components.detector.registry import DETECTOR
from components.head.registry import HEAD
from components.tracker.registry import TRACKER
from utils.logger import get_logger
from utils.registry import build_from_cfg


def __build_head_component(head_component_cfg):
    return build_from_cfg(head_component_cfg, HEAD)


def __build_detector_component(detector_component_cfg):
    return build_from_cfg(detector_component_cfg, DETECTOR)


def __build_tracker_component(tracker_component_cfg):
    return build_from_cfg(tracker_component_cfg, TRACKER)


def __build_backbone_component(backbone_component_cfg):
    return build_from_cfg(backbone_component_cfg, BACKBONE_COMPONENT)


# 定义head 进程的运行函数
def __head_process(head_cfg, sendqs, timeout):
    logger = get_logger()
    head = __build_head_component(head_cfg)
    logger.info('create ' + str(head_cfg) + ' and which len is {}'.format(len(head)))
    try:
        for kwargs in head:
            for sendq in sendqs:
                sendq.put(kwargs, timeout=timeout)
    except KeyboardInterrupt:
        logger.info('user stop the head process')
    except Full:
        logger.info('head管道长时间爆满，可能detector出现了问题')
    except Exception as e:
        logger.exception(e)
    finally:
        for sendq in sendqs:
            sendq.close()
        logger.info('release the head source')


# 定义detector 进程的运行函数
def __detector_process(detector_cfg, recivq: Queue, sendqs, timeout):
    logger = get_logger()
    detector = __build_detector_component(detector_cfg)
    logger.info('create ' + str(detector_cfg))
    try:
        while True:
            kwargs = recivq.get(timeout=timeout)
            kwargs = detector(**kwargs)
            # 因为后续可能是backbones也可能是tracker所以使用list来发送
            for sendq in sendqs:
                sendq.put(kwargs, timeout=timeout)
    except KeyboardInterrupt:
        logger.info('user stop the detector process')
    except Empty:
        logger.info('head不再发送数据detector自动释放')
    except Exception as e:
        logger.exception(e)
    finally:
        del detector  # 清除探测器对象
        torch.cuda.empty_cache()  # 清空GPU缓存，防止出现进程STOP占用显存
        for sendq in sendqs:
            sendq.close()
        logger.info('release the detector source')


def __tracker_process(tracker_cfg, recivq: Queue, sendqs, timeout):
    logger = get_logger()
    tracker = __build_tracker_component(tracker_cfg)
    logger.info('create ' + str(tracker_cfg))
    try:
        while True:
            kwargs = recivq.get(timeout=timeout)
            imgs, imgs_info = kwargs['imgs'], kwargs['imgs_info']
            for index, (img, img_info) in enumerate(zip(imgs, imgs_info)):
                img_info = tracker(img, img_info)
                imgs_info[index] = img_info
            for sendq in sendqs:
                sendq.put({'imgs': imgs, 'imgs_info': imgs_info}, timeout=timeout)
    except KeyboardInterrupt:
        logger.info('user stop the detector process')
    except Empty:
        logger.info('detector不再发送数据tracker自动释放')
    except Exception as e:
        logger.exception(e)
    finally:
        del tracker  # 清除探测器对象
        torch.cuda.empty_cache()  # 清空GPU缓存，防止出现进程STOP占用显存
        for sendq in sendqs:
            sendq.close()
        logger.info('release the tracker source')


def __backbone_process(backbone_cfg: list, recivq: Queue, timeout):
    logger = get_logger()
    # 实例化一个backbone里面所有的组件
    backbone_components = [__build_backbone_component(bbcfg) for bbcfg in backbone_cfg]
    logger.info('create backbone {0} '.format(backbone_cfg))
    try:
        while True:
            kwargs = recivq.get(timeout=timeout)
            # 首先由该管道内的第一个组件处理数据
            kwargs = backbone_components[0](**kwargs)
            if len(backbone_components) > 1:
                # 如果该管道有多个component的话依次将数据交给之后的component处理
                for backbone_component in backbone_components[1:]:
                    kwargs = backbone_component(**kwargs)
                # 处理到最后的数据直接清楚
            del kwargs
    except KeyboardInterrupt:
        logger.info('user stop a backbone_process process')
    except Empty:
        logger.info('backbone normal stoped')
    except Exception as e:
        logger.exception(e)
    return


def __build_process(cfg_type, cfg, recivqs, sendqs, timeout):
    if cfg_type == 'head':
        return [Process(target=__head_process, args=(cfg[0], sendqs, timeout,))]
    elif cfg_type == 'detector':
        return [Process(target=__detector_process, args=(cfg[0], recivqs[0], sendqs, timeout,))]
    elif cfg_type == 'tracker':
        return [Process(target=__tracker_process, args=(cfg[0], recivqs[0], sendqs, timeout,))]
    elif cfg_type == 'backbones':
        return [Process(target=__backbone_process, args=(backbone_cfg, recivq, timeout)) for backbone_cfg, recivq in
                zip(cfg, recivqs)]
    else:
        raise AttributeError('暂时不支持类型为{}的组件'.format(cfg_type))


def compile_task_cfg(cfg: dict, timeout=10, maxsize=30):
    detector_cfg = None
    if 'detector' in cfg.keys():
        detector_cfg = cfg['detector']
    tracker_cfg = None
    if 'tracker' in cfg.keys():
        tracker_cfg = cfg['tracker']
    if 'backbones' not in cfg.keys() or 'head' not in cfg.keys():
        raise AttributeError('task_cfg必须至少包含有head 和 backbone')
    head_cfg = cfg['head']
    backbones_cfg = cfg['backbones']
    if not isinstance(backbones_cfg, list):
        raise AttributeError('backbones_cfg必须为list')
    compile_list = [('head', head_cfg), ('detector', detector_cfg), ('tracker', tracker_cfg),
                    ('backbones', backbones_cfg)]
    # 过滤掉不存在的Task组件cfg
    compile_list = [task_component for task_component in compile_list if task_component[1] is not None]
    # 开始解析Task结构
    sendqs_list = []
    recivqs_list = []
    for i in range(len(compile_list)):
        task_component = compile_list[i][1]
        # 检查Task组件cfg
        if not isinstance(task_component, list) or len(task_component) == 0:
            raise AttributeError('TaskComponentCfg必须为list且非空')
        if i + 1 < len(compile_list):
            qnum = len(compile_list[i + 1][1])
            sendqs = [Queue(maxsize=maxsize) for _ in range(qnum)]
            sendqs_list.append(sendqs)
    sendqs_list.append(None)
    recivqs_list.append(None)
    for sendqs in sendqs_list:
        recivqs_list.append(sendqs)
    Task = []
    # 开始构建Task
    for tc, sendqs, recivq in zip(compile_list, sendqs_list, recivqs_list):
        # 每个组件都需要知道自己的获得数据的队列recivq  以及 发送数据到其他组件的sendqs 以及自生类型以及cfg
        # Task组件类型 head or detector or tracker or backbones
        tc_type = tc[0]
        tc_cfg = tc[1]
        Task.append(__build_process(tc_type, tc_cfg, recivq, sendqs, timeout))
    print(Task)
    return Task
