#!/bin/bash
set -e

INPUT_FILE="INPUT.DXF"

if [[ ! -f "$INPUT_FILE" ]]; then
  echo "❌ Missing input file: $INPUT_FILE"
  echo "   Drop your DXF next to this script and name it exactly '$INPUT_FILE'."
  exit 1
fi

echo "🔄 Running DXF processing pipeline..."
echo ""

echo "Step 1/3: Extracting DXF data..."
python3 extract_dxf_data.py

echo ""
echo "Step 2/3: Running panelize..."
python3 panelize.py

echo ""
echo "Step 3/3: Generating color-coded tributary output..."
python3 tributary.py

echo ""
echo "✓ Processing complete!"
echo "✓ Output: tributary_output_fixed.dxf (with color-coded layers)"
echo "✓ Output: column_load_takedown.xlsx (column load takedown)"
