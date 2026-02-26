#include <Audio.h>
#include "ks_mono.h"


// CONF
#define NUM_CHORDS 7
#define VOICES_PER_CHORD 3

// PINS
#define VOL_PIN A8
#define T60_PIN A0
#define STRUM_PIN A3
#define MODE_PIN 16

int buttonPins[NUM_CHORDS] = { 0, 1, 2, 3, 4, 5, 9 };

// SCALES

int majorScale[7] = {0,2,4,5,7,9,11};
int minorScale[7] = {0,2,3,5,7,8,10};

// STATE

int root = 0;
bool isMajor = true;

int strumDelay = 20;
ks_mono voices[VOICES_PER_CHORD];

unsigned long chordStartTime = 0;
int activeChord = -1;
bool chordPlaying = false;
bool noteTriggered[VOICES_PER_CHORD] = { false };

AudioMixer4 mixer;
AudioOutputI2S out;
AudioControlSGTL5000 audioShield;
AudioEffectDelay delayR;

// Audio connections
AudioConnection* patchCords[VOICES_PER_CHORD];
AudioConnection* patchOutL;
AudioConnection* patchOutR;
AudioConnection* patchDelay;


bool lastState[NUM_CHORDS] = { false };

void setup() {
    // Init pins
    for (int i = 0; i < NUM_CHORDS; i++) {
        pinMode(buttonPins[i], INPUT);
    }
    pinMode(MODE_PIN, INPUT);

    // init audio
    AudioMemory(80);
    audioShield.enable();
    audioShield.volume(0.5);

    // connect voices to mixer
    for (int i = 0; i < VOICES_PER_CHORD; i++) {
        patchCords[i] = new AudioConnection(voices[i], 0, mixer, i);
        mixer.gain(i, 0.25);
    }

    // mixer → stereo out
    patchDelay = new AudioConnection(mixer, 0, delayR, 0);
    patchOutL = new AudioConnection(mixer, 0, out, 0);
    patchOutR = new AudioConnection(delayR, 0, out, 1);
    delayR.delay(0, 5);
    randomSeed(analogRead(A0));
    Serial.begin(1000000);
}


void loop() {

    bool shift = digitalRead(MODE_PIN);
    float vol_value = floorf(analogRead(VOL_PIN) / 1023.0f * 100.0f) / 100.0f;
    float t60_value = 10.0f + (analogRead(T60_PIN) / 1023.0f) * 91.0f;
    float strumPot = analogRead(STRUM_PIN) / 1023.0f;
    int baseStrum = 10 + pow(strumPot, 2) * 150; // baseStrum changes between 10ms and 150ms.

    for (int i = 0; i < NUM_CHORDS; i++) {

        bool pressed = digitalRead(buttonPins[i]);

        if (pressed && !lastState[i]) {
            if (shift) {
                if (i == 0) {
                    root = (root + 5) % 12;
                    Serial.printf("Key changed: %d\n", root);
                }
                else if (i == 1) {
                    root = (root + 7) % 12;
                    Serial.printf("Key changed: %d\n", root);
                }
                else if (i == 2) {
                    isMajor = !isMajor;
                    Serial.println(isMajor ? "Major" : "Minor");
                }
            } else {
                for (int v = 0; v < VOICES_PER_CHORD; v++) {
                    voices[v].setParamValue("gate", 0);
                    voices[v].setParamValue("t60", t60_value);
                    mixer.gain(v, vol_value);
                    noteTriggered[v] = false;
                }

                chordStartTime = millis();
                activeChord = i;
                chordPlaying = true;

                strumDelay = baseStrum + random(0, 20);
            }
        }

        if (!pressed && lastState[i] && i == activeChord && !shift) {

            for (int v = 0; v < VOICES_PER_CHORD; v++) {
                voices[v].setParamValue("gate", 0);
            }
            chordPlaying = false;
            activeChord = -1;
        }

        lastState[i] = pressed;
    }

    if (chordPlaying && activeChord >= 0 && !shift) {

        int* scale = isMajor ? majorScale : minorScale;
        int degree = activeChord;

        float freqArray[VOICES_PER_CHORD];
        int noteValues[VOICES_PER_CHORD];

        for (int v = 0; v < VOICES_PER_CHORD; v++) {
            int noteIndex = (degree + 2*v) % 7;
            int noteValue = 60 + root + scale[noteIndex] + ((degree + 2*v) / 7) * 12;
            noteValues[v] = noteValue;
            freqArray[v] = (float)(440.0 * pow(2.0, (noteValue - 69) / 12.0));
        }

        unsigned long now = millis();
        unsigned long dt = now - chordStartTime;

        for (int v = 0; v < VOICES_PER_CHORD; v++) {

            if (!noteTriggered[v] && dt > (unsigned long)(v * strumDelay)) {  // un ecart entre chaque note

                if (v == 0) {
                    Serial.printf("%.2f;%.2f;%.2f\n",
                        freqArray[0],
                        freqArray[1],
                        freqArray[2]);
                }

                voices[v].setParamValue("note", noteValues[v]);
                voices[v].setParamValue("gate", 1);
                noteTriggered[v] = true;
            }
        }
    }
}
