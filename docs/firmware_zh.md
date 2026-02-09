# Firmware 固件代码

## 只有1个文件！

```
firmware/
└── SON.ino    ← 所有代码都在这里（310行）
```

---

## 📦 SON.ino 包含什么？

### 4个类（全在一个文件里）

#### 1. FaustDSP
- **干啥的**：DSP音效处理
- **核心方法**：
  - `setParameter()` - 设置音效参数
  - `processDistortion()` - 失真处理

#### 2. AudioProcessor
- **干啥的**：音频输入输出
- **核心方法**：
  - `begin()` - 启动音频系统
  - `setParameter()` - 传参数给DSP

#### 3. KnobController
- **干啥的**：读旋钮、平滑数值
- **核心方法**：
  - `update()` - 读ADC，平滑处理
  - `getKnob1()` / `getKnob2()` - 返回0.0-1.0

#### 4. SerialComm
- **干啥的**：USB发参数到PC
- **核心方法**：
  - `sendMultipleParameters()` - 批量发送

---

## 🎯 Arduino标准函数

### setup()
- 初始化串口（115200）
- 初始化旋钮（A0, A1）
- 初始化音频系统
- 打印系统信息

### loop()
- 每10ms执行一次（100Hz）
- 读旋钮 → 更新DSP → 发数据到PC
- LED闪烁（表示运行中）

## 🔧 需要的库

- **Audio** - Teensy音频库（Teensyduino自带）
