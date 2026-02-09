# Hardware - Connexions matérielles

## 2 documents

### 1. circuit.txt

- **Fonction** : Indique comment câbler les composants
- **Contenu principal** :
  - Microphone → Teensy A2
  - Potentiomètre 1 → Teensy A0
  - Potentiomètre 2 → Teensy A1
  - Module DAC → Broches I2S Teensy (Pin 7, 20, 21)
  - Alimentation USB

---

### 2. pinout.txt
- **Fonction** : Table d'attribution des broches Teensy
- **Contenu principal** :
  - A0, A1, A2 → Potentiomètres et microphone
  - Pin 7, 20, 21 → Audio I2S
  - USB → Communication et alimentation
  - 9 broches utilisées, 31 disponibles pour extension
