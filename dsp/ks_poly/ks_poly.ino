#include <Audio.h>
#include "ks_mono.h"

#define NUM_KEYS 3

int buttonPins[NUM_KEYS] = {1,2,3};

int notes[NUM_KEYS] = {60, 64, 67};

ks_mono voices[NUM_KEYS];

AudioMixer4 mixer;
AudioOutputI2S out;
AudioControlSGTL5000 audioShield;

// Audio connections
AudioConnection* patchCords[NUM_KEYS];
AudioConnection* patchOutL;
AudioConnection* patchOutR;

bool lastState[NUM_KEYS] = {false};

void setup() {

  for (int i = 0; i < NUM_KEYS; i++) {
    pinMode(buttonPins[i], INPUT_PULLUP);
  }

  AudioMemory(50);

  audioShield.enable();
  audioShield.volume(0.5);

  // connect voices to mixer
  for (int i = 0; i < NUM_KEYS; i++) {
    patchCords[i] = new AudioConnection(voices[i], 0, mixer, i);
    mixer.gain(i, 0.3);   // 防止爆音
  }

  // mixer → stereo out
  patchOutL = new AudioConnection(mixer, 0, out, 0);
  patchOutR = new AudioConnection(mixer, 0, out, 1);
}


void loop() {

  for (int i = 0; i < NUM_KEYS; i++) {

    bool pressed = !digitalRead(buttonPins[i]);

    if (pressed && !lastState[i]) {
        voices[i].setParamValue("note", notes[i]);
        voices[i].setParamValue("gate", 1);
    }

    if (!pressed && lastState[i]) {
        voices[i].setParamValue("gate", 0);
    }

    lastState[i] = pressed;
  }

  delay(2);
}
