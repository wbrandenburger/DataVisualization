# Unsupervised Segmentation

## Convolutional Neural Net

### General

- [Explanation](https://www.pyimagesearch.com/2018/12/31/keras-conv2d-and-convolutional-layers/)
- [Dilated Convolution](https://erogol.com/dilated-convolution/)

### Convolutions

- If your input images are greater than 128×128 you may choose to use a kernel size > 3 to help (1) learn larger spatial filters and (2) to help reduce volume size
- Dimensionality reduction which helps to keep the number of parameters in the network low.

### Stride

- Typically you’ll leave the strides parameter with the default (1, 1) value; however, you may occasionally increase it to (2, 2) to help reduce the size of the output volume (since the step size of the filter is larger).

### Data Format

- The data format value in the Conv2D class can be either channels_last (height x width x depth) or channels_first (depth x height x width)

### [Batch Normalization](https://en.wikipedia.org/wiki/Batch_normalization)

- Each layer of a neural network has inputs with a corresponding distribution, which is affected during the training process by the randomness in the parameter initialization and the randomness in the input data. The effect of these sources of randomness on the distribution of the inputs to internal layers during training is described as internal covariate shift.
- It is used to normalize the input layer by re-centering and re-scaling.
- Recently, some scholars have argued that batch normalization does not reduce internal covariate shift, but rather smooths the objective function, which in turn improves the performance.

- In a neural network, batch normalization is achieved through a normalization step that fixes the means and variances of each layer's inputs. Ideally, the normalization would be conducted over the entire training set, but to use this step jointly with stochastic optimization methods, it is impractical to use the global information. Thus, normalization is restrained to each mini-batch in the training process.
- During the training stage of networks, as the parameters of the preceding layers change, the distribution of inputs to the current layer changes accordingly, such that the current layer needs to constantly readjust to new distributions. This problem is especially severe for deep networks, because small changes in shallower hidden layers will be amplified as they propagate within the network, resulting in significant shift in deeper hidden layers. Therefore, the method of batch normalization is proposed to reduce these unwanted shifts to speed up training and to produce more reliable models.

#### Benefits of Batch Normalization

The intention behind batch normalization is to optimize network training. It has been shown to have several benefits:

- Networks train faster — Whilst each training iteration will be slower because of the extra normalization calculations during the forward pass and the additional hyperparameters to train during back propagation. However, it should converge much more quickly, so training should be faster overall.
- Allows higher learning rates — Gradient descent usually requires small learning rates for the network to converge. As networks get deeper, gradients get smaller during back propagation, and so require even more iterations. Using batch normalization allows much higher learning rates, increasing the speed at which networks train.
- Makes weights easier to initialize — Weight initialization can be difficult, especially when creating deeper networks. Batch normalization helps reduce the sensitivity to the initial starting weights.
- Makes more activation functions viable — Some activation functions don’t work well in certain situations. Sigmoids lose their gradient quickly, which means they can’t be used in deep networks, and ReLUs often die out during training (stop learning completely), so we must be careful about the range of values fed into them. But as batch normalization regulates the values going into each activation function, nonlinearities that don’t work well in deep networks tend to become viable again.
- Simplifies the creation of deeper networks — The previous 4 points make it easier to build and faster to train deeper neural networks, and deeper networks generally produce better results.
- Provides some regularization — Batch normalization adds a little noise to your network, and in some cases, (e.g. Inception modules) it has been shown to work as well as dropout. You can consider batch normalization as a bit of extra regularization, allowing you to reduce some of the dropout you might add to a network.

## Examples

### [Automatic Segmentation of MR Brain Images](https://arxiv.org/pdf/1704.03295.pdf)

```Python
nn.Conv2d((25*25, ), (11*11, ), kernel_size=5, stride=1, padding=2) # 1
nn.Conv2d((11*11, ), (5*5, ), kernel_size=3, stride=1, padding=1) # 24
nn.Conv2d((5*5, ), (3*3, ), kernel_size=3, stride=1, padding=1) # 32
nn-Linear((3*3, ), 256 ) # 48

nn.Conv2d((51*51,), (23*23, ), kernel_size=7, stride=1, padding=3) # 1
nn.Conv2d((23*23,), (10*10, ), kernel_size=5, stride=1, padding=2) # 24
nn.Conv2d((10*10, ), (4*4, ), kernel_size=3, stride=1, padding=1) # 32
nn-Linear((4*4, ), 256 ) # 48

nn.Conv2d((75*75, ), (34*34, ), kernel_size=9, stride=1, padding=4) # 1 
nn.Conv2d((34*34, ), (14*14), kernel_size=7, stride=1, padding=3) # 24
nn.Conv2d((14*14, ), (5*5, ), kernel_size=5, stride=1, padding=2) # 32
nn-Linear((5*5, ), 256 ) # 48

```

- Max-pooling with kernels of 2×2 voxels is performed on the convolved images.
- To allow the method to use multi-scale information about each voxel, multiple patch sizes are used. The larger scales implicitly provide spatial information,because they are large enough to recognize where in the image the voxel is located, while the smaller scales provide detailed information about the local neighborhood of the voxel.
- For each of these patch sizes, different kernel sizes are trained,i.e. larger kernel sizes are used for larger patches. This multi-scale approach allows the network to incorporate local details as well as global spatial consistency.
- For each of the patch sizes, a separate network branch is used; only the output layer is shared.
- Multiple convolution layers are used; after each convolution, the resulting images are sub-sampled by extracting the highest responses with max-pooling.
- While the dimensions of the patches decrease in each layer, the number of kernels that are trained increases.
- After the convolution layers, separate fully connected layers are used for each input patch size. To perform the final classification, these layers are connected to a single softmax output layer with one node for each class (including a background class).

- Rectified linear units [39] are used for all nodes because of their speed in training CNNs .

### [Unsupervised Image Segmentation by Backpropagation](https://arxiv.org/pdf/1704.03295.pdf)

- Constraint on the number of each unique cluster.
- The intra-axis normalization process for the response map before assigning cluster labels via argmax classification - here, we use batch normalization.
- This operation (also known as whitening) converts the original response to a new one, where each axis has zero mean and unit variance.