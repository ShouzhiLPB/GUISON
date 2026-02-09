# Conception de l'architecture système

## Architecture globale

```
┌───────────────────────────────────────────┐
│     Visualisation côté PC (Python)         │
│   Recevoir paramètres → Rendu graphique   │
└──────────────▲────────────────────────────┘
               │ USB Serial
┌──────────────┴────────────────────────────┐
│   Firmware Teensy 4.0 (C++ + Faust DSP)   │
│  Micro → Traitement DSP → Écouteurs        │
│         ↑ Contrôle potentiomètres          │
└───────────────────────────────────────────┘
```

## Trois modules principaux

### 1. Firmware (Micrologiciel)

**Fichiers** : `firmware/src/`

| Fichier | Responsabilité |
|---------|---------------|
| `main.cpp` | Programme principal : initialisation matérielle, boucle principale |
| `AudioProcessor.h/cpp` | Noyau de traitement du flux audio |
| `KnobController.h/cpp` | Lecture des potentiomètres et mappage des paramètres |
| `SerialComm.h/cpp` | Communication USB série |
| `FaustDSP.h/cpp` | Couche d'encapsulation Faust DSP |

**Flux audio** :
```
Microphone(ADC) → AudioProcessor → FaustDSP → Écouteurs(DAC)
                        ↑
                  KnobController
```

### 2. DSP (Algorithmes d'effets)

**Fichiers** : `dsp/`

| Fichier | Effet |
|---------|-------|
| `guitar_distortion.dsp` | Effet de distorsion (saturation non linéaire) |
| `guitar_delay.dsp` | Effet de délai (écho) |
| `guitar_reverb.dsp` | Effet de réverbération (sens spatial) |
| `guitar_main.dsp` | Chaîne de signal principale (combine tous les effets) |

**Flux de compilation** :
```
Code source Faust → faust2teensy → Code C++ → Intégration au firmware
```

### 3. Visualizer (Visualisation)

**Fichiers** : `visualizer/src/`

| Fichier | Responsabilité |
|---------|---------------|
| `main.py` | Point d'entrée du programme principal |
| `SerialReader.py` | Lire les paramètres Teensy |
| `GraphicsEngine.py` | Moteur de rendu graphique |
| `AudioVisualizer.py` | Logique de mappage paramètres→graphiques |

**Exemples de mappage de paramètres** :
- `distortion` → Degré de distorsion graphique, saturation des couleurs
- `delay` → Effet de traînée, nombre d'images rémanentes
- `reverb` → Halo d'arrière-plan, rayon de flou

## Protocole de communication

### Format USB Serial
```
PARAM:distortion:0.75
PARAM:delay_time:0.50
PARAM:reverb_size:0.85
```

- Débit en bauds : 115200
- Format : `PARAM:<nom_paramètre>:<valeur(0.0-1.0)>\n`

## Pile technologique

| Niveau | Technologie |
|--------|-------------|
| Matériel | Teensy 4.0 + Audio Shield |
| Firmware | C++ + Teensy Audio Library |
| DSP | Langage Faust |
| Visualisation | Python + Pygame/OpenGL |
| Communication | USB Serial |

## Principes de conception

1. **Modularité** : Chaque module compilé et testé indépendamment
2. **Temps réel** : Latence de traitement audio < 10ms
3. **Extensibilité** : Ajout facile de nouveaux effets
4. **Minimalisme** : Zéro redondance dans le code et la documentation
