#pragma once
#include <stdint.h>
#include <string.h>

// Fixed 5% setpoint; gain (ppm/ms) is learned, not a regulator pressure setting.
// Field fit: about 54 s transport + 4 s mixing. Retain commands for 60 s.
// Timing and the 500 ppm/ms calibration bound are operating assumptions, not
// guarantees for arbitrary plumbing, pressure changes or a stuck valve.
struct Co2DoseModel {
  struct Shot {
    uint32_t at;
    uint16_t ms;
  } shots[4];
  int32_t mass; // Concentration change + estimated leakage in this window.
  int16_t bias; // Bounded integral correction for steady concentration error.
  uint32_t tickAt, sendAt, windowAt;
  uint16_t lastPpm, input, gain, referenceMs, startPpm;
  uint16_t zeroMs; // Isolated failed probes establish opening overhead only before success.
  uint8_t lossAt50; // ppm/s at 50,000 ppm; learned before the first dose.
  bool seen, previousValid, hasSent, trained, floorLearned;

  Co2DoseModel(int32_t = 50000, uint16_t = 1000) {
    memset(this, 0, sizeof(*this));
    reset();
  }

  // Keep gas already commanded after a sensor gap or re-enable.
  __attribute__((noinline,noclone)) void reset(bool preserve = false) {
    if (!preserve) {
      memset(shots, 0, sizeof(shots));
      seen = hasSent = false;
      lossAt50 = 20;
    }
    gain = 150;
    bias = mass = 0;
    input = 0;
    trained = false;
    referenceMs = 5;
    zeroMs = 0;
    floorLearned = false;
    previousValid = false;
    windowAt = tickAt;
  }

  uint16_t loss(uint16_t ppm) const {
    return (uint32_t)(ppm > 400 ? ppm - 400 : 0) * lossAt50 / 50000UL;
  }

  uint32_t inventory() const {
    uint32_t p = 0;
    for (uint8_t j = 0; j < 4; j++) p += (uint32_t)(shots[j].ms > zeroMs ? shots[j].ms - zeroMs : 0) * gain;
    return p;
  }

  __attribute__((noinline,noclone)) int32_t projection(uint32_t) const {
    return (int32_t)lastPpm + inventory() - (uint32_t)loss(lastPpm) * 50;
  }

  __attribute__((noinline,noclone)) void update(uint32_t now, int32_t ppm,
                                               bool valid, bool learn = true) {
    if (!seen) {
      seen = true;
      tickAt = windowAt = now;
      startPpm = lastPpm = ppm;
      previousValid = valid;
      return;
    }
    uint32_t elapsed = now - tickAt;
    tickAt = now;
    uint8_t dt = elapsed / 1000;
    for (uint8_t j = 0; j < 4; j++) {
      if (shots[j].ms && now - shots[j].at >= 60000UL) {
        input += shots[j].ms > zeroMs ? shots[j].ms - zeroMs : 0;
        shots[j].ms = 0;
      }
    }
    if (valid && previousValid && learn && elapsed <= 10000UL) {
      mass += ppm - lastPpm + (uint32_t)loss((ppm + lastPpm) / 2) * dt;
      // A delayed response cannot be assigned just to the latest 20 s pulse.
      if (now - windowAt >= 100000UL) {
        if (!hasSent && startPpm > ppm && ppm > 1000) {
          uint32_t l = (uint32_t)(startPpm - ppm) * 500 /
                       (((uint32_t)startPpm + ppm) / 2 - 400);
          if (l > 0 && l < 100) lossAt50 = l;
        }
        if (input >= 5 && mass >= (int32_t)input * 5) {
          int32_t g = mass / input;
          if (g > 500) g = 500;
          gain = g > gain ? g : (gain + g) / 2;
          trained = floorLearned = true;
        }
        if (input >= 5 && mass < (int32_t)input * 5) {
          // A later empty cylinder/contact loss must not invent mechanical overhead.
          if (!floorLearned && referenceMs < 100) zeroMs = referenceMs;
          if (referenceMs < 100) referenceMs += 5;
          trained = false;
          bias = 0;
        }
        mass = 0;
        input = 0;
        windowAt = now;
      }
      if (trained) {
        int32_t e = 50000L - ppm;
        if (e > -3000 && e < 3000) {
          int32_t b = bias + e * dt / 1024;
          if (b < -2000) b = -2000;
          if (b > 2000) b = 2000;
          bias = b;
        }
      }
    } else {
      mass = 0;
      input = 0;
      windowAt = now;
    }
    if (valid && ppm > 53000) {
      zeroMs = 0;
      floorLearned = false;
    }
    previousValid = valid;
    if (valid) lastPpm = ppm;
  }

  bool ready(uint32_t now) const {
    return !hasSent || now - sendAt >= (trained ? 20000UL : 100000UL);
  }

  __attribute__((noinline,noclone)) uint16_t pulse(uint32_t now) const {
    if (!previousValid || !ready(now) || lastPpm >= 51000) return 0;
    if (!trained) {
      uint16_t safe = (57000UL - lastPpm) / 500;
      uint16_t p = referenceMs < safe ? referenceMs : safe;
      return lastPpm < 49500 && p >= 5 ? p : 0;
    }
    int32_t p = ((int32_t)loss(lastPpm) * 20 +
                 (50000L - projection(now)) / 2 + bias) / (int32_t)gain;
    if (p <= 0) return 0;
    p += zeroMs;
    // Limit growth from the last opening and estimated gas per command.
    uint16_t cap = referenceMs + referenceMs / 4 + 5;
    uint16_t quantity = (lastPpm > 40000 ? 1000 : 5000) / gain;
    if (quantity < 5) quantity = 5;
    quantity += zeroMs;
    if (cap > quantity) cap = quantity;
    if (p > cap) p = cap;
    if (p > 1000) p = 1000;
    return p >= 5 ? p : 0;
  }

  __attribute__((noinline,noclone)) void record(uint16_t ms, uint32_t now) {
    // Automatic spacing needs at most three slots; merge surplus manual shots
    // conservatively into the last slot instead of silently losing gas history.
    for (uint8_t j = 0; j < 4; j++) {
      if (!shots[j].ms || j == 3) {
        shots[j].ms += ms;
        shots[j].at = now;
        break;
      }
    }
    // Start a calibration window at its probe, including after a door pause.
    if (!trained) {
      windowAt = now;
      mass = 0;
      input = 0;
    }
    referenceMs = ms;
    sendAt = now;
    hasSent = true;
  }
};
