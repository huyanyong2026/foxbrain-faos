# BA-V2.0-D Store Health Model

Status: PASS

The Store Health Model scores each store from 0 to 100 across five dimensions: Sales Performance, Inventory Health, Product Performance, Task Completion, and Customer Experience.

## Dimensions

- Sales: current unit trend against previous period.
- Inventory: penalty for low-stock and slow-inventory alerts.
- Product: reward for positive product trends.
- Execution: completed store tasks divided by tracked tasks.
- Customer Experience: customer signal deltas from Core facts.

## Output

The engine returns store code, store name, total health, detailed dimension scores, and AI source trace. Example: Nanshan health 92 with Sales 95, Inventory 90, Execution 91.
