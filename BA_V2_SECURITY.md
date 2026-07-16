# BA_V2_SECURITY

Version: BA-V2.0-A

## Mission
Upgrade FoxBrain Supply Chain Center from digital inventory assistant to AI Supply Chain Operating System without redesigning the foundation, changing SAP core logic, or creating a duplicate inventory database.

## Architecture
SAP B1 remains the business truth. Core Enterprise Data Layer remains the source for product, brand, store, inventory, sales, supplier, and event facts. The Supply Chain Intelligence Engine in `foxbrain_os/business_activation_v2_supply_chain.py` turns Core facts into forecasts, purchase plans, transfer suggestions, brand health, supplier alerts, Huyan CEO command center data, and approval workflow tasks.

## Controls
All AI recommendations require human approval before business execution. Supplier data is filtered to own-brand scope. Store managers are filtered to own-store scope. CEO permissions can view all Huyan command center outputs.

## Acceptance
Demand Forecast: PASS  
Purchase Planning: PASS  
Inventory Transfer: PASS  
Brand Dashboard: PASS  
Supplier Collaboration: PASS  
AI Agent: PASS  
Huyan Integration: PASS  
Security: PASS  
Deployment: PASS

## Policy
RBAC permissions gate functions; ABAC scopes restrict supplier brand and store manager store visibility; audit events record permission checks with actor, action, decision, reason, and timestamp.
