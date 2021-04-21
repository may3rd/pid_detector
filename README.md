# PID_Detector
P&amp;ID Detector by using Deep learning.

## Deep Learning
### Darknet
The P&amp;ID symbol detection is established by using [darknet](https://pjreddie.com/darknet/yolo/)

## Dataset Preparing

The dataset for training and validating models was prepared from P&amp;ID from various projects.

### Use image_slicer to divide image into tiles

image_slicer 

```python
import image_slicer
image_slicer.slice('cake.jpg', 4)
```