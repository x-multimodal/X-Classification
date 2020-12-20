import os
import argparse
import torch
from datasets.dataset_loader import get_test_loader
from models.get_network import get_network

def test_engine(__C):
    # define the network
    net = get_network(__C)
    net = net.cuda()
    net.eval()

    # get the test loader
    test_loader = get_test_loader(__C)

    # define the weight path and load weight
    weight_path = os.path.join(__C.ckpts_dir, __C.model, __C.version)
    if not os.path.exists(weight_path):
        print("the weight doesn't exist, please check the args: --ckpt_v")
    else:
        weight_path = os.path.join(weight_path,'{net}-{ckpt_e}-{type}.pth')
        weight_path.format(net=__C.model, ckpt_e=__C.ckpt_e, type=__C.ckpt_type)
    net.load_state_dict(torch.load(weight_path))

    # define the statistic params
    correct_1 = 0.0
    correct_5 = 0.0
    total = 0
    with torch.no_grad():
        for step, (images, labels) in enumerate(test_loader):
            print("iteration: {}\ttotal {} iterations".format(step + 1, len(test_loader)))
            images = images.cuda()
            labels = labels.cuda()

            test_outputs = net(images)
            _, pred = test_outputs.topk(5, 1, largest=True, sorted=True)
            labels = labels.view(labels.size(0), -1).expand_as(pred)
            correct = pred.eq(labels).float()

            # compute Top-5 Accuracy
            correct_5 += correct[:, :5].sum()

            # compute Top-1 Accuracy
            correct_1 += correct[:, :1].sum()

        print()
        print("Top 1 err: ", 1 - correct_1 / len(test_loader.dataset))
        print("Top 5 err: ", 1 - correct_5 / len(test_loader.dataset))
        print("Parameter numbers: {}".format(sum(p.numel() for p in net.parameters())))