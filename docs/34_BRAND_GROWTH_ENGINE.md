# 34 Brand Growth Engine

## Goal

Brand Growth Engine helps VAFOX manage each brand strategically.

It supports:

- Brand role classification
- Brand diagnosis
- Brand strategy
- Pricing strategy
- Inventory portfolio matrix
- Supplier and rebate risk
- Brand task generation
- Content and research handoff

## Route

- `/brand-growth`

## Brand Roles

- Core Growth Brand
- Profit Brand
- Traffic Brand
- Image Brand
- Strategic Brand
- Clearance Brand
- Experimental Brand
- Private Label

These are editable classifications. V1 does not hardcode final business decisions.

## Models

`brand_diagnoses`

- `diagnosis_id`
- `brand_id`
- `sales_status`
- `margin_status`
- `inventory_status`
- `discount_status`
- `supplier_status`
- `market_status`
- `customer_feedback`
- `key_problems`
- `opportunities`
- `ai_suggestions`
- `data_sources`
- `status`

`brand_strategies`

- `strategy_id`
- `brand_id`
- `strategy_title`
- `brand_role`
- `target_customer`
- `target_stores`
- `pricing_principle`
- `inventory_principle`
- `content_principle`
- `growth_goal`
- `risk_control`
- `key_actions`

`pricing_strategies`

- `pricing_strategy_id`
- `brand_id`
- `product_id`
- `normal_discount`
- `promotion_discount`
- `clearance_discount`
- `minimum_allowed_discount`
- `rebate_assumption`
- `margin_warning_line`
- `notes`

## Osprey Template

The engine includes Osprey discount simulation as a safe template. It does not state final pricing conclusions without real data and human decision.

## Safety

- Do not invent brand sales, margin, stock, rebate or supplier facts.
- External research must remain pending until reviewed.
- Pricing changes require human review.
