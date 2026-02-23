#include <Audio.h>
#include "ks_mono.h"

#define NUM_CHORDS 4
#define VOICES_PER_CHORD 3

int buttonPins[NUM_CHORDS] = {2,3,4,5};

int chordNotes[NUM_CHORDS][VOICES_PER_CHORD] = {
  {60, 64, 67},  // C
  {62, 65, 69},  // Dm
  {64, 67, 71},  // Em
  {65, 69, 72}   // F
};

int strumDelay = 20;

ks_mono voices[VOICES_PER_CHORD];

unsigned long chordStartTime = 0;
int activeChord = -1;
bool chordPlaying = false;
bool noteTriggered[VOICES_PER_CHORD] = {false};

AudioMixer4 mixer;
AudioOutputI2S out;
AudioControlSGTL5000 audioShield;
AudioRecordQueue queueL;
AudioRecordQueue queueR;
AudioEffectDelay delayR;

// Audio connections
AudioConnection* patchCords[VOICES_PER_CHORD];
AudioConnection* patchOutL;
AudioConnection* patchOutR;
AudioConnection* patchQueueL;
AudioConnection* patchQueueR;
AudioConnection* patchDelay;


bool lastState[NUM_CHORDS] = {false};

void setup() {

  for (int i = 0; i < NUM_CHORDS; i++) {
    pinMode(buttonPins[i], INPUT_PULLUP);
  }

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

  patchQueueL = new AudioConnection(mixer, 0, queueL, 0);
  patchQueueR = new AudioConnection(delayR, 0, queueR, 0);

  delayR.delay(0, 5);
  randomSeed(analogRead(A0));

  queueL.begin();
  queueR.begin();
  Serial.begin(1000000);
}


void loop() {

  for (int i = 0; i < NUM_CHORDS; i++) {

    bool pressed = !digitalRead(buttonPins[i]);

    if (pressed && !lastState[i]) {

		for (int v = 0; v < VOICES_PER_CHORD; v++) {
            voices[v].setParamValue("gate", 0);
            noteTriggered[v] = false;
        }

		chordStartTime = millis();
		activeChord = i;
		chordPlaying = true;

		strumDelay = 10 + random(0,10);

        // for (int v = 0; v < VOICES_PER_CHORD; v++) {
		// 	noteTriggered[v] = false;
		// 	voices[v].setParamValue("gate", 0);
  		// }
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

	unsigned long now = millis();
	unsigned long dt = now - chordStartTime;

	for (int v = 0; v < VOICES_PER_CHORD; v++) {

		if (!noteTriggered[v] && dt > v * strumDelay) {   // un ecart entre chaque note

			voices[v].setParamValue("note", chordNotes[activeChord][v]);
			voices[v].setParamValue("gate", 1);
			noteTriggered[v] = true;
		}
	}

	// if (dt > VOICES_PER_CHORD * strumDelay) {
	// 	chordPlaying = false;
	// }
  }

  static int blockCounter = 0;

  while (queueL.available() && queueR.available()) {

    int16_t* bufferL = queueL.readBuffer();
    int16_t* bufferR = queueR.readBuffer();

	blockCounter++;

    if (blockCounter >= 4) {
      for (int i=0; i<128; i+=8) {
        //Serial.print(bufferL[i]);
        //Serial.print(", ");
        //Serial.println(bufferR[i]);
        Serial.write((uint8_t*)&bufferL[i], 2);
        Serial.write((uint8_t*)&bufferR[i], 2);
      }

      blockCounter = 0;
    }

    queueL.freeBuffer();
    queueR.freeBuffer();
}

  while (queueL.available() > 10) {
    queueL.freeBuffer();
  }
  while (queueR.available() > 10) {
    queueR.freeBuffer();
  }


}
