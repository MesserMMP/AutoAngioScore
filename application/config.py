import random
import numpy as np
import torch
from omegaconf import OmegaConf

from .utils import pick_device

CFG = OmegaConf.load("configs/default.yaml")
DEVICE = pick_device(CFG.device)

def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

set_seed(CFG.seed)