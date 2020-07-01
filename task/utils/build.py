from queue import Empty, Full

import torch
from torch.multiprocessing import Process, Queue
import  os
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
def __head_process(head_cfg, sendqs, timeout, run_semaphore, pause_event):
    head = __build_head_component(head_cfg)
    logger = get_logger()
    logger.info('create ' + str(head_cfg['type']) + ' and which len is {}'.format(len(head)))
    try:
        for kwargs in head:
            if not run_semaphore.value:
                logger.info('通过信号量停止了head')
                break
            pause_event.wait()
            for sendq in sendqs:
                sendq.put(kwargs, timeout=timeout)
                # print('head sendq len is {}'.format(sendq.qsize()))
    except KeyboardInterrupt:
        logger.info('user stop the head process')
    except Full:
        logger.info('通向探测器的队列已满')
    # except Exception as e:
    #     logger.exception(e)
    finally:
        logger.info('release the head source')
        del logger
        for sendq in sendqs:
            sendq.cancel_join_thread()
            sendq.close()
    return


# 定义detector 进程的运行函数
def __detector_process(detector_cfg, recivq: Queue, sendqs, timeout, run_semaphore, pause_event):
    detector = __build_detector_component(detector_cfg)
    logger = get_logger()
    logger.info('create ' + str(detector_cfg['type']))
    try:
        while True:
            if not run_semaphore.value:
                logger.info('通过信号量停止了detector')
                break
            pause_event.wait()
            kwargs = recivq.get(timeout=timeout)
            kwargs = detector(**kwargs)
            # 因为后续可能是backbones也可能是tracker所以使用list来发送
            for sendq in sendqs:
                sendq.put(kwargs, timeout=timeout)
    except KeyboardInterrupt:
        logger.info('user stop the detector process')
    except Empty:
        logger.info('head不再发送数据detector自动释放')
    except Full:
        logger.exception('通向某一条主干或者跟踪器的队列已满')
    # except Exception as e:
    #     logger.exception(e)
    finally:
        logger.info('release the detector source')
        del detector  # 清除探测器对象
        del logger
        torch.cuda.empty_cache()  # 清空GPU缓存，防止出现进程STOP占用显存
        recivq.cancel_join_thread()
        for sendq in sendqs:
            sendq.cancel_join_thread()
            sendq.close()
        recivq.close()
    return


def __tracker_process(tracker_cfg, recivq: Queue, sendqs, timeout, run_semaphore, pause_event):
    tracker = __build_tracker_component(tracker_cfg)
    logger = get_logger()
    logger.info('create ' + str(tracker_cfg['type']))
    try:
        while True:
            if not run_semaphore.value:
                logger.info('通过信号量停止了tracker')
                break
            pause_event.wait()
            kwargs = recivq.get(timeout=timeout)
            imgs, imgs_info = kwargs['imgs'], kwargs['imgs_info']
            for index, (img, img_info) in enumerate(zip(imgs, imgs_info)):
                img_info = tracker(img, img_info)
                imgs_info[index] = img_info
            for sendq in sendqs:
                # print('tracker sendq len is {}'.format(sendq.qsize()))
                sendq.put({'imgs': imgs, 'imgs_info': imgs_info}, timeout=timeout)
    except KeyboardInterrupt:
        logger.info('user stop the detector process')
    except Empty:
        logger.info('detector不再发送数据tracker自动释放')
    except Full:
        logger.exception('通向某一条主干的队列已满')
    # except Exception as e:
    #     logger.exception(e)
    finally:
        logger.info('release the tracker source')
        del tracker  # 清除探测器对象
        del logger
        torch.cuda.empty_cache()  # 清空GPU缓存，防止出现进程STOP占用显存
        recivq.cancel_join_thread()
        for sendq in sendqs:
            sendq.cancel_join_thread()
            sendq.close()
        recivq.close()
    return


def __backbone_process(backbone_cfg: list, recivq: Queue, sendq: Queue, timeout, run_semaphore, pause_event):
    # 实例化一个backbone里面所有的组件
    backbone_components = [__build_backbone_component(bbcfg) for bbcfg in backbone_cfg]
    logger = get_logger()
    logger.info('create backbone')
    try:
        while True:
            if not run_semaphore.value:
                logger.info('通过信号量停止了backbone')
                break
            pause_event.wait()
            kwargs = recivq.get(timeout=timeout)
            # 首先由该管道内的第一个组件处理数据
            kwargs = backbone_components[0](**kwargs)
            if len(backbone_components) > 1:
                # 如果该管道有多个component的话依次将数据交给之后的component处理
                for backbone_component in backbone_components[1:]:
                    kwargs = backbone_component(**kwargs)
            # print('backbone sendq len is {}'.format(sendq.qsize()))
            for img_info in kwargs['imgs_info']:
                sendq.put(img_info, timeout=timeout)
    except KeyboardInterrupt:
        logger.info('user stop a backbone_process process')
    except Empty:
        logger.info('backbone normal stoped')
    except Full as e:
        logger.exception(e)
        logger.warning('通向主进程的队列已满，请检查主进程是否正常取出数据')
    except Exception as e:
        logger.exception(e)
        logger.info('发生不可忽视的错误，因此强制停止整个后台程序运行，请检查log输出定位错误')
        # import signal
        # os.killpg(os.getpgid(os.getpid()), signal.SIGKILL)
    finally:
        logger.info('release backbone source')
        del logger
        recivq.cancel_join_thread()
        sendq.cancel_join_thread()
        recivq.close()
        sendq.close()
    return


def build_process(cfg_type, cfg, recivqs, sendqs, timeout,run_semaphore,pause_event):
    if cfg_type == 'head':
        return [Process(target=__head_process, args=(cfg, sendqs, timeout, run_semaphore, pause_event,))]
    elif cfg_type == 'detector':
        return [Process(target=__detector_process, args=(cfg, recivqs[0], sendqs, timeout, run_semaphore, pause_event,))]
    elif cfg_type == 'tracker':
        return [Process(target=__tracker_process, args=(cfg, recivqs[0], sendqs, timeout, run_semaphore, pause_event,))]
    elif cfg_type == 'backbones':
        return [Process(target=__backbone_process, args=(backbone_cfg, recivq, sendq, timeout, run_semaphore, pause_event,))
                for backbone_cfg, recivq, sendq in zip(cfg, recivqs, sendqs)]
    else:
        raise AttributeError('暂时不支持类型为{}的组件'.format(cfg_type))
