# Visualizer - Programme de visualisation

## 4 fichiers Python à écrire

### 1. main.py

- **Fonction** : Programme principal, démarre tout
- **Boucle principale** :
  1. Lire les paramètres envoyés par Teensy
  2. Mettre à jour la visualisation
  3. Rendu à l'écran (60FPS)

---

### 2. SerialReader.py
- **Fonction** : Lire les paramètres envoyés par Teensy via USB
- **Méthodes principales** :
  - `connect()` - Se connecter au port série
  - `read_parameters()` - Retourner un dictionnaire de paramètres
- **Protocole** : Recevoir le format `PARAM:distortion_gain:0.75\n`

---

### 3. GraphicsEngine.py
- **Fonction** : Encapsuler Pygame pour le dessin
- **Méthodes principales** :
  - `draw_circle()` - Dessiner un cercle
  - `draw_polygon()` - Dessiner un polygone
  - `draw_gradient_circle()` - Dessiner un halo
  - `flip()` - Rafraîchir l'écran

---

### 4. AudioVisualizer.py
- **Fonction** : Transformer les paramètres d'effets en graphiques
- **Méthodes principales** :
  - `update(parameters)` - Mettre à jour l'état
  - `render()` - Dessiner
- **Règles de mappage** :
  - `distortion_gain` → Degré de distorsion graphique
  - `delay_time` → Traînée de particules
  - `reverb_size` → Taille du halo d'arrière-plan

---

## Comment exécuter
```bash
cd visualizer/
pip install -r requirements.txt
python src/main.py --port COM3
```
