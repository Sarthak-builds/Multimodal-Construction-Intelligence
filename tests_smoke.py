"""Quick non-UI smoke tests for the demo engine (no Streamlit server needed)."""
import ast
import json
import re
import sys

src = open("app.py", encoding="utf-8").read()
ast.parse(src)
print("syntax OK")

COST_PER_SQFT = {
    "Residential - Apartment": {"1": 4200, "2": 2800, "3": 2100},
    "Residential - Villa": {"1": 5500, "2": 3600, "3": 2600},
    "Commercial - Office": {"1": 6200, "2": 4300, "3": 3200},
    "Commercial - Retail": {"1": 7000, "2": 4800, "3": 3500},
    "Industrial - Warehouse": {"1": 3800, "2": 2400, "3": 1800},
}
CITY_MARKET_INDEX = {"1": 1.12, "2": 0.95, "3": 0.82}
STEEL_KG_SQFT = {"Residential - Apartment": 3.6, "Residential - Villa": 4.2,
                 "Commercial - Office": 5.5, "Commercial - Retail": 5.0,
                 "Industrial - Warehouse": 6.2}


def compute_valuation(structure, sqft, tier, completion):
    total = sqft * COST_PER_SQFT[structure][tier]
    incurred = total * completion
    value = sqft * COST_PER_SQFT[structure][tier] * CITY_MARKET_INDEX[tier] * (0.55 + 0.45 * completion)
    return {"total": total, "value": value, "steel": sqft * STEEL_KG_SQFT[structure]}


def parse_json_reply(text):
    cleaned = re.sub(r"```(?:json)?", "", text).strip().strip("`")
    m = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not m:
        raise ValueError("no JSON")
    return json.loads(m.group(0))


v = compute_valuation("Residential - Apartment", 1800, "1", 0.65)
assert v["total"] == 1800 * 4200, "budget math"
assert 0 < v["value"], "valuation"
assert v["steel"] == 1800 * 3.6, "steel"
print("valuation engine OK:", v)

assert parse_json_reply('```json\n{"a": 1}\n```') == {"a": 1}
assert parse_json_reply('{"b": [1,2,3]}') == {"b": [1, 2, 3]}
print("json contract parser OK")
print("ALL TESTS PASSED")
