# ===========================================================================
#   torchnet.py -------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import torch
import torch.nn as nn

#   example -----------------------------------------------------------------
# ---------------------------------------------------------------------------
    
    # https://pytorch.org/docs/master/generated/torch.nn.Conv2d.html
    # in_channels: Number of channels in the input image
    # out_channels:  Number of channels produced by the convolution
    # kernel_size: Size of the convolving kernel. Default = 1
    # strid: Stride of the convolution. Default: 1
    # stride controls the stride for the cross-correlation, a single number or a  tuple.
    # padding: Zero-padding added to both sides of the input. Default: 0
    # padding controls the amount of implicit zero-paddings on both sides for padding number of points for each dimension.        

    # https://pytorch.org/docs/master/generated/torch.nn.BatchNorm2d.html?highlight=batchnorm#torch.nn.BatchNorm2d
    # num_features: C from an expected input of size (N,C,H,W)

    # https://pytorch.org/docs/master/generated/torch.nn.ReLU.html?highlight=relu#torch.nn.ReLU
    # Applies the rectified linear unit function element-wise:

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class TorchNet1(nn.Module):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, inp_dim, mod_dim1, mod_dim2):
        super(TorchNet1, self).__init__()
        
        self.seq = nn.Sequential(

            # input dimension img to mod_dim1
            nn.Conv2d(inp_dim, mod_dim1, kernel_size=3, stride=1, padding=1), #, padding_mode="replicate"),
            nn.BatchNorm2d(mod_dim1),
            nn.ReLU(inplace=True),

            nn.Conv2d(mod_dim1, mod_dim2, kernel_size=1, stride=1, padding=0), #, padding_mode="replicate"),
            nn.BatchNorm2d(mod_dim2),
            nn.ReLU(inplace=True),

            nn.Conv2d(mod_dim2, mod_dim1, kernel_size=3, stride=1, padding=1), #, padding_mode="replicate"),
            nn.BatchNorm2d(mod_dim1),
            nn.ReLU(inplace=True),

         # input dimension mod_dim1 to mod_dim2 
            nn.Conv2d(mod_dim1, mod_dim2, kernel_size=1, stride=1, padding=0),
            nn.BatchNorm2d(mod_dim2)
        )
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def forward(self, x):
        return self.seq(x)

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class TorchNet2(nn.Module):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, inp_dim, mod_dim1, mod_dim2):
        super(TorchNet2, self).__init__()
        
        self.seq = nn.Sequential(

            # input dimension img to mod_dim1
            nn.Conv2d(inp_dim, mod_dim1, kernel_size=7, stride=1, padding=3), #, padding_mode="replicate"),
            nn.BatchNorm2d(mod_dim1),
            nn.ReLU(inplace=True),

            nn.Conv2d(mod_dim1, mod_dim2, kernel_size=5, stride=1, padding=2), #, padding_mode="replicate"),
            nn.BatchNorm2d(mod_dim2),
            nn.ReLU(inplace=True),

            nn.Conv2d(mod_dim2, mod_dim1, kernel_size=3, stride=1, padding=1), #, padding_mode="replicate"),
            nn.BatchNorm2d(mod_dim1),
            nn.ReLU(inplace=True),

         # input dimension mod_dim1 to mod_dim2 
            nn.Conv2d(mod_dim1, mod_dim2, kernel_size=1, stride=1, padding=0),
            nn.BatchNorm2d(mod_dim2)
        )
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def forward(self, x):
        return self.seq(x)

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class TorchNet3(nn.Module):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, inp_dim, mod_dim1, mod_dim2):
        super(TorchNet3, self).__init__()
        
        self.seq = nn.Sequential(

            # input dimension img to mod_dim1
            nn.Conv2d(inp_dim, mod_dim1, kernel_size=7, stride=1, padding=3), #, padding_mode="replicate"),
            nn.BatchNorm2d(mod_dim1),
            nn.ReLU(inplace=True),

            nn.Conv2d(mod_dim1, mod_dim2, kernel_size=5, stride=1, padding=2), #, padding_mode="replicate"),
            nn.BatchNorm2d(mod_dim2),
            nn.ReLU(inplace=True),

            nn.Conv2d(mod_dim2, mod_dim2, kernel_size=3, stride=1, padding=1), #, padding_mode="replicate"),
            nn.BatchNorm2d(mod_dim2),
            nn.ReLU(inplace=True),

         # input dimension mod_dim1 to mod_dim2 
            nn.Conv2d(mod_dim2, mod_dim2, kernel_size=1, stride=1, padding=0),
            nn.BatchNorm2d(mod_dim2)
        )
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def forward(self, x):
        return self.seq(x)


#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class TorchNet(nn.Module):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, inp_dim, mod_dim1, mod_dim2):
        super(TorchNet, self).__init__()
        
        self.torchnet1 = TorchNet(inp_dim=3, mod_dim1=mod_dim1, mod_dim2=mod_dim2)

        self.torchnet2 = TorchNet(inp_dim=3, mod_dim1=mod_dim1, mod_dim2=mod_dim2)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def forward(self, x):
        x1, x2 = x
        
        out1 = self.torchnet1(x1)
        out2 = self.torchnet1(x2)

        out = torch.cat((out1, out2), 1)
        return out
