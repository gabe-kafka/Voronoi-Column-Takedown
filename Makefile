.PHONY: all setup clean verify-input deps

PYTHON ?= python3
PIP ?= $(PYTHON) -m pip

INPUT_FILE := INPUT.DXF

all: deps verify-input
	$(PYTHON) extract_dxf_data.py
	$(PYTHON) panelize.py
	$(PYTHON) tributary.py
	@echo "✓ Processing complete! Outputs: tributary_output_fixed.dxf, column_load_takedown.xlsx"

setup:
	$(PYTHON) -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	@echo "✓ Setup complete! Run 'source venv/bin/activate' to activate the environment"

clean:
	rm -f *.csv tributary_output_fixed.dxf column_load_takedown.xlsx
	@echo "✓ Cleaned output files"

verify-input:
	@test -f "$(INPUT_FILE)" || (echo "Missing $(INPUT_FILE). Drop your DXF next to the Makefile and name it $(INPUT_FILE)." && exit 1)

deps:
	$(PIP) install -r requirements.txt
