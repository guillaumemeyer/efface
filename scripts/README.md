# Scripts

Thin command wrappers live here. The harness is importable as the `efface`
package; scripts exist only for cron-style or cluster entry points that need a
stable filename.

Live:

- `spike_mps.py` — Week 1 throughput and memory measurement.
- `calibrate_null.py` — fit the unwatermarked null for one generator row and
  write the fit with diagnostics. Feeds `efface score --null`.

Planned:

- `generate_corpus.py`
- `run_singles.py`
- `run_search.py`
- `build_tables.py`
