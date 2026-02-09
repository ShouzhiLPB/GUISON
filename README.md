# GUISON - Guitar Effects DSP Project

Projet son : Synthétiseur de guitare en temps réel avec processeur d'effets et visualisation

Processeur d'effets guitare en temps réel basé sur Teensy 4.0 et Faust + Système de visualisation (spectre des fréquences, lissajous, etc.)

## Démarrage rapide

### Matériel requis
- Carte de développement Teensy 4.0
- Module audio (interface I2S)
- Plusieurs potentiomètres
- Microphone + Écouteurs
- Breadboard, résistances, câbles de connexion

### Logiciels requis
- PlatformIO (développement firmware)
- Compilateur Faust (algorithmes DSP)
- Python 3.10+ (visualisation)

## Structure du projet

```
GUISON/
├── hardware/      # Schémas de circuits et définitions de broches
├── firmware/      # Firmware Teensy (arduino)
├── dsp/           # Algorithmes d'effets Faust
├── visualizer/    # Visualisation côté PC (Python)
└── docs/          # Documentation principale
```

## Flux de développement

1. **Connexion matérielle** - Voir `hardware/circuit.txt`
2. **Compiler le DSP** - Aller dans `dsp/` et exécuter `./build.sh`
3. **Téléverser le firmware** - Uploader `firmware/` via PlatformIO
4. **Démarrer la visualisation** - Exécuter `python visualizer/src/main.py`

## Fonctionnalités principales

- Effets guitare en temps réel : Distorsion / Délai / Réverbération
- Contrôle par potentiomètres : 2 potentiomètres ajustent les paramètres en temps réel
- Visualisation : Les paramètres d'effets pilotent des graphiques dynamiques sur PC

## Documentation

- [Conception de l'architecture](docs/architecture.md) - Architecture système et description des modules
- [Définition des paramètres](docs/parameters.md) - Table de mappage des paramètres d'effets
