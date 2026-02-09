# Firmware 固件代码

## 需要写5个文件

### 1. main.cpp
- **干啥的**：程序入口，协调所有模块
- **要写啥**：
  - `setup()` - 初始化所有硬件
  - `loop()` - 读旋钮 → 更新DSP → 发数据到PC

---

### 2. AudioProcessor.h/cpp
- **干啥的**：处理音频输入输出
- **核心方法**：
  - `begin()` - 启动音频系统
  - `processAudio()` - 麦克风 → DSP处理 → 耳机
  - `setParameter()` - 设置音效参数

---

### 3. KnobController.h/cpp
- **干啥的**：读旋钮、平滑数值
- **核心方法**：
  - `update()` - 读取ADC，平滑处理
  - `getKnob1()` / `getKnob2()` - 返回0.0-1.0的值

---

### 4. SerialComm.h/cpp
- **干啥的**：通过USB发参数到PC
- **核心方法**：
  - `sendParameter(name, value)` - 发一条数据
  - 格式：`PARAM:distortion_gain:0.75\n`

---

### 5. FaustDSP.h/cpp
- **干啥的**：封装Faust生成的音效代码
- **核心方法**：
  - `compute()` - 处理音频
  - `setParameter()` - 调节音效参数

---

## 依赖关系
```
main.cpp 调用→ AudioProcessor（音频）
            → KnobController（旋钮）
            → SerialComm（通信）
            
AudioProcessor 调用→ FaustDSP（音效）
```
