# Firmware - Code du micrologiciel

## Un seul fichier !

```
firmware/
└── SON.ino    ← Tout le code est ici (310 lignes)
```

---

## 📦 Que contient SON.ino ?

### 4 classes (toutes dans un seul fichier)

#### 1. FaustDSP
- **Fonction** : Traitement audio DSP
- **Méthodes principales** :
  - `setParameter()` - Définir les paramètres d'effet
  - `processDistortion()` - Traitement de distorsion

#### 2. AudioProcessor
- **Fonction** : Entrée/sortie audio
- **Méthodes principales** :
  - `begin()` - Démarrer le système audio
  - `setParameter()` - Transmettre les paramètres au DSP

#### 3. KnobController
- **Fonction** : Lecture des potentiomètres et lissage
- **Méthodes principales** :
  - `update()` - Lire l'ADC, lissage
  - `getKnob1()` / `getKnob2()` - Renvoie 0.0-1.0

#### 4. SerialComm
- **Fonction** : Envoyer les paramètres au PC via USB
- **Méthodes principales** :
  - `sendMultipleParameters()` - Envoi par lots
  - Format : `PARAM:distortion_gain:0.75\n`

---

## 🎯 Fonctions standard Arduino

### setup()
- Initialiser le port série (115200)
- Initialiser les potentiomètres (A0, A1)
- Initialiser le système audio
- Afficher les informations système

### loop()
- Exécute toutes les 10ms (100Hz)
- Lire les potentiomètres → Mettre à jour le DSP → Envoyer au PC
- Clignotement de la LED (indique le fonctionnement)

---

---

## 🔧 Bibliothèques requises

- **Audio** - Bibliothèque audio Teensy (incluse avec Teensyduino)

C'est tout ! Tout le reste est intégré.
