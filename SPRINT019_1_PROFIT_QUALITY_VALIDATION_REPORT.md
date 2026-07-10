# Sprint019.1 Profit Quality Validation Report

## Rule

2026 SAP profit already includes identified brand rebate income. FoxBrain must display rebates as composition only and must not add them again.

## Display Values

- SAP profit: 1,723,487.13 when no database value is available.
- Identified rebate portion included in SAP profit: 1,044,717.78.
- Osprey rebate: 964,798.03.
- Kailas rebate: 79,919.75.
- Profit excluding identified rebates: SAP profit minus identified rebate portion.
- Rebate dependency ratio: identified rebate portion divided by SAP profit.

## UX Requirement

The CEO homepage and workbench show a warning that rebate income is policy-dependent and not guaranteed as future recurring profit.

## Safety

No SAP data is modified. Profit composition is presentation logic only.

