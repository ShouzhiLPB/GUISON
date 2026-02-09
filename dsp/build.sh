#!/bin/bash
# Script de compilation Faust DSP - Génère du code C++ compatible Teensy

echo "=== Script de build Faust DSP ==="

# Vérifier si Faust est installé
if ! command -v faust &> /dev/null; then
    echo "Erreur : Compilateur Faust non trouvé"
    echo "Veuillez visiter https://faust.grame.fr pour installer Faust"
    exit 1
fi

# Répertoire de sortie
OUTPUT_DIR="../firmware/src/generated"
mkdir -p "$OUTPUT_DIR"

echo "Début de la compilation des fichiers Faust DSP..."

# Compiler le fichier DSP principal
echo "  - guitar_main.dsp → FaustDSP_generated.cpp"
faust -a minimal.cpp \
      -lang cpp \
      -cn GuitarDSP \
      guitar_main.dsp \
      -o "$OUTPUT_DIR/FaustDSP_generated.cpp"

# Vérifier le résultat de la compilation
if [ $? -eq 0 ]; then
    echo "✓ Compilation réussie !"
    echo "Fichier généré : $OUTPUT_DIR/FaustDSP_generated.cpp"
else
    echo "✗ Échec de la compilation"
    exit 1
fi

# Optionnel : générer des diagrammes (pour débogage)
# faust2svg guitar_main.dsp

echo "=== Build terminé ==="
