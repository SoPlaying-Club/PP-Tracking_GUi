# PP-Tracking GUI v2.0

## 一.项目介绍

技术栈：PP-Tracking + Pyside2

本项目是基于飞桨开源的实时目标跟踪系统[PP-Tracking](https://github.com/PaddlePaddle/PaddleDetection/blob/develop/deploy/pptracking)开发的GUI可视化界面。用户可通过GUI界面进行阈值调整、模型预测，视频结果输出等，方便了用户直接体验功能。当前覆盖单镜头的全部功能，如行人跟踪，车辆跟踪，流量统计等，适用于智慧交通、安防监控等场景。

## 二.项目界面演示：

![PP-Tracking GUI主界面1](https://gitee.com/hchhtc123/picture/raw/master/typora/PP-Tracking%20GUI%E4%B8%BB%E7%95%8C%E9%9D%A21.png)

![PP-Tracking行人追踪1](https://gitee.com/hchhtc123/picture/raw/master/typora/PP-Tracking%E8%A1%8C%E4%BA%BA%E8%BF%BD%E8%B8%AA1.png)

![PP-Tracking GUI车辆追踪1](https://gitee.com/hchhtc123/picture/raw/master/typora/PP-Tracking%20GUI%E8%BD%A6%E8%BE%86%E8%BF%BD%E8%B8%AA1.png)

![PP-Tracking GUI多类别追踪1](https://gitee.com/hchhtc123/picture/raw/master/typora/PP-Tracking%20GUI%E5%A4%9A%E7%B1%BB%E5%88%AB%E8%BF%BD%E8%B8%AA1.png)

![PP-Tracking行人追踪实操效果](https://gitee.com/hchhtc123/picture/raw/master/typora/PP-Tracking%E8%A1%8C%E4%BA%BA%E8%BF%BD%E8%B8%AA%E5%AE%9E%E6%93%8D%E6%95%88%E6%9E%9C.png)

## 三.项目配置：

推荐使用Windows或Mac环境

主要包含以下三个步骤：

- 导入训练模型，修改模型名称
- 安装必要的依赖库
- 启动前端界面

### 1. 下载预测模型

PP-Tracking 提供了覆盖多种场景的预测模型，用户可以根据自己的实际使用场景在[链接](https://github.com/PaddlePaddle/PaddleDetection/blob/develop/deploy/pptracking/README.md#%E4%BA%8C%E7%AE%97%E6%B3%95%E4%BB%8B%E7%BB%8D)中直接下载表格最后一列的预测部署模型

如果您想自己训练得到更符合您场景需求的模型，可以参考[快速开始文档](https://github.com/PaddlePaddle/PaddleDetection/blob/develop/configs/mot/fairmot/README_cn.md#%E5%BF%AB%E9%80%9F%E5%BC%80%E5%A7%8B)训练并导出预测模型

模型导出放在`./output_inference`目录下


### 2. 必要的依赖库安装

```
pip install -r requirements.txt
```
其中包括以下依赖

```
pyqt5
moviepy
opencv-python
PySide2
matplotlib
scipy
Cython
cython_bbox
paddlepaddle
pycocotools
lap
sklearn
motmetrics
openpyxl
```

**注：**

1. Windows环境下，需要手动下载安装[cython_bbox](https://pypi.org/project/pip/)，然后将setup.py中的找到steup.py, 修改`extra_compile_args=[’-Wno-cpp’]`，替换为`extra_compile_args = {'gcc': ['/Qstd=c99']}`, 然后运行`python setup.py build_ext install`
2. numpy版本需要大于1.20

### 3. 启动前端界面

执行`python main.py`启动前端界面


参数说明如下:

| 参数       | 是否必须 | 含义                                     |
| ---------- | -------- | ---------------------------------------- |
| 模型运行   | Option   | 点击后进行模型训练                       |
| 结果显示   | Option   | 在运行状态为检测完成的时候进行结果视频显示 |
| 停止运行   | Option   | 停止整个视频输出                         |
| 取消轨迹   | Option   | 在一开始时取消轨迹                       |
| 阈值调试   | Option   | 预测得分的阈值，默认为0.5                |
| 输入FPS    | Option   | 输入视频的FPS                                |
| 检测用时   | Option   | 视频的检测时间                           |
| 人流量检测 | Option   | 每隔一段帧数内的人流量统计图表           |
| 时间长度   | Option   | 人流量时间统计长度                       |
| 开启出入口 | Option   | 导入视频后可自行选择是否开启出入口训练   |
| 导出文件   | Option   | 可视化结果保存的根目录，默认为output/    |


说明：

- 如果安装的PaddlePaddle不支持基于TensorRT进行预测，需要自行编译，详细可参考[预测库编译教程](https://paddleinference.paddlepaddle.org.cn/user_guides/source_compile.html)。
- 更多配置细节可以查看提供的PP-Tracking_GUi项目环境配置教程.docx文件

## 四.代码贡献：

![PP-Tracking代码贡献](https://gitee.com/hchhtc123/picture/raw/master/typora/PP-Tracking%E4%BB%A3%E7%A0%81%E8%B4%A1%E7%8C%AE.png)

