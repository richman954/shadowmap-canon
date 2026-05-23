# Repository rules for coding agents:

1. Do not alter ShadowMap canon semantics unless the issue explicitly asks for it.
2. Do not promote local submodules into master canon.
3. Do not add large PDFs, ZIPs, notebooks, XLSX files, or copyrighted source documents.
4. Do not invent citations.
5. Do not remove tests to make CI pass.
6. Prefer small PRs.
7. Every code change needs either a test or a clear explanation of why no test applies.
8. Generated outputs must go under data/results or artifacts.
9. Canon documents are knowledge artifacts, not scratchpads.
10. PR summaries must separate:
   - code changes
   - documentation changes
   - generated artifacts
   - files intentionally untouched

This follows the master canon’s interpretation rule: always separate what the authors say, what the data/model/code actually supports, what hidden structure is present, and what remains inference or analogy.
