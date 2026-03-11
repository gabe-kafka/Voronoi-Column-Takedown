from pathlib import Path

import ezdxf
import pandas as pd
import numpy as np

# Conversion factor
INCHES_TO_FEET = 1/12

# Input filename expected to be dropped next to the scripts
INPUT_DXF = Path("INPUT.DXF")
if not INPUT_DXF.exists():
    raise FileNotFoundError(f"Missing input DXF: {INPUT_DXF}")

# Load the DXF file
doc = ezdxf.readfile(str(INPUT_DXF))
msp = doc.modelspace()

# Initialize storage
points = []
boundaries = []
column_labels = []
floor_numbers = []

# Extract entities, using layers to distinguish types
for e in msp:
    layer = e.dxf.layer if hasattr(e.dxf, 'layer') else ''
    
    # Extract column labels from MTEXT entities on "COLUMN NUMBER" layer
    if e.dxftype() == "MTEXT" and layer == "COLUMN NUMBER":
        try:
            # Extract text content and coordinates
            label_text = e.text
            insert_point = e.dxf.insert
            
            # Convert coordinates from inches to feet
            x_feet = insert_point.x * INCHES_TO_FEET
            y_feet = insert_point.y * INCHES_TO_FEET
            
            # Store column label data
            column_labels.append({
                'label': label_text,
                'x': x_feet,
                'y': y_feet
            })
        except AttributeError as ex:
            # Handle malformed entities
            print(f"Warning: Skipping malformed MTEXT entity - {ex}")
        except Exception as ex:
            # Handle other unexpected errors
            print(f"Warning: Error processing MTEXT entity - {ex}")
    
    # Extract floor numbers from MTEXT entities on "FLOOR NUMBER" layer
    elif e.dxftype() == "MTEXT" and layer == "FLOOR NUMBER":
        try:
            # Extract text content and coordinates
            floor_text = e.text
            insert_point = e.dxf.insert
            
            # Convert coordinates from inches to feet
            x_feet = insert_point.x * INCHES_TO_FEET
            y_feet = insert_point.y * INCHES_TO_FEET
            
            # Store floor number data
            floor_numbers.append({
                'floor_number': floor_text,
                'x': x_feet,
                'y': y_feet
            })
        except AttributeError as ex:
            # Handle malformed entities
            print(f"Warning: Skipping malformed FLOOR NUMBER MTEXT entity - {ex}")
        except Exception as ex:
            # Handle other unexpected errors
            print(f"Warning: Error processing FLOOR NUMBER MTEXT entity - {ex}")
    
    # Extract floor numbers from TEXT entities on "FLOOR NUMBER" layer
    elif e.dxftype() == "TEXT" and layer == "FLOOR NUMBER":
        try:
            # Extract text content and coordinates
            floor_text = e.dxf.text
            insert_point = e.dxf.insert
            
            # Convert coordinates from inches to feet
            x_feet = insert_point.x * INCHES_TO_FEET
            y_feet = insert_point.y * INCHES_TO_FEET
            
            # Store floor number data
            floor_numbers.append({
                'floor_number': floor_text,
                'x': x_feet,
                'y': y_feet
            })
        except AttributeError as ex:
            # Handle malformed entities
            print(f"Warning: Skipping malformed FLOOR NUMBER TEXT entity - {ex}")
        except Exception as ex:
            # Handle other unexpected errors
            print(f"Warning: Error processing FLOOR NUMBER TEXT entity - {ex}")
    
    elif e.dxftype() == "POINT":
        pt = e.dxf.location
        points.append((pt.x * INCHES_TO_FEET, pt.y * INCHES_TO_FEET))
    elif e.dxftype() == "LINE" and layer == 'BOUNDARY':
        start = e.dxf.start
        end = e.dxf.end
        boundaries.append({
            'type': 'LINE',
            'start': (start.x * INCHES_TO_FEET, start.y * INCHES_TO_FEET),
            'end': (end.x * INCHES_TO_FEET, end.y * INCHES_TO_FEET)
        })
    elif e.dxftype() in ["POLYLINE", "LWPOLYLINE"] and layer == 'BOUNDARY':
        # Extract polyline vertices
        vertices = []
        if e.dxftype() == "POLYLINE":
            for vertex in e.vertices:
                pt = vertex.dxf.location
                vertices.append((pt.x * INCHES_TO_FEET, pt.y * INCHES_TO_FEET))
        else:  # LWPOLYLINE
            for vertex in e.get_points():
                vertices.append((vertex[0] * INCHES_TO_FEET, vertex[1] * INCHES_TO_FEET))
        if vertices:
            boundaries.append({
                'type': e.dxftype(),
                'vertices': vertices,
                'closed': e.closed if hasattr(e, 'closed') else False
            })
    elif e.dxftype() == "CIRCLE" and layer == 'BOUNDARY':
        center = e.dxf.center
        radius = e.dxf.radius
        boundaries.append({
            'type': 'CIRCLE',
            'center': (center.x * INCHES_TO_FEET, center.y * INCHES_TO_FEET),
            'radius': radius * INCHES_TO_FEET
        })
    elif e.dxftype() == "ARC" and layer == 'BOUNDARY':
        center = e.dxf.center
        radius = e.dxf.radius
        start_angle = e.dxf.start_angle
        end_angle = e.dxf.end_angle
        boundaries.append({
            'type': 'ARC',
            'center': (center.x * INCHES_TO_FEET, center.y * INCHES_TO_FEET),
            'radius': radius * INCHES_TO_FEET,
            'start_angle': start_angle,
            'end_angle': end_angle
        })

