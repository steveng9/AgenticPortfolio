---
name: explain
description: Explain a finance or investing concept at an age-appropriate level. Usage: /explain [concept] [age]. Age defaults to 18 if not provided.
argument-hint: CONCEPT [AGE]
allowed-tools: WebSearch
---

# Task

Explain this finance or investing concept: **$0**

Target audience age: **$1** (default: 18 if not specified)

---

# Instructions

Calibrate every aspect of your explanation to the target age:
- **Age 10–14**: Analogies only from everyday life (lunch money, toys, sports). No jargon.
- **Age 15–18**: Light jargon is okay if immediately defined. Use relatable examples (first job, saving up for something).
- **Age 20–25**: Can handle more terminology. Use real-world examples from early career and personal finance.
- **Age 30+**: Assume basic financial literacy. Focus on nuance, tradeoffs, and practical application.

**Always be factual.** Base explanations on how concepts actually work — reference real market mechanics, regulatory context, or historical examples where relevant. Do not simplify to the point of being wrong.

---

# Output format

Keep it tight and visual. Use:
- A plain-English **one-sentence definition** up front
- A **real-world analogy** matched to the target age
- A **how it actually works** section (brief, factual)
- A **why it matters** section (practical relevance)
- A **key numbers or facts** table where applicable
- A **common misconception** if there's a prevalent one worth correcting

Do not pad. If the concept is simple, a short answer is the right answer.
