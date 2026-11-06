#pragma once
#include <stdint.h>

// Measured1..5-stair proportion; falling/flat below target permits the next dose.
struct Co2DoseModel {
  uint32_t referenceMs = 20;
  uint32_t referenceRise = 0;
  struct Step { uint32_t ms; uint16_t rise; } steps[5] = {};
  uint8_t stepCount = 0, stepHead = 0;
  uint32_t responseMs = 20000;
  uint32_t lastMs = 0;
  uint16_t lastProbeMs = 0;
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
    if (!valid || !learn) { previousValid = false; falling = flat = 0; return; }
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
      if ((falling >= 2 || flat >= 2) && mass >= 200 && now - sendAt >= 20000UL) {
        int32_t delivered = mass + lossPpmPerSec * ((peakAt - valleyAt) / 1000.0f);
        // Only useful rises enter the history. In particular, the recorded
        // 69ppm fluctuation must not replace a response of several thousand ppm.
        if (!stepCount) { referenceMs = 0; referenceRise = 0; }
        Step &slot = steps[stepHead];
        referenceMs -= slot.ms;
        referenceRise -= slot.rise;
        slot.ms = lastMs;
        slot.rise = delivered > 65535L ? 65535 : delivered;
        referenceMs += slot.ms;
        referenceRise += slot.rise;
        if (++stepHead == 5) stepHead = 0;
        if (stepCount < 5) stepCount++;
        responseMs = peakAt - sendAt;
        if ((int32_t)responseMs < 20000) responseMs = 20000;
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
    int32_t needed = 50000L - lastPpm + lossPpmPerSec * (responseMs / 1000.0f);
    if (needed <= 0) return 0;
    uint32_t duration;
    if (trained && referenceRise) {
      // Average gain = sum(useful ppm) / sum(opening ms), using only the
      // available1..5 stairs. No five-sample wait and no percentage growth cap.
      uint64_t calculated = ((uint64_t)referenceMs * needed + referenceRise - 1) / referenceRise;
      duration = calculated > 1000 ? 1000 : calculated;
    } else {
      duration = lastProbeMs + 20UL; // User-requested calibration:20,40,60,80,... until measured gain.
    }
    if (duration > 1000) duration = 1000;
    if (duration < 5) duration = 5;
    return duration;
  }

  __attribute__((noinline,noclone)) void record(uint16_t ms, uint32_t now) {
    lastProbeMs = ms;
    if (observing) lastMs += ms;
    else {
      lastMs = ms;
      valley = peak = lastPpm; valleyAt = peakAt = now;
      mass = 0;
    }
    falling = flat = 0;
    sendAt = now;
    hasSent = true;
    observing = true;
  }

  // Kept for the legacy CSV column: -1 explicitly means no forecast is used.
  int32_t projection(uint32_t) const { return -1; }
};
