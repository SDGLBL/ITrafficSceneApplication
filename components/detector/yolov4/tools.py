from .tool.darknet2pytorch import Darknet


def get_yolov4(cfgs, weightp, img_size=416):
    model = Darknet(cfgs, img_size)
    model.load_weights(weightp)
    model.eval()
    return model
