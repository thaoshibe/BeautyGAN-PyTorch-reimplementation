import os, glob, cv2
import torch
import random
import linecache
import numpy as np

from torch.utils.data import Dataset
from PIL import Image

class MAKEUP(Dataset):
    def __init__(self, image_path, transform, mode, transform_mask, cls_list):
        self.image_path = image_path
        self.transform = transform
        self.mode = mode
        self.transform_mask = transform_mask

        self.A_seg = glob.glob(os.path.join(image_path, 'segs', 'non-makeup', '*.png'))
        self.As = [os.path.join(image_path, 'images', 'non-makeup', x.split('/')[-1]) for x in self.A_seg]
        self.B_seg = glob.glob(os.path.join(image_path, 'segs', 'makeup', '*.png'))
        self.Bs = [os.path.join(image_path, 'images', 'makeup', x.split('/')[-1]) for x in self.B_seg]

        self.noiA = len(self.As)
        self.noiB = len(self.Bs)

        print(self.noiA, self.noiB)

    def __getitem__(self, index):
        if self.mode == 'train':
            idxA = random.choice(range(self.noiA))
            idxB = random.choice(range(self.noiB))

            mask_A = Image.open(self.A_seg[idxA]).convert("RGB")
            mask_B = Image.open(self.B_seg[idxB]).convert("RGB")
            
            image_A = Image.open(self.As[idxA]).convert("RGB")
            image_B = Image.open(self.Bs[idxB]).convert("RGB")
            
            image_A = Image.fromarray(cv2.resize(np.array(image_A), (256, 256)))
            image_B = Image.fromarray(cv2.resize(np.array(image_B), (256, 256)))
            return self.transform(image_A), self.transform(image_B), self.transform_mask(mask_A), self.transform_mask(mask_B)

    def __len__(self):
        if self.mode == 'train' or self.mode == 'train_finetune':
            num_A = len(self.As)
            num_B = len(self.Bs)
            return max(num_A, num_B)
        
        elif self.mode in ['test', "test_baseline", 'test_all']:
            num_A = len(self.As)
            num_B = len(self.Bs)
            return num_A * num_B