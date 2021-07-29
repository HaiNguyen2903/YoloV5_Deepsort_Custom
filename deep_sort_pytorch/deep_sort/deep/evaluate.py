import torch
from IPython import embed
import argparse

parser = argparse.ArgumentParser(description="Train on market1501")
parser.add_argument("--predict-path", default='predicts/features_train25epochs.pth', type=str)
parser.add_argument("--topk", default=5, type=int)
args = parser.parse_args()

features = torch.load(args.predict_path)

'''
gf: querry frames: shape (frames x features_len) (208 x 512)
ql: querry labels: vector len = number of querry images
gf: gallery frames: shape (frames x features_len) (21549 x 512)
gl: gallery labels: vector len = number of gallery images
'''

qf = features["qf"]
ql = features["ql"]
gf = features["gf"]
gl = features["gl"]

# matrix of confidence with shape (querry frames x gallery frames)
scores = qf.mm(gf.t())

# return vector of index in scores metric that have highest score for each querry: len = querry frame
res = scores.topk(5, dim=1)[1][:, 0]            

# total equal values between ql and ql vectors
top1correct = gl[res].eq(ql).sum().item()

print("Accuracy top 1: {:.3f}".format(top1correct / ql.size(0)))


def calculate_precision_k(features, k=5):

    qf = features["qf"]
    ql = features["ql"]
    gf = features["gf"]
    gl = features["gl"]

    # matrix of confidence with shape (querry frames x gallery frames)
    scores = qf.mm(gf.t())

    # return vector of index in scores metric that have highest score for each querry: len = querry frame
    res = scores.topk(k, dim=1)[1]

    # top_pred for each query
    pred = gl[res]

    # average p@k for all queries
    avg_acc = 0

    # for each query
    for i in range(ql.size(0)): 
        # number of correct label in top k
        correct = 0
        # count number of label value in pred equal to true label
        correct += pred[i].eq(ql[i]).sum().item()

        # acc for each query
        acc = correct/k
        
        avg_acc += acc

    # calculate average acc
    avg_acc /= ql.size(0)

    print('P@{}: {:.3f}'.format(k, avg_acc))
    return avg_acc

if __name__ == '__main__':
    calculate_precision_k(features, args.topk)