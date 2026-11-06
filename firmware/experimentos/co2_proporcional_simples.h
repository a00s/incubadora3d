#pragma once
#include <stdint.h>
// Measured stairs, matched to queued commands before calculating the next dose.
// No fixed observation pause: expected gas still in transit reduces the deficit.
// Measured1..5-stair proportion; falling/flat below target permits the next dose.
struct Co2DoseModel {
  enum { MAX_PULSE_MS = 100 };
  uint16_t referenceMs = 20;
  uint32_t referenceRise = 0;
  struct Step { uint16_t ms; uint16_t rise; } steps[5] = {};
  uint8_t stepCount = 0, stepHead = 0;
  uint32_t responseMs = 20000;
  uint16_t lastMs = 0;
  uint32_t arrivalMs = 0;
  struct Pending { uint32_t at; uint8_t ms; bool learned; } pending[5] = {};
  uint8_t pendingHead = 0;
  uint8_t lastProbeMs = 0;
  int32_t lastPpm = 0, valley = 0, peak = 0, mass = 0;
  uint32_t sendAt = 0, lastAt = 0, valleyAt = 0, peakAt = 0, firstFallAt = 0;
  uint8_t flat = 0;
  uint8_t falling = 0;
  bool previousValid = false, hasSent = false, trained = false, observing = false;

  __attribute__((noinline,noclone)) void reset(bool preserve = false) {
    if (preserve) {
      previousValid = false; falling = flat = 0;
      observing = false; valley = peak = mass = 0;
      for (uint8_t i = 0; i < 5; ++i) pending[i] = Pending();
      pendingHead = 0;
    } else *this = Co2DoseModel();
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

    } else { falling = flat = 0; }
    if (observing) {
      // The gas can arrive after a continuing decline. Measure the observed
      // rise from its actual valley, even if the peak stays below command ppm.
      if (ppm < valley) { valley = peak = ppm; valleyAt = peakAt = now; }
      if (ppm > peak) { peak = ppm; peakAt = now; }
      mass = peak - valley;
      if ((falling >= 2 || flat >= 2) && mass >= 200 && now - sendAt >= 20000UL) {
        int32_t delivered = mass; // Match the observed stair to the oldest unanswered opening.
        uint8_t owner = 5;
        uint32_t oldestAge = 0;
        for (uint8_t i = 0; i < 5; ++i) {
          uint32_t age = now - pending[i].at;
          if (pending[i].ms && !pending[i].learned && (owner == 5 || age > oldestAge)) {
            owner = i; oldestAge = age;
          }
        }
        if (owner == 5) { observing = false; return; }
        // Only useful rises enter the history. In particular, the recorded
        // 69ppm fluctuation must not replace a response of several thousand ppm.
        if (!stepCount) { referenceMs = 0; referenceRise = 0; }
        Step &slot = steps[stepHead];
        referenceMs -= slot.ms;
        referenceRise -= slot.rise;
        uint16_t deliveredMs = 0;
        uint32_t newestAt = pending[owner].at;
        uint32_t observedArrival = trained ? arrivalMs : valleyAt - pending[owner].at;
        for (uint8_t i = 0; i < 5; ++i) {
          if (pending[i].ms && !pending[i].learned && (int32_t)(peakAt - pending[i].at) >= (int32_t)observedArrival) {
            deliveredMs += pending[i].ms;
            if (now - pending[i].at < now - newestAt) newestAt = pending[i].at;
            pending[i].learned = true;
          }
        }
        if (!deliveredMs) deliveredMs = pending[owner].ms;
        slot.ms = deliveredMs;
        slot.rise = delivered > 65535L ? 65535 : delivered;
        referenceMs += slot.ms;
        referenceRise += slot.rise;
        if (++stepHead == 5) stepHead = 0;
        if (stepCount < 5) stepCount++;
        if (!trained) {
          arrivalMs = valleyAt - pending[owner].at;
          responseMs = peakAt - newestAt;
          if (arrivalMs >= responseMs) arrivalMs = responseMs / 2;
        }
        pending[owner].learned = true;
        if ((int32_t)responseMs < 20000) responseMs = 20000;
        trained = true;
        observing = false;
        for (uint8_t i = 0; i < 5; ++i) if (pending[i].ms && !pending[i].learned) observing = true;
        valley = peak = ppm; valleyAt = peakAt = now; mass = 0;
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
    int32_t needed = 50000L - lastPpm;
    if (trained && referenceRise && referenceMs) {
      uint16_t totalMs = 0;
      uint32_t oldest = 20000;
      for (uint8_t i = 0; i < 5; ++i) if (pending[i].ms) {
        totalMs += pending[i].ms;
        uint32_t age = now - pending[i].at;
        if (age > oldest) oldest = age;
      }
      uint32_t maintenanceMs = totalMs * 20000UL / oldest;
      int32_t maintenance = maintenanceMs * referenceRise / referenceMs;
      if (maintenance > 1000) maintenance = 1000;
      needed += maintenance;
    }
    if (trained && referenceRise) {
      uint16_t remainingMs = 0;
      for (uint8_t i = 0; i < 5; ++i) {
        uint32_t age = now - pending[i].at;
        if (pending[i].ms && age < responseMs) {
          if (age <= arrivalMs) remainingMs += pending[i].ms;
          else remainingMs += ((uint32_t)pending[i].ms * (responseMs - age) + (responseMs - arrivalMs) - 1) / (responseMs - arrivalMs);
        }
      }
      needed -= (int32_t)((uint32_t)remainingMs * referenceRise / referenceMs);
    }
    if (needed <= 0) return 0;
    uint32_t duration;
    if (trained && referenceRise) {
      // Average gain = sum(useful ppm) / sum(opening ms), using only the
      // available1..5 stairs. No five-sample wait and no percentage growth cap.
      // referenceMs <=2500 and positive needed <=51000: product fits uint32_t.
      uint32_t calculated = (referenceMs * (uint32_t)needed + referenceRise - 1) / referenceRise;
      duration = calculated > MAX_PULSE_MS ? (uint32_t)MAX_PULSE_MS : calculated;
    } else {
      duration = lastProbeMs + 20UL; // User-requested calibration:20,40,60,80,... until measured gain.
    }
    uint32_t nextMaximum = lastProbeMs ? (uint32_t)lastProbeMs + 20 : 20;
    if (duration > nextMaximum) duration = nextMaximum;
    if (duration > MAX_PULSE_MS) duration = MAX_PULSE_MS;
    if (duration < 5) duration = 5;
    return duration;
  }

  __attribute__((noinline,noclone)) void record(uint16_t ms, uint32_t now) {
    pending[pendingHead].at = now;
    pending[pendingHead].ms = ms;
    pending[pendingHead].learned = false;
    if (++pendingHead == 5) pendingHead = 0;
    lastProbeMs = ms;
    lastMs = ms;
    if (!observing) {
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
