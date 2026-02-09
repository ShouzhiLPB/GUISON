# 系统架构设计

## 整体架构

```
┌───────────────────────────────────────────┐
│         PC可视化端 (Python)                │
│   接收参数 → 实时渲染图形                  │
└──────────────▲────────────────────────────┘
               │ USB Serial
┌──────────────┴────────────────────────────┐
│      Teensy 4.0固件 (C++ + Faust DSP)     │
│  麦克风 → DSP处理 → 耳机                   │
│         ↑ 旋钮控制                         │
└───────────────────────────────────────────┘
```

## 三大模块

### 1. Firmware（固件）

**文件**：`firmware/src/`

| 文件 | 职责 |
|------|------|
| `main.cpp` | 主程序：初始化硬件、主循环 |
| `AudioProcessor.h/cpp` | 音频流处理核心 |
| `KnobController.h/cpp` | 旋钮读取与参数映射 |
| `SerialComm.h/cpp` | USB串口通信 |
| `FaustDSP.h/cpp` | Faust DSP封装层 |

**音频流程**：
```
麦克风(ADC) → AudioProcessor → FaustDSP → 耳机(DAC)
                    ↑
              KnobController
```

### 2. DSP（音效算法）

**文件**：`dsp/`

| 文件 | 效果 |
|------|------|
| `guitar_distortion.dsp` | 失真效果（非线性饱和） |
| `guitar_delay.dsp` | 延迟效果（回声） |
| `guitar_reverb.dsp` | 混响效果（空间感） |
| `guitar_main.dsp` | 主信号链（组合所有效果） |

**编译流程**：
```
Faust源码 → faust2teensy → C++代码 → 集成到firmware
```

### 3. Visualizer（可视化）

**文件**：`visualizer/src/`

| 文件 | 职责 |
|------|------|
| `main.py` | 主程序入口 |
| `SerialReader.py` | 读取Teensy参数 |
| `GraphicsEngine.py` | 图形渲染引擎 |
| `AudioVisualizer.py` | 参数→图形映射逻辑 |

**参数映射示例**：
- `distortion` → 图形扭曲度、颜色饱和度
- `delay` → 拖尾效果、残影数量
- `reverb` → 背景光晕、模糊半径

## 技术栈

| 层级 | 技术 |
|------|------|
| 硬件 | Teensy 4.0 + Audio Shield |
| 固件 | C++ + Teensy Audio Library |
| DSP | Faust语言 |
| 可视化 | Python + Pygame/OpenGL |
| 通信 | USB Serial |

## 设计原则

1. **模块化**：每个模块独立编译、测试
2. **实时性**：音频处理延迟 < 10ms
3. **可扩展**：轻松添加新效果器
4. **精简**：零冗余代码和文档
