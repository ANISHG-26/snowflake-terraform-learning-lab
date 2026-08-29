# Phase 1 schema design — synthetic garage

## Naming and layering

- Database: `GARAGE_PROD`
- Landing schema: `RAW`
- Consumer schema: `ANALYTICS`
- Table names are singular business concepts; IDs are stable text keys from the CSVs.

`RAW` is the controlled landing area. `ANALYTICS` contains views that are safe
for garage staff and reporting users. The five source tables are deliberately
small, but they represent reference, master, location, inventory, and service
data.

## Tables and Snowflake types

| Table | Column | Type | Key / meaning |
|---|---|---|---|
| `RAW.MANUFACTURERS` | `manufacturer_id` | `VARCHAR(10)` | Primary key |
|  | `manufacturer_name` | `VARCHAR(100)` | Required brand name |
|  | `country` | `VARCHAR(60)` | Country label |
| `RAW.DEALERSHIPS` | `dealership_id` | `VARCHAR(10)` | Primary key |
|  | `dealership_name` | `VARCHAR(120)` | Required garage location name |
|  | `region` | `VARCHAR(60)` | Region label |
| `RAW.VEHICLES` | `vehicle_id` | `VARCHAR(10)` | Primary key |
|  | `manufacturer_id` | `VARCHAR(10)` | Foreign key to manufacturers |
|  | `model` | `VARCHAR(80)` | Model name |
|  | `model_year` | `NUMBER(4,0)` | Model year |
|  | `fuel_type` | `VARCHAR(20)` | Controlled label |
|  | `color` | `VARCHAR(30)` | Vehicle color |
|  | `price_usd` | `NUMBER(10,2)` | Monetary value, not floating point |
| `RAW.INVENTORY` | `inventory_id` | `VARCHAR(10)` | Primary key |
|  | `vehicle_id` | `VARCHAR(10)` | Foreign key to vehicles |
|  | `dealership_id` | `VARCHAR(10)` | Foreign key to dealerships |
|  | `status` | `VARCHAR(20)` | `IN_STOCK`, `IN_TRANSIT`, or `SOLD` |
| `RAW.SERVICE_RECORDS` | `service_id` | `VARCHAR(10)` | Primary key |
|  | `vehicle_id` | `VARCHAR(10)` | Foreign key to vehicles |
|  | `service_type` | `VARCHAR(40)` | Work performed |
|  | `service_date` | `DATE` | Service completion date |
|  | `cost_usd` | `NUMBER(10,2)` | Service cost |

For this learning project, keys and constraints document intent and help us
reason about quality. Snowflake standard tables do not generally enforce
primary-key and foreign-key constraints, so we will also run explicit orphan,
duplicate, null, and domain-value checks after loading.

## Dependency and load order

```text
MANUFACTURERS ──┐
                └──> VEHICLES ──┬──> INVENTORY ──> DEALERSHIPS
                                └──> SERVICE_RECORDS
```

Recommended load order:

1. `MANUFACTURERS`
2. `DEALERSHIPS`
3. `VEHICLES`
4. `INVENTORY`
5. `SERVICE_RECORDS`

The CSV load itself can succeed without enforced foreign keys, but this order
matches the business dependencies and makes validation easier.

## First curated view

Create `ANALYTICS.SERVICE_HISTORY` from `SERVICE_RECORDS` joined to `VEHICLES`
and `MANUFACTURERS`. Expose `service_id`, `vehicle_id`, manufacturer name,
model, model year, service type, service date, and cost. Do not expose raw
landing details unless a later use case requires them.

## Validation queries to plan

- Row counts for all five tables.
- Duplicate primary-key checks.
- Orphan checks for each foreign key.
- Null checks on required columns.
- Domain check for inventory status and fuel type.
- Aggregate service cost by month and manufacturer through the view.
