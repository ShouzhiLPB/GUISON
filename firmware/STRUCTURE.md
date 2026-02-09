# Firmware - Code du micrologiciel

## 5 fichiers à écrire

### 1. main.cpp
- **Fonction** : Point d'entrée du programme, coordonne tous les modules
- **Ce qu'il faut écrire** :
  - `setup()` - Initialiser tout le matériel
  - `loop()` - Lire les potentiomètres → Mettre à jour le DSP → Envoyer les données au PC

---

### 2. AudioProcessor.h/cpp
- **Fonction** : Traiter les entrées et sorties audio
- **Méthodes principales** :
  - `begin()` - Démarrer le système audio
  - `processAudio()` - Microphone → Traitement DSP → Écouteurs
  - `setParameter()` - Définir les paramètres d'effets

---

### 3. KnobController.h/cpp
- **Fonction** : Lire les potentiomètres, lisser les valeurs
- **Méthodes principales** :
  - `update()` - Lire l'ADC, traitement de lissage
  - `getKnob1()` / `getKnob2()` - Retourne une valeur entre 0.0 et 1.0

---

### 4. SerialComm.h/cpp
- **Fonction** : Envoyer les paramètres au PC via USB
- **Méthodes principales** :
  - `sendParameter(name, value)` - Envoyer une donnée
  - Format : `PARAM:distortion_gain:0.75\n`

---

### 5. FaustDSP.h/cpp
- **Fonction** : Encapsuler le code d'effets généré par Faust
- **Méthodes principales** :
  - `compute()` - Traiter l'audio
  - `setParameter()` - Ajuster les paramètres d'effets

---

## Dépendances
```
main.cpp appelle → AudioProcessor (audio)
                 → KnobController (potentiomètres)
                 → SerialComm (communication)
            
AudioProcessor appelle → FaustDSP (effets)
```
