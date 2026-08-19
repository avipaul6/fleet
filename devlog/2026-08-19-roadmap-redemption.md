# Roadmap idea — redemption-side ("where can my points take me?")

**Status:** v2 / post-hackathon. Deliberately OUT of the hackathon scope.

## The idea
Complement DuckFleet's *earn* side (hunt cheap points-earning errands) with a *redemption*
side: given the household's accumulated points, surface the best award flights / destinations
— in the spirit of seats.aero, pointspath.com, flightlegroom.com (award search + a Google
Flights overlay via Chrome extension).

## Why NOT now (recorded so we don't re-litigate)
- **Locked out-of-scope** (CLAUDE.md): "any automated purchasing or points-**redemption**
  booking"; "more than ~3 scouts."
- **North-star trap:** a redemption subsystem is exactly the product-scope creep that would
  eat the ~12 days that belong to shipping the governed-earn narrative by Aug 31.
- **Breaks scouting principles:** award availability needs either brittle airline-inventory
  scraping (ToS-sensitive) or a **paid** API (e.g. seats.aero) — against "read-only stable
  feeds" and "$0 to the author."
- **Crowded space / narrative dilution:** seats.aero already owns award search; DuckFleet's
  novelty is governed earn + errand-worth-it + gated actions. Adding "where can I fly" makes
  the 3-minute demo crowded.
- (Tell: seats.aero literally showed up in a live scout pull as a `no_points_angle` row.)

## Cheap "taste" we CAN do now (optional, on-narrative)
The valuer already carries `REDEMPTION_VALUE_CPP` (Qantas pt ≈ 1.8c). The presenter can add
one *illustrative* line per hero stack — e.g. "16,800 Qantas pts ≈ ~$300 value, roughly a
one-way SYD–MEL economy seat" — using static benchmarks, no live search, no cost. Flourish,
not a feature.

## If/when built (v2 notes)
- Fits the post-hackathon **managed-agent product** ("earn + redeem, governed").
- Keep it read-only; never wire actual booking. BYO airline-program data / paid API stays on
  the user's side to preserve the $0-to-author cost boundary.
