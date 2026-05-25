# ShadowMap Exemplar: AlphaProof Nexus Formal Search

## What AlphaProof Nexus Authors Claim
AlphaProof Nexus claims to solve complex formal verification and proof generation tasks by employing deep reinforcement learning and large language models, specifically leveraging tools like Lean for formal verification.

## What the Results Repo Actually Contains
The AlphaProof Nexus results repository does not contain the full agent implementation, environment definitions, or trained model weights. It contains mechanically formalized Lean proof outputs and selected natural-language proof writeups.

## What ShadowMap is Borrowing Structurally
ShadowMap borrows the structural workflow of formal proof search:
`object -> formal sketch -> constrained search -> validator -> survivor proof`.
We adopt this schema to formally record and structure proof attempts without vendoring the entire framework or underlying dependencies.

## What Remains Future Work
Future work may involve integrating an actual validation engine like Lean directly into the ShadowMap CI pipeline to automatically verify these schemas and proofs, but currently, they remain static structured records.
