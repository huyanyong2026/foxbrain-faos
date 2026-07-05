# 56 Command Center

## Goal

Command Center is the OS-level control tower for company status, risks, work queue and data freshness.

## Route

- `/command-center`

## APIs

- `GET /api/command-center`
- `GET /api/command-palette`
- `POST /api/command-palette/execute`
- `GET /api/os/context`

Commands are logged but executed by their destination modules.
