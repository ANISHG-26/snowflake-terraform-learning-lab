"""Generate deterministic synthetic relational data for the Phase 1 workshop."""

from __future__ import annotations

import csv
import random
from pathlib import Path


SEED = 20260828
VEHICLE_COUNT = 300
OUTPUT_DIR = Path(__file__).parent / "data"

MAKES_AND_MODELS = {
    "Orion": ["Trail 2", "Aster", "Summit"],
    "Maple": ["City E", "Cedar", "North"],
    "Northstar": ["Haul 150", "Voyager", "Pioneer"],
    "Solara": ["Breeze", "Arc", "Lumen"],
    "Evergreen": ["Ridge", "Meadow", "Peak"],
}
FUEL_TYPES = ["Gasoline", "Hybrid", "Electric", "Diesel"]
COLORS = ["Silver", "Blue", "White", "Black", "Green", "Red"]
REGIONS = ["Ontario", "Quebec", "Alberta", "British Columbia"]


def generate_data() -> dict[str, list[dict[str, object]]]:
    rng = random.Random(SEED)

    manufacturers = [
        {"manufacturer_id": f"M{n:03d}", "manufacturer_name": make, "country": country}
        for n, (make, country) in enumerate(
            zip(MAKES_AND_MODELS, ["Canada", "United States", "Japan", "Germany", "Sweden"], strict=True), 1
        )
    ]

    dealerships = [
        {
            "dealership_id": f"D{n:03d}",
            "dealership_name": f"{rng.choice(list(MAKES_AND_MODELS))} Motors {n}",
            "region": rng.choice(REGIONS),
        }
        for n in range(1, 21)
    ]

    vehicles = []
    inventory = []
    service_records = []
    for number in range(1, VEHICLE_COUNT + 1):
        make = rng.choice(list(MAKES_AND_MODELS))
        model = rng.choice(MAKES_AND_MODELS[make])
        fuel_type = rng.choice(FUEL_TYPES)
        vehicle_id = f"V{number:04d}"
        base_price = {"Electric": 39000, "Hybrid": 33000}.get(fuel_type, 28000)
        vehicles.append(
            {
                "vehicle_id": vehicle_id,
                "manufacturer_id": f"M{list(MAKES_AND_MODELS).index(make) + 1:03d}",
                "model": model,
                "model_year": rng.randint(2018, 2025),
                "fuel_type": fuel_type,
                "color": rng.choice(COLORS),
                "price_usd": base_price + rng.randint(-5000, 18000),
            }
        )
        inventory.append(
            {
                "inventory_id": f"I{number:04d}",
                "vehicle_id": vehicle_id,
                "dealership_id": f"D{rng.randint(1, 20):03d}",
                "status": rng.choice(["IN_STOCK", "IN_TRANSIT", "SOLD"]),
            }
        )
        service_records.append(
            {
                "service_id": f"S{number:04d}",
                "vehicle_id": vehicle_id,
                "service_type": rng.choice(["Inspection", "Oil change", "Brake service", "Tire rotation"]),
                "service_date": f"2025-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
                "cost_usd": rng.randint(80, 1600),
            }
        )

    return {
        "manufacturers": manufacturers,
        "dealerships": dealerships,
        "vehicles": vehicles,
        "inventory": inventory,
        "service_records": service_records,
    }


def main() -> None:
    data = generate_data()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, rows in data.items():
        output_path = OUTPUT_DIR / f"{name}.csv"
        with output_path.open("w", newline="", encoding="utf-8") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {len(rows):>3} rows to {output_path}")


if __name__ == "__main__":
    main()
