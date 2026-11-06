#pragma once
#include <stdint.h>

// Last useful dose and measured loss only. No pending-gas projection or integral correction.
struct Co2DoseModel {
  uint16_t referenceMs = 20;
  uint16_t referenceRise = 0;
  uint16_t lastMs = 0;
  int32_t lastPpm = 0, valley = 0, peak = 0, mass = 0;
  uint32_t sendAt = 0, lastAt = 0, valleyAt = 0, peakAt = 0, firstFallAt = 0;
  float lossPpmPerSec = 0;
  uint8_t flat = 0;
  uint8_t falling = 0;
  bool previousValid = false, hasSent = false, trained = false, observing = false;

  __attribute__((noinline,noclone)) void reset(bool preserve = false) {
    uint32_t oldAt = sendAt;
    bool sent = hasSent;
    float loss = lossPpmPerSec;
    *this = Co2DoseModel();
    if (preserve) { sendAt = oldAt; hasSent = sent; lossPpmPerSec = loss; }
  }

  __attribute__((noinline,noclone)) void update(uint32_t now, int32_t ppm, bool valid, bool learn = true) {
    if (!valid || !learn) { previousValid = false; falling = 0; return; }
    uint32_t elapsed = now - lastAt;
    if (previousValid && elapsed && elapsed <= 20000UL) {
      int32_t delta = ppm - lastPpm;
      if (delta < 0) {
        if (!falling || now - firstFallAt > 20000UL) { falling = 1; firstFallAt = now; }
        else if (falling < 2) falling++;
      } else falling = 0;
      if (delta * 1000L <= (int32_t)elapsed * 2 && delta * 1000L >= -(int32_t)elapsed * 2) { if (flat < 2) flat++; }
      else flat = 0;
      if (falling >= 2 && ppm >= 45000 && (!hasSent || now - sendAt >= 20000UL)) {
        float observed = (lastPpm - ppm) * 1000.0f / elapsed;
        if (observed <= 200) lossPpmPerSec = lossPpmPerSec > 0 ? lossPpmPerSec * .8f + observed * .2f : observed;
      }
    } else { falling = flat = 0; }
    if (observing) {
      // The gas can arrive after a continuing decline. Measure the observed
      // rise from its actual valley, even if the peak stays below command ppm.
      if (ppm < valley) { valley = peak = ppm; valleyAt = peakAt = now; }
      if (ppm > peak) { peak = ppm; peakAt = now; }
      mass = peak - valley;
      if ((falling >= 2 || flat >= 2) && mass >= 50 && now - sendAt >= 20000UL) {
        referenceMs = lastMs;
        int32_t delivered = mass + lossPpmPerSec * ((peakAt - valleyAt) / 1000.0f);
        referenceRise = delivered > 65535L ? 65535 : delivered;
        trained = true;
        observing = false;
      }
    }
    previousValid = true;
    lastPpm = ppm; lastAt = now;
  }

  bool ready(uint32_t now) const {
    bool plateau = flat >= 2 && lastPpm > 0;
    return previousValid && (falling >= 2 || plateau) && (!hasSent || now - sendAt >= 20000UL);
  }

  __attribute__((noinline,noclone)) uint16_t pulse(uint32_t now) const {
    if (!ready(now) || lastPpm >= 51000 || lastPpm <= 0) return 0;
    int32_t needed = 50000L - lastPpm + lossPpmPerSec * 20;
    if (needed <= 0) return 0;
    uint32_t duration;
    if (trained && referenceRise) {
      // Last opening * (remaining ppm + measured loss refill) / observed dose result.
      duration = ((uint32_t)referenceMs * needed + referenceRise - 1) / referenceRise;
    } else {
      // No useful response yet: increase the short probe gradually, without
      // inventing a gain or dividing by zero during initial chamber filling.
      duration = hasSent ? lastMs + (lastMs + 3) / 4 : 20;
      uint32_t safe = (57000L - lastPpm) / 500;
      if (safe > 100) safe = 100;
      if (duration > safe) duration = safe;
    }
    if (duration > 1000) duration = 1000;
    if (duration < 5) duration = 5;
    return duration;
  }

  __attribute__((noinline,noclone)) void record(uint16_t ms, uint32_t now) {
    lastMs = ms;
    valley = peak = lastPpm; valleyAt = peakAt = now;
    mass = 0;
    falling = flat = 0;
    sendAt = now;
    hasSent = true;
    observing = true;
  }

  // Kept for the legacy CSV column: -1 explicitly means no forecast is used.
  int32_t projection(uint32_t) const { return -1; }
};
