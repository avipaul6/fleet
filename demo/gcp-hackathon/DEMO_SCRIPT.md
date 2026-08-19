# 3-Minute Demo Beat Sheet

Judges triage fast. One idea per beat, biggest moment at ~1:50, end on numbers.

**0:00–0:20 — Cold open (the duck).**
Photo of the BigW rubber duck. VO: "In 2025 this $3.50 bath toy earned Qantas
Points at half a cent each — bought in bulk, it was a business-class seat. The
only people who caught it were refreshing forums at midnight. I built a fleet
of agents that hunts the next duck while I sleep."

**0:20–0:45 — The fleet, at night.**
Architecture diagram animates: Scheduler fires 2am → scouts fan out (show real
Cloud Run logs scrolling) → "overnight: 1,400 offers ingested into BigQuery,
37 candidate stacks found." Screen-record the actual BigQuery table.

**0:45–1:15 — The brain.**
Valuer output on screen: one real stack, the math visible — price × multipliers
→ cents/point → net $. Then the ToS gate: a grey-area coupon exploit appears
and gets flagged-not-actioned. VO: "It hunts hard, inside the lines."

**1:15–1:40 — The refusal (governance as delight).**
Worth-It agent on a real map: two stores with stock. Store B: "22 min each
way — trip costs $28, Ooshie's worth $6. SKIP." VO: "Last month my family
drove to three shops for a stockout. The fleet just refuses bad errands."

**1:40–2:20 — THE MOMENT: the gated call.**
Approval request pops on phone → tap approve → agent dials the real store →
plays actual audio: "Hi, I'm an AI assistant calling on behalf of a customer —
quick stock question…" → store answers → transcript lands in the brief.
(One clean take. Get the store's okay beforehand; film the approval tap.)

**2:20–2:45 — Morning brief.**
The Gmail brief: 5 ranked actions, net dollars, one refused errand with its
reason, audit-log link. "This is what I wake up to."

**2:45–3:00 — Close on numbers + stack.**
"Built solo on ADK: six agents, Gemini 3.5 both tiers, Cloud Run, Pub/Sub,
Firestore, BigQuery, Routes API, phone gateway. Model-swappable per agent via
Vertex Model Garden. Every action gated, logged, human-approved. The next
duck won't get past it."
