#pragma once
#include <stdint.h>

// The last completed dose is the only dosing reference. No dose accumulation.
struct Co2DoseModel {
  uint16_t referenceMs = 80;
  uint16_t referenceRise = 0;
  bool trained = false;
  bool fresh = true;

  void reset() { *this = Co2DoseModel(); }

  void learn(uint16_t pulseMs, uint16_t risePpm) {
    referenceMs = pulseMs;
    referenceRise = risePpm;
    trained = risePpm >= 50;
    fresh = false;
  }

  uint16_t pulse(int32_t deficit, uint16_t limitMs) const {
    if (deficit <= 0) return 0;
    float calculated = referenceMs;
    if (!fresh) {
      calculated = trained ? referenceMs * ((float)deficit / referenceRise)
                           : referenceMs * 1.1f;
      // Limit upward extrapolation; a new cylinder can change the flow.
      float growthLimit = referenceMs * 1.1f;
      if (calculated > growthLimit) calculated = growthLimit;
    }
    // With no measured response, bound the next dose by the remaining deficit.
    uint16_t unknownLimit = deficit / 150;
    if (!fresh && unknownLimit < 80) unknownLimit = 80;
    if (!trained && calculated > unknownLimit) calculated = unknownLimit;
    if (calculated > limitMs) calculated = limitMs;
    if (calculated < 5) calculated = 5;
    return (uint16_t)(calculated + 0.999f);
  }
};
