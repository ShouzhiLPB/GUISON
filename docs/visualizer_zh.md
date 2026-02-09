# Visualizer 可视化程序

## 需要写4个Python文件

### 1. main.py

- **干啥的**：主程序，启动一切
- **主循环**：
  1. 读取Teensy发来的参数
  2. 更新可视化
  3. 渲染到屏幕（60FPS）

---

### 2. SerialReader.py
- **干啥的**：从USB读取Teensy发来的参数
- **核心方法**：
  - `connect()` - 连接串口
  - `read_parameters()` - 返回参数字典
- **协议**：接收`PARAM:distortion_gain:0.75\n`这种格式

---

### 3. GraphicsEngine.py
- **干啥的**：封装Pygame，画图用
- **核心方法**：
  - `draw_circle()` - 画圆
  - `draw_polygon()` - 画多边形
  - `draw_gradient_circle()` - 画光晕
  - `flip()` - 刷新屏幕

---

### 4. AudioVisualizer.py
- **干啥的**：把音效参数变成图形
- **核心方法**：
  - `update(parameters)` - 更新状态
  - `render()` - 画图
- **映射规则**：
  - `distortion_gain` → 图形扭曲程度
  - `delay_time` → 粒子拖尾
  - `reverb_size` → 背景光晕大小

---

## 怎么运行
```bash
cd visualizer/
pip install -r requirements.txt
python src/main.py --port COM3
```
