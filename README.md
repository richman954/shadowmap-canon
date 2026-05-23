# ShadowMap Canon

Repository scaffold for the ShadowMap canonical workspace: distilled canon files, local submodules, worked exemplars, and runnable tensor-message / loop-residual transfer tests.

## Kernel

```text
object -> shadow representation -> hidden invariant
```

Current promoted tensor-message form:

```text
object -> factor/tensor graph -> message fixed point -> loop residual -> hidden invariant
```

Operational compression:

```text
The message fixed point is the first shadow; the loop residual is the shadow-of-the-shadow.
```

## Repository layout

```text
docs/
  canon/             Master canon, REV_C merge files, source map, diff notes
  submodules/        Local reusable ShadowMap submodules
  exemplars/         Worked examples and transfer tests
  patches/           Canon patches and canon-hold notes
  update_actions/    Upload / replacement instructions
src/shadowmap/       Runnable factor-graph utilities
scripts/             Transfer-test runner
tests/               Unit tests
data/results/        Stored and regenerated result artifacts
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m unittest discover -s tests
python scripts/run_transfer_tests.py
```

## Current repo decision

A new repo is the clean path. Existing accessible repositories were not targeted because this project has its own canon, documentation, and testable code surface.

Suggested remote name:

```text
richman954/shadowmap-canon
```

After creating that empty repository on GitHub, push this scaffold:

```bash
git remote add origin git@github.com:richman954/shadowmap-canon.git
git branch -M main
git push -u origin main
```

HTTPS alternative:

```bash
git remote add origin https://github.com/richman954/shadowmap-canon.git
git branch -M main
git push -u origin main
```

## Notes

This scaffold does not include the large research PDF/ZIP/XLSX corpus. It preserves derived canon artifacts and runnable small-graph transfer tests. Add source artifacts later only under an explicit license and storage policy.

No open-source license has been selected yet; see `LICENSE_PENDING.md`.
