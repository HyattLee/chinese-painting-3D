# 中国山水画三维场景构建平台
该平台的通过Flask Web框架实现；HTML文本在src/templates中；其他前端文件，例如JS等，在src/static中。

平台运行方法：

    cd src
    sudo python main.py
    
在Firefox（不要chrome）中访问ip/实现平台访问（因为设置的端口号是80，所以不用在ip后面加端口号）。

# 场景构建过程
## 创建高度图
### 前端草图交实现互绘制
src/templates/painting.html
### 地形辅助线解析
通过在src/main.py中route(“/achieveSketch”)响应函数中调用sketch/handleSketch.py中的function parseTerrainSketch实现
### 高度图生成
通过在src/main.py中route(“/achieveSketch”)响应函数中调用terrain/createHeightMap.py实现，过程分为4步：

1. createMountain 创建山

2. createPlane 创建地平面

3. mountainPlusPlaneWithSmooth 将山和地平面叠加后进行平滑

4. addNoiseToMap 向高度图的山体部分加入噪声

### 创建流图
### 前端SPH可视化交互
src/templates/waterFlowCreator.html

通过src/static/three.js实现SPH可视化绘制

通过src/static/SPH-Fluid-WebGL/js/sph_fluid.js实现SPH粒子受力分析计算
### 载入场景
