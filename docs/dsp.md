# DSP 音效算法

## 需要写4个Faust文件

### 1. guitar_distortion.dsp
- **干啥的**：吉他失真效果
- **算法**：用`tanh()`把声音压扁，制造失真
- **参数**：
  - `gain` - 失真强度
  - `tone` - 音色（暗沉/明亮）

---

### 2. guitar_delay.dsp
- **干啥的**：回声效果
- **算法**：延迟线 + 反馈回路
- **参数**：
  - `delay_time` - 延迟多久（100-1000ms）
  - `feedback` - 回声重复几次
  - `mix` - 干湿比

---

### 3. guitar_reverb.dsp
- **干啥的**：房间混响
- **算法**：Schroeder混响（4个梳状滤波器+2个全通滤波器）
- **参数**：
  - `room_size` - 房间大小
  - `damping` - 高频衰减
  - `mix` - 干湿比

---

### 4. guitar_main.dsp
- **干啥的**：把上面3个效果串起来
- **信号链**：`麦克风 → 失真 → 延迟 → 混响 → 耳机`
- **代码**：
```faust
import("stdfaust.lib");
distortion = library("guitar_distortion.dsp");
delay = library("guitar_delay.dsp");
reverb = library("guitar_reverb.dsp");
process = distortion : delay : reverb;
```

---

## build.sh 怎么用
```bash
cd dsp/
./build.sh
```
- **干啥的**：把Faust代码编译成C++，输出到`firmware/src/generated/`
- **输出**：`FaustDSP_generated.cpp`（Teensy直接用）

---

## 性能
- 失真：5% CPU
- 延迟：10% CPU
- 混响：20% CPU
- **总共**：35% CPU，足够
