# Définition des paramètres d'effets

## Mappage des potentiomètres

| Potentiomètre | Paramètre contrôlé | Plage | Description |
|---------------|-------------------|-------|-------------|
| Knob 1 | `distortion_gain` | 0.0 - 1.0 | Gain de distorsion (0=propre, 1=distorsion lourde) |
| Knob 2 | `effect_mix` | 0.0 - 1.0 | Mélange d'effets (0=son original, 1=plein effet) |

## Table des paramètres DSP

### 1. Distortion (Distorsion)

| Nom du paramètre | Type | Plage | Valeur par défaut | Description |
|-----------------|------|-------|-------------------|-------------|
| `distortion_gain` | float | 0.0 - 1.0 | 0.5 | Intensité de distorsion |
| `distortion_tone` | float | 0.0 - 1.0 | 0.5 | Timbre (équilibre basses/hautes fréquences) |

### 2. Delay (Délai)

| Nom du paramètre | Type | Plage | Valeur par défaut | Description |
|-----------------|------|-------|-------------------|-------------|
| `delay_time` | float | 0.0 - 1.0 | 0.3 | Temps de retard (mappé sur 100-1000ms) |
| `delay_feedback` | float | 0.0 - 1.0 | 0.4 | Quantité de rétroaction (nombre d'échos) |
| `delay_mix` | float | 0.0 - 1.0 | 0.3 | Ratio sec/humide |

### 3. Reverb (Réverbération)

| Nom du paramètre | Type | Plage | Valeur par défaut | Description |
|-----------------|------|-------|-------------------|-------------|
| `reverb_size` | float | 0.0 - 1.0 | 0.6 | Taille de la salle |
| `reverb_damping` | float | 0.0 - 1.0 | 0.5 | Amortissement (atténuation hautes fréquences) |
| `reverb_mix` | float | 0.0 - 1.0 | 0.25 | Ratio sec/humide |

## Mappage de visualisation

### Paramètres → Éléments visuels

| Paramètre d'effet | Effet visuel | Méthode d'implémentation |
|------------------|--------------|--------------------------|
| `distortion_gain` | Degré de distorsion graphique | Décalage des sommets |
| `distortion_gain` | Saturation des couleurs | Coefficient de saturation RGB |
| `delay_time` | Longueur de traînée | Durée de vie des particules |
| `delay_feedback` | Nombre d'images rémanentes | Nombre de couches de mélange Alpha |
| `reverb_size` | Rayon du halo d'arrière-plan | Rayon de flou gaussien |
| `reverb_damping` | Température de couleur | Décalage de teinte |

## Fréquence de mise à jour des paramètres

- **Échantillonnage des potentiomètres** : 100Hz (intervalle de 10ms)
- **Mise à jour des paramètres DSP** : Temps réel (chaque bloc audio)
- **Envoi série** : 30Hz (intervalle de 30ms, réduit la charge de communication)
- **Rafraîchissement de visualisation** : 60Hz (intervalle de 16.6ms)

## Lissage des paramètres

Pour éviter les clics causés par des changements brusques, tous les changements de paramètres utilisent un filtre passe-bas de premier ordre :

```
Constante de temps de lissage : τ = 50ms
Formule de mise à jour : param_smooth = param_smooth * 0.95 + param_new * 0.05
```
