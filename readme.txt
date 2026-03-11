# DXF Tributary Processing (Local Only)

This repo now runs entirely on your workstation—no Flask server, Google Cloud deployment, or file uploads required. Everything expects a single DXF named `INPUT.DXF` that lives in the project root (next to `Makefile`).

## Preparing the input
1. Export or copy your DXF to the repository root.
2. Rename it to **`INPUT.DXF`** (the scripts and helpers look for that exact filename).
3. Run the pipeline. Both `make` and `run.sh` verify that the file exists before doing anything.

## Quick start

```bash
make setup          # create venv + install dependencies
source venv/bin/activate

# Option A: orchestrated via make
make

# Option B: equivalent shell script
./run.sh

# Remove intermediate CSV/outputs
make clean
```

> Tip: Running `make` now invokes the `deps` target first, which executes `pip install -r requirements.txt` so dependencies stay up to date automatically.

## What the pipeline does

The DXF is processed through three stages, mirroring the previous hosted workflow:

1. **extract_dxf_data.py** – Reads `INPUT.DXF`, pulls out point/boundary/label tables, and emits CSVs.
2. **panelize.py** – Previews the extracted CSVs and sets up panelization data.
3. **tributary.py** – Calculates tributary regions, writes `tributary_output_fixed.dxf`, and exports `column_load_takedown.xlsx` (requires `openpyxl`).

### Layers
- Input layers: `WALL` (cyan), `BOUNDARY` (blue), `COLUMNS/POINTS` (magenta).
- Output layers: `FLOOR_*_WALL_TRIBUTARY_*` (red), `FLOOR_*_TRIBUTARY_COL_*` (yellow), `FLOOR_*_LARGE_TRIBUTARY` (>30 SF, magenta), `FLOOR_*_AREA_LABELS` (green).

## Dependencies

Install everything with `pip install -r requirements.txt` (or let `make setup` handle it). Need to refresh packages without running the pipeline? Run `make deps`. The list is short:
- `ezdxf`
- `pandas`
- `numpy`
- `matplotlib`
- `shapely`
- `openpyxl` (needed for the Excel export)

If `openpyxl` is missing, the DXF processing still runs but the takedown spreadsheet will be skipped.

## Manual commands (when not using make/run.sh)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python3 extract_dxf_data.py
python3 panelize.py
python3 tributary.py
```

Each script runs locally against `INPUT.DXF` and the intermediate CSVs it produces—no background workers, uploads, or cloud infra involved anymore.
