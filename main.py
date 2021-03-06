import opts
import torch
import train
import test
import os
from torch import  cuda


if __name__ == '__main__':
    opt = vars(opts.parse().parse_args())
    torch.manual_seed(12)
    torch.set_default_tensor_type('torch.FloatTensor')
#################################################################
    # cuda stuff
    cuda.set_device(opt['devid'])
    print('\n\27[32mModels will be saved in \27[0m\27[4m' + str(opt['save']) + '\27[0m')
    if not os.path.exists(str(opt['save'])):
        os.mkdir(str(opt['save']))
    if opt['saveAll']:
        if not os.path.exists(str(opt['save'])+'/all'):
            os.mkdir(str(opt['save'])+'/all')

#################################################################
data = None
if opt['dataset'] == 'cv':
    import data.loadCamVid as DataLoader
    data = DataLoader.CamVidDataLoader
    opt['conClasses'] = data.conClasses, opt['Classes'] = data.classes, opt['histClasses'] = data.histClasses
    opt['trainData'] = data.trainData, opt['testData'] = data.testData
    print ("data is loadCamVid")
elif opt['dataset'] == 'cs':
    import data.loadCityscapes as DataLoader
    data = DataLoader.CityScapeDataLoader(opt)
    data.data_loader()
    opt['conClasses'] = data.conClasses
    opt['Classes'] = data.classes
    opt['histClasses'] = data.histClasses
    print(type(data.train_data))
    opt['trainData'] = data.train_data
    opt['testData'] = data.val_data
    print ("data is loadCityscapes")
else:
    print ("data loader could not be found")


#################################################################
curr_dir = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(curr_dir, opt['save'], 'opt.txt')
fp = open(filename, 'w')
for arg in opt:
    fp.write(str(arg) + ":" + str(opt[arg]) + "\n")
fp.close()

#################################################################
epoch = 1

folder, filename = opt['model'].split('/')
print("folder and filename:", folder, filename, "\n")
old_path = os.getcwd()
#os.chdir(folder)

#model_raw = __import__(filename+".py") 
#model_raw = __import__('model.py'
if filename == 'model.py':
    import  models.model as model
elif filename == 'nobypass.py':
    import models.nobypass as model
else:
    import models.model_res_dec as model

model_init = model.Model(opt)
Train = train.Train(model_init, opt)
Test = test.Test(opt)


print('\27[31m\27[4m\nTraining and testing started\27[0m')
print('[batchSize = ' + str(opt['batchSize']) + ']')

while epoch < opt['maxepoch']:
    print('\27[31m\27[4m\nEpoch # ', epoch, '\27[0m')
    print('==> Training:')
    trainConf, model, loss = Train.train(opt['trainData'], opt['Classes'], epoch)
    print('==> Testing:')
    Test.test(opt['testData'], opt['Classes'], epoch, trainConf, model, loss)
    trainConf = None

    epoch = epoch + 1

#################################################################
