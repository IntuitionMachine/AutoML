import torch

from torch import nn
import numpy as np

from .retinanet import ret18, ret34, ret50, ret101, ret152
from .resnet import ResNet
from .pyramidnet import PyramidNet
from .shakeshake.shake_resnet import ShakeResNet
from .wideresnet import WideResNet
from .shakeshake.shake_resnext import ShakeResNeXt
from .efficientnet_pytorch import EfficientNet, RoutingFn
# from tf_port.tpu_bn import TpuBatchNormalization


def get_model(model_name, num_classes=10, depth=None, ratios=None, scales=None, weights_dir=None, pretrained=True):


    if model_name == 'retinanet':
        retinanet = {18: ret18, 34: ret34, 50: ret50, 101: ret101, 152: ret152}
        model = retinanet[depth](num_classes=num_classes, ratios=ratios, scales=scales,
                                       weights_dir=weights_dir,
                                       pretrained=pretrained)
    elif model_name == 'resnet50':
        model = ResNet(dataset='imagenet', depth=50, num_classes=num_classes, bottleneck=True)
    elif model_name == 'resnet200':
        model = ResNet(dataset='imagenet', depth=200, num_classes=num_classes, bottleneck=True)
    elif model_name == 'wresnet40_2':
        model = WideResNet(40, 2, dropout_rate=0.0, num_classes=num_classes)
    elif model_name == 'wresnet28_10':
        model = WideResNet(28, 10, dropout_rate=0.0, num_classes=num_classes)

    elif model_name == 'shakeshake26_2x32d':
        model = ShakeResNet(26, 32, num_classes)
    elif model_name == 'shakeshake26_2x64d':
        model = ShakeResNet(26, 64, num_classes)
    elif model_name == 'shakeshake26_2x96d':
        model = ShakeResNet(26, 96, num_classes)
    elif model_name == 'shakeshake26_2x112d':
        model = ShakeResNet(26, 112, num_classes)

    elif model_name == 'shakeshake26_2x96d_next':
        model = ShakeResNeXt(26, 96, 4, num_classes)

    elif model_name == 'pyramid':
        model = PyramidNet('cifar10', depth=conf['depth'], alpha=conf['alpha'], num_classes=num_classes, bottleneck=conf['bottleneck'])

    elif 'efficientnet' in model_name:
        model = EfficientNet.from_name(model_name, condconv_num_expert=conf['condconv_num_expert'], norm_layer=None)  # TpuBatchNormalization
        if local_rank >= 0:
            model = nn.SyncBatchNorm.convert_sync_batchnorm(model)
        def kernel_initializer(module):
            def get_fan_in_out(module):
                num_input_fmaps = module.weight.size(1)
                num_output_fmaps = module.weight.size(0)
                receptive_field_size = 1
                if module.weight.dim() > 2:
                    receptive_field_size = module.weight[0][0].numel()
                fan_in = num_input_fmaps * receptive_field_size
                fan_out = num_output_fmaps * receptive_field_size
                return fan_in, fan_out

            if isinstance(module, torch.nn.Conv2d):
                # https://github.com/tensorflow/tpu/blob/master/models/official/efficientnet/efficientnet_model.py#L58
                fan_in, fan_out = get_fan_in_out(module)
                torch.nn.init.normal_(module.weight, mean=0.0, std=np.sqrt(2.0 / fan_out))
                if module.bias is not None:
                    torch.nn.init.constant_(module.bias, val=0.)
            elif isinstance(module, RoutingFn):
                torch.nn.init.xavier_uniform_(module.weight)
                torch.nn.init.constant_(module.bias, val=0.)
            elif isinstance(module, torch.nn.Linear):
                # https://github.com/tensorflow/tpu/blob/master/models/official/efficientnet/efficientnet_model.py#L82
                fan_in, fan_out = get_fan_in_out(module)
                delta = 1.0 / np.sqrt(fan_out)
                torch.nn.init.uniform_(module.weight, a=-delta, b=delta)
                if module.bias is not None:
                    torch.nn.init.constant_(module.bias, val=0.)
        model.apply(kernel_initializer)
    else:
        raise NameError('no model named, %s' % model_name)


    # device = torch.device('cuda', local_rank)
    # model = model.to(device)
    # model = DistributedDataParallel(model, device_ids=[local_rank], output_device=local_rank)

    # THIS CAN SUBSTANTIALLY SLOW DOWN THE FIRST EPOCH WHEN TIMES ARE DIFFERENT
    # cudnn.benchmark = True
    return model


def num_class(dataset):
    return {
        'cifar10': 10,
        'reduced_cifar10': 10,
        'cifar10.1': 10,
        'cifar100': 100,
        'svhn': 10,
        'reduced_svhn': 10,
        'imagenet': 1000,
        'reduced_imagenet': 120,
    }[dataset]
