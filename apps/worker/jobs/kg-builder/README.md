# Knowledge Graph Builder Job

VAFOX Enterprise OS V1.9 worker job boundary.

Schedule: 02:30 daily.

Steps:

- Scan SAP readonly data
- Scan knowledge base
- Scan uploaded files
- Scan task and workflow records
- Update enterprise entities and graph edges

The worker must not write back to SAP.

