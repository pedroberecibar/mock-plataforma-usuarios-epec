# EPEC Commercial Portal — UI Kit

## Overview
High-fidelity component recreation of EPEC's internal **Gerencia Comercial** web application. This system is used by billing and commercial staff to manage customer supplies, meter readings, distributed generation configuration, and invoice generation.

## Design Width
Desktop-only: **1280px** minimum. Dense data-table layout typical of utility management systems.

## Screens in index.html
1. **Supply List** — searchable/filterable table of all supplies
2. **Supply Detail** — individual supply record with GD configuration tabs
3. **Meter Reading Entry** — OBIS code data entry form
4. **Billing Panel** — invoice generation and review

## Components
- `Sidebar.jsx` — Left navigation with EPEC branding and menu items
- `TopBar.jsx` — Top header with search, user info, breadcrumbs
- `SupplyTable.jsx` — Paginated data table for supply list
- `SupplyDetail.jsx` — Supply record detail with "E. Distribuida" tab
- `BillingPanel.jsx` — Billing history and invoice panel

## Usage Notes
- Import `../../colors_and_type.css` for tokens
- All components use Plus Jakarta Sans + JetBrains Mono from Google Fonts
- Icons via Lucide (CDN)