# Convert to DataFrames
points_df = pd.DataFrame(points, columns=["x", "y"])

# Create boundaries DataFrame
boundary_data = []
for i, boundary in enumerate(boundaries):
    if boundary['type'] in ["POLYLINE", "LWPOLYLINE"]:
        for j, vertex in enumerate(boundary['vertices']):
            boundary_data.append({
                'boundary_id': i,
                'type': boundary['type'],
                'vertex_index': j,
                'x': vertex[0],
                'y': vertex[1],
                'closed': boundary['closed']
            })
    elif boundary['type'] == "LINE":
        boundary_data.append({
            'boundary_id': i,
            'type': 'LINE',
            'start_x': boundary['start'][0],
            'start_y': boundary['start'][1],
            'end_x': boundary['end'][0],
            'end_y': boundary['end'][1]
        })
    elif boundary['type'] == "CIRCLE":
        boundary_data.append({
            'boundary_id': i,
            'type': boundary['type'],
            'center_x': boundary['center'][0],
            'center_y': boundary['center'][1],
            'radius': boundary['radius']
        })
    elif boundary['type'] == "ARC":
        boundary_data.append({
            'boundary_id': i,
            'type': boundary['type'],
            'center_x': boundary['center'][0],
            'center_y': boundary['center'][1],
            'radius': boundary['radius'],
            'start_angle': boundary['start_angle'],
            'end_angle': boundary['end_angle']
        })

boundaries_df = pd.DataFrame(boundary_data)

# Create column labels DataFrame
column_labels_df = pd.DataFrame(column_labels)

# Create floor numbers DataFrame
floor_numbers_df = pd.DataFrame(floor_numbers)

# Save to CSV
points_df.to_csv("dxf_points.csv", index=False)
boundaries_df.to_csv("dxf_boundaries.csv", index=False)
column_labels_df.to_csv("dxf_column_labels.csv", index=False)
floor_numbers_df.to_csv("dxf_floor_numbers.csv", index=False)

print("Points:")
print(points_df)
print("\nBoundaries:")
print(boundaries_df)
print("\nColumn Labels:")
print(column_labels_df)
if len(column_labels) == 0:
    print("Warning: No column labels found on 'COLUMN NUMBER' layer")
print("\nFloor Numbers:")
print(floor_numbers_df)
if len(floor_numbers) == 0:
    print("Warning: No floor numbers found on 'FLOOR NUMBER' layer")
