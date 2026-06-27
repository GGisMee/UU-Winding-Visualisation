WINDING_GUIDE_TEXT = """The Winding Layout allows you to define the physical arrangement of the stator windings within the generator. This layout is represented as a matrix where you map electrical phases to specific slots and poles.

## The Winding Matrix
• Columns (Poles): Each column represents a magnetic pole of the rotor.
• Rows (Slots): Each row represents a physical slot in the stator.
• Cells: Each cell defines which electrical phase is placed in that specific slot for that specific pole, and its winding direction.

## How to Configure
1. Select Phase: Use the number keys (1-9) on your keyboard to select the active phase. The current active phase determines which phase will be assigned when you click.
2. Assign Positive Polarity: Left-click on a cell to assign the active phase with a positive winding direction (current flowing into the page). This is represented by a solid block of color.
3. Assign Negative Polarity: Right-click on a cell to assign the active phase with a negative winding direction (current flowing out of the page). This is represented by a hatched pattern.

By carefully arranging the phases and polarities across the poles and slots, you can optimize the generated voltage and minimize unwanted harmonic overtones."""
