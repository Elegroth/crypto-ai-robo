# Market Memo Prompt

Summarize the current crypto market environment for BTC and large-cap alts.

## Requirements

- Focus on facts and cite sources in structured metadata.
- Produce one of: `risk_on`, `neutral`, `risk_off`.
- Return a bounded multiplier between `0.50` and `1.00`.
- Never suggest specific orders or asset weights.
- Default to `neutral` when confidence is low or sources conflict.
