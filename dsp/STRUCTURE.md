# DSP - Algorithmes d'effets audio

## 4 fichiers Faust à écrire

### 1. guitar_distortion.dsp
- **Fonction** : Effet de distorsion guitare
- **Algorithme** : Utiliser `tanh()` pour compresser le son et créer la distorsion
- **Paramètres** :
  - `gain` - Intensité de distorsion
  - `tone` - Timbre (sombre/brillant)

---

### 2. guitar_delay.dsp
- **Fonction** : Effet d'écho
- **Algorithme** : Ligne de retard + boucle de rétroaction
- **Paramètres** :
  - `delay_time` - Durée du retard (100-1000ms)
  - `feedback` - Nombre de répétitions d'écho
  - `mix` - Ratio sec/humide

---

### 3. guitar_reverb.dsp
- **Fonction** : Réverbération de salle
- **Algorithme** : Réverbération Schroeder (4 filtres en peigne + 2 filtres passe-tout)
- **Paramètres** :
  - `room_size` - Taille de la salle
  - `damping` - Atténuation des hautes fréquences
  - `mix` - Ratio sec/humide

---

### 4. guitar_main.dsp
- **Fonction** : Chaîner les 3 effets ci-dessus
- **Chaîne de signal** : `Microphone → Distorsion → Délai → Réverb → Écouteurs`
- **Code** :
```faust
import("stdfaust.lib");
distortion = library("guitar_distortion.dsp");
delay = library("guitar_delay.dsp");
reverb = library("guitar_reverb.dsp");
process = distortion : delay : reverb;
```

---

## Comment utiliser build.sh
```bash
cd dsp/
./build.sh
```
- **Fonction** : Compiler le code Faust en C++, sortie vers `firmware/src/generated/`
- **Sortie** : `FaustDSP_generated.cpp` (utilisable directement par Teensy)

---

## Performance
- Distorsion : 5% CPU
- Délai : 10% CPU
- Réverbération : 20% CPU
- **Total** : 35% CPU, suffisant
