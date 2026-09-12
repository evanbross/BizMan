# Dealer Ops Blueprint

Feature spec for an original equipment-dealer management platform, scoped from public
marketing pages of an existing commercial product (Ideal Computer Systems /
idealcomputersystems.com) — what the category of software does, not how any specific
vendor builds, writes, or designs it.

A styled version of this document is also published as a Claude Artifact:
https://claude.ai/code/artifact/b1535751-8488-4c25-b821-d8f17173b681

## Scope note

This is a catalog of functional categories — inventory, service, CRM, POS, and so on —
inferred from a competitor's marketing copy, for the purpose of designing an **original**
system that covers similar ground for equipment dealers (outdoor power equipment,
powersports, marine, RV, ag).

- No text, layout, screen design, or code from the source product is reproduced here or
  should be reproduced in the build.
- Product/module names below (TargetCRM, Ideal Cloud, etc.) are the source vendor's
  trademarks, named only for reference — this project needs its own naming.
- Feature categories and general business functionality are not copyrightable; the
  specific expression of them is. Implementation, UI, and data model should be designed
  fresh, not reverse-engineered from the source app.

## Legal boundary to hold while building

- **Do** design original database schemas, UI layouts, wording, and code for every module.
- **Do** talk to actual dealers (or domain knowledge already on hand) about workflow
  details — that's better source material than a competitor's site.
- **Don't** copy screen layouts, marketing copy, help-doc text, or trade dress from the
  source product.
- **Don't** use the source vendor's product or company names, logos, or trademarks
  anywhere in this build.
- **Don't** reverse-engineer or decompile the source product's software if access to it
  is ever obtained — this spec is built from public marketing pages only, and should stay
  that way.

## Modules

### Operations

| Module | Description |
|---|---|
| Inventory Control | Real-time stock levels across units and parts, reorder thresholds, multi-location tracking. |
| Sales & Invoicing | Quote-to-invoice flow for unit and parts sales, document generation, line-item history. |
| Service Management | Work order creation, technician scheduling, job status tracking, warranty claim handling. |
| Parts Locator | Cross-dealer parts search — find a part in a partner network before ordering from the manufacturer. |
| Point of Sale | Counter-side transaction processing for walk-in parts and accessory sales. |
| Rental Management | Rental contracts, availability calendars, return/condition tracking. |

### Customer & Growth

| Module | Description |
|---|---|
| Customer Management | Unified customer records: purchase history, service history, communication log. |
| CRM | Targeted outreach campaigns and follow-up reminders built from purchase/service history. |
| Lead Management | Capture and track sales leads from first contact through close. |
| Web Storefront | Customer-facing site for browsing inventory and initiating purchases/service requests online. |
| Mobile App | Field access to CRM and operational functions for staff away from the front desk. |

### Finance & Back Office

| Module | Description |
|---|---|
| General Ledger | Core accounting ledger and cash-flow tracking tied to sales, service, and inventory activity. |
| Accounts Payable | Vendor invoice entry, posting, and payment tracking. |
| Payroll Integration | Sync of hours/commissions to an external payroll processor rather than a built-in payroll engine. |
| Accounting Sync | Two-way data sync with a general-purpose accounting package (e.g. QuickBooks). |
| Integrated Payments | Card/ACH processing embedded directly in the sales and service checkout flow. |
| Finance & Insurance | Payment-plan quoting and deal document assembly for financed unit sales. |

### Reporting

| Module | Description |
|---|---|
| Analytics & Reports | Gross profit, inventory turnover, sales/service performance dashboards. |

### Platform & Integrations

| Capability | Description |
|---|---|
| Cloud hosting | Hosted infrastructure so a dealer isn't running an on-prem server/DB. |
| Open API | Programmatic access to inventory/order data for external storefronts and marketplaces. |
| Manufacturer price sync | Scheduled ingestion of manufacturer/distributor price files. |
| Parts image management | Upload and share parts photos across locations for identification. |

### Target industries

Outdoor Power Equipment, Powersports, Marine, RV, Trailer, Golf Cars, Agriculture,
Hardware Retail, and combination categories ("Rural Lifestyle").

## OPE Deep Dive

Outdoor Power Equipment (mowers, tractors, handheld — Toro, Ariens/Gravely, Polaris) gets
its own set of requirements layered onto the modules above:

1. **Manufacturer & network integration** (Inventory / Parts Locator) — OEM warranty
   claim submission and product registration automated per-manufacturer (named
   integrations: Toro, Ariens/Gravely, Polaris, Ace Hardware); distributor parts ordering
   and price-list sync; Parts Locator extended to search a dealer network for
   used/hard-to-find parts during supply disruptions.
2. **Parts economics** (Parts Locator) — fill-rate tracking against a target (85–90%
   from stock), service-parts markup tracking (1–3%), margin verification against
   manufacturer MSRP, stock liquidation for slow-moving inventory.
3. **Service floor metrics** (Service Management) — color-coded work order status board,
   recovery rate (billed vs. paid hours), tech efficiency (billed vs. clocked time),
   completion-time tracking, and seasonal (annual/bi-annual) maintenance reminder
   campaigns — OPE's service load is sharply seasonal, so this matters more here than in
   year-round verticals.
4. **Customer communication** (Customer Management / CRM) — SMS for job-complete and
   parts-arrived events, text-to-pay on invoices, upsell/special-order add-on tracking at
   point of sale.
5. **Rental workflow** (Rental Management) — a unit crosses between rental and
   sales/service without re-entering its data; rentals, seasonal rent-to-own, and
   trade-ins are common enough in OPE that duplicate entry is a daily friction point.
6. **Sales KPIs** (Reporting) — per-salesperson performance and closing-ratio reporting.

## Suggested build order (all industries)

1. **Core counter operations** — Inventory Control, Sales & Invoicing, Customer
   Management, basic Reports. Replaces a spreadsheet-and-paper shop on its own.
2. **Service floor** — Service Management, Point of Sale, Parts Locator.
3. **Growth layer** — CRM, Lead Management, Web Storefront, Mobile App, Rental
   Management.
4. **Finance depth & platform** — General Ledger, Accounts Payable, Payroll/Accounting
   sync, Integrated Payments, F&I, Cloud hosting, Open API.

## Phase 1 build scope — OPE dealer (single location)

The generic Phase 1 above leaves an OPE shop's service bay on paper — repair and
seasonal tune-up work is a large share of an OPE dealer's daily volume, not an add-on.
This scope pulls a **minimal** service ticket into Phase 1 and pushes everything metric-
or automation-heavy to Phase 2, so the shop can run entirely inside the system from day
one without over-building.

### Entities

| Entity | Key fields | Notes |
|---|---|---|
| Customer | name, phone, email, address | One record shared by sales and service. |
| Unit | category, manufacturer, model, serial no., cost, price, status | Whole goods are serialized — track serial number from day one even though warranty/registration automation is Phase 2+, since retrofitting serial tracking onto sold history later is painful. |
| Part | SKU, description, manufacturer, qty on hand, reorder threshold, cost, price | Non-serialized, quantity-tracked. |
| Invoice / InvoiceLine | customer, status (quote/invoiced/paid), line items | A line references either a Unit or a Part — one sales flow for both. |
| WorkOrder | customer, unit (nullable), status, intake notes, parts used, timestamps | Status is just dropped off → in progress → ready → picked up. No recovery-rate or tech-efficiency math yet — that needs clocked-hours data this phase doesn't collect. |
| Location | name | Single row in Phase 1, but every other table carries a location FK so multi-location isn't a schema rewrite later. |

### Core workflows

1. **Sell a unit** — counter staff selects an in-stock Unit, generates an invoice, unit
   status flips to sold.
2. **Sell parts** — quick invoice against the Part catalog; quantity on hand decrements
   immediately.
3. **Take in for service** — create a WorkOrder against a Customer (and a Unit, if it was
   bought there or its serial is on file); status starts at dropped off.
4. **Work the ticket** — move status forward, attach Parts consumed against inventory as
   they're used, mark ready for pickup.
5. **Look up a customer** — see past invoices and open/closed work orders in one place at
   the counter.
6. **Check the numbers** — daily sales total, inventory value on hand, low-stock parts,
   open work order count.

### Explicitly out of scope for Phase 1

- Cross-dealer Parts Locator network, rental management, CRM/lead campaigns and SMS,
  multi-location, multi-user roles/permissions.
- Manufacturer OEM integrations — warranty claim automation, product registration,
  distributor ordering, price-list sync.
- Service KPI layer — recovery rate, tech efficiency, color-coded boards, maintenance
  reminder campaigns (all need clocked-hours or scheduling data Phase 1 doesn't capture).
- Payment processing (record method as a note field), accounting/payroll sync.
