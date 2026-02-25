#include <Audio.h>
#include "ks_mono.h"

#define NUM_CHORDS 7
#define VOICES_PER_CHORD 3

#define VOL_PIN A8
#define T60_PIN A0

#define KEY_NEXT_PIN 16
#define KEY_PREV_PIN 17
#define MODE_PIN 18

int buttonPins[NUM_CHORDS] = { 0, 1, 2, 3, 4, 5, 9 };


// C4 Major chords scale
// int chordNotes[NUM_CHORDS][VOICES_PER_CHORD] = {
//   { 60, 64, 67 },  // C major : I
//   { 62, 65, 69 },  // D minor : ii
//   { 64, 67, 71 },  // E minor : iii
//   { 65, 69, 72 },  // F major : IV
//   { 67, 71, 74 },  // G major : V
//   { 69, 72, 76 },  // A minor : vi
//   { 71, 74, 77 }   // B diminished : vii°
// };
int majorScale[7] = {0,2,4,5,7,9,11};
int minorScale[7] = {0,2,3,5,7,8,10};

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
AudioConnection* patchQueueL;
AudioConnection* patchQueueR;
AudioConnection* patchDelay;


bool lastState[NUM_CHORDS] = { false };

// void MidiToFreq(int notes[], float freqArray[]) {
//   for (int i = 0; i < VOICES_PER_CHORD; i++) {
//     freqArray[i] = (float)(440.0 * pow(2.0, (notes[i] - 69) / 12.0));
//   }
// }

void setup() {

  for (int i = 0; i < NUM_CHORDS; i++) {
    pinMode(buttonPins[i], INPUT);
  }

  pinMode(KEY_NEXT_PIN, INPUT);
  pinMode(KEY_PREV_PIN, INPUT);
  pinMode(MODE_PIN, INPUT);

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
  static bool lastNext = false;
  static bool lastPrev = false;
  static bool lastMode = false;

  bool nextPressed = digitalRead(KEY_NEXT_PIN);
  bool prevPressed = digitalRead(KEY_PREV_PIN);
  bool modePressed = digitalRead(MODE_PIN);

  if (nextPressed && !lastNext) {
    root = (root + 7) % 12;
  }

  if (prevPressed && !lastPrev) {
    root = (root + 5) % 12;
  }

  if (modePressed && !lastMode) {
	isMajor = !isMajor;
  }

  lastNext = nextPressed;
  lastPrev = prevPressed;
  lastMode = modePressed;

  float vol_value = floorf(analogRead(VOL_PIN) / 1023.0f * 100.0f) / 100.0f;
  float t60_value = 10.0f + (analogRead(T60_PIN) / 1023.0f) * 91.0f;
  // Serial.printf("%.3f\n", t60_value);

  for (int i = 0; i < NUM_CHORDS; i++) {

    bool pressed = digitalRead(buttonPins[i]);

    if (pressed && !lastState[i]) {

      for (int v = 0; v < VOICES_PER_CHORD; v++) {
        voices[v].setParamValue("gate", 0);
        voices[v].setParamValue("t60", t60_value);
        mixer.gain(v, vol_value);
        noteTriggered[v] = false;
      }

      chordStartTime = millis();
      activeChord = i;
      chordPlaying = true;

      strumDelay = 30 + random(0, 10);
    }

    if (!pressed && lastState[i] && i == activeChord) {

      for (int v = 0; v < VOICES_PER_CHORD; v++) {
        voices[v].setParamValue("gate", 0);
      }
      chordPlaying = false;
      activeChord = -1;
    }

    lastState[i] = pressed;
  }

  if (chordPlaying && activeChord >= 0) {

	int* scale = isMajor ? majorScale : minorScale;
	int degree = activeChord;

    float freqArray[VOICES_PER_CHORD];
	int noteValues[VOICES_PER_CHORD];

	for (int v = 0; v < VOICES_PER_CHORD; v++) {
		int noteIndex = (degree + 2*v) % 7;
		int noteValue = 60 + root + scale[noteIndex];
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
