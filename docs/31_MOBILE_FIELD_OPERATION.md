# 31 Mobile Field Operation

## Goal

Mobile Field Operation turns FoxBrain into a daily tool for store employees.

Employees can use phones to:

- Upload store and product photos
- Submit daily store notes
- Submit customer feedback
- Submit inventory issues
- Submit competitor observations
- Submit event records
- Ask Jarvis
- Receive and complete tasks
- Feed the knowledge base through review

## Routes

- `/mobile`
- `/mobile/tasks`
- `/mobile/review`

## Field Submission Model

`field_submissions`

- `submission_id`
- `submission_type`
- `title`
- `content`
- `store_id`
- `employee_id`
- `related_object_type`
- `related_object_id`
- `photos`
- `attachments`
- `tags`
- `status`
- `reviewed_by`
- `reviewed_at`
- `review_notes`
- `created_by`
- `created_at`
- `updated_at`

## Submission Types

- `store_note`
- `product_photo`
- `customer_feedback`
- `inventory_issue`
- `competitor_price`
- `event_record`
- `training_note`
- `repair_issue`
- `knowledge_feed`

## Review Flow

Submit -> Pending Review -> Approve / Reject -> Convert to Task / Convert to Knowledge / Archive

No mobile submission becomes official knowledge without review.

## Mobile UX

- iPhone-first layout
- Large buttons
- Simple forms
- File input for camera/photo upload
- No dense ERP tables

## Safety

- Customer-sensitive data must remain permission controlled.
- Competitor observations are pending evidence until reviewed.
- Photos and notes are stored as submissions first, not official facts.
