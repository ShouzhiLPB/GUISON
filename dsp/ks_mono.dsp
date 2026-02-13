import("stdfaust.lib");

// --------------------
// Parameters
// --------------------

midiNote = hslider("note", 60, 0, 127, 1);
freq = ba.midikey2hz(midiNote);

velocity = hslider("velocity", 100, 0, 127, 1);
velNorm  = velocity / 127.0;

gate = button("gate");

t60 = hslider("t60", 3, 0.1, 10, 0.1);

rawAtt = pow(0.001, 1.0/(freq*t60));
att = min(rawAtt, 0.999);

// --------------------
// Envelope
// --------------------

env = gate : en.adsr(0.001, 0.01, 0, 0.3);

// --------------------
// Excitation
// --------------------

excitation =
    (no.noise : fi.lowpass(1, 2000 + 6000 * velNorm))
    * env
    * velNorm;

// --------------------
// Karplus–Strong
// --------------------

delaySamples = ma.SR / freq;

oneZero(x) = (x + x') * 0.5;

string =
    excitation
    + (oneZero : *(att) : de.fdelay(4096, delaySamples))
    ~ _;

left = string;
right = string : @(8) : fi.lowpass(1, 3000);
// --------------------
// Output
// --------------------

process =  left, right;