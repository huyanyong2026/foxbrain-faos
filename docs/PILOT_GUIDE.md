# Sprint 3 Pilot Guide

## Before using the pilot

Sign in through the enterprise identity flow and use the assigned role and
store scope. Do not share tokens. Data displayed by the Customer Brain, Retail
Brain, and Store Manager AI is read-only; every recommendation requires human
verification and execution outside the system.

## Employees

1. Open **Employee AI Workspace** (`ai-web`) and ask product or scenario
   questions to receive advisory guidance.
2. Use customer information only when your role includes customer-read scope
   and you are assigned to the customer's store.
3. Verify price, available inventory, sizing, customer consent, and the actual
   usage scenario before following up with a customer.

## Store managers

1. Choose your assigned store in **Store Manager Workspace**.
2. Review sales summary, product opportunities, inventory alerts, customer
   opportunities, and AI recommendations.
3. Confirm the current store data and customer authorization before assigning
   work. You can submit operational feedback; it is recorded for review and
   does not execute replenishment or other mutations.

## CEO users

1. Open **Huyan CEO AI Cockpit** (`huyan-web`) to view the read-only operating
   summary.
2. Treat sales, inventory, and customer opportunities as signals to review,
   not automated decisions.
3. Use the CEO role only for authorized management users and retain normal
   approval processes for all decisions and external actions.

## Escalation

If an API returns authentication, permission, or data-scope errors, stop and
ask the pilot administrator to verify the identity role and store assignment.
Report incorrect source data or unsafe recommendations through the Store
Manager feedback workflow; do not work around a scope restriction.
