# Task 2.1 – Explore raw downloads and missing values
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pathlib import Path

from etl.transform_worldbank import transform_worldbank_file, transform_worldbank_countries
from etl.transform_who import transform_who_file

RAW_WB = Path("data/raw/worldbank")
RAW_WHO = Path("data/raw/who")

print("=" * 60)
print("WORLD BANK – countries")
countries = transform_worldbank_countries(RAW_WB / "countries.json")
print(countries.head())
print("Missing:\n", countries.isna().sum())

print("\n" + "=" * 60)
print("WORLD BANK – health expenditure")
df = transform_worldbank_file(RAW_WB / "SH.XPD.CHEX.GD.ZS_from2000.json", "SH.XPD.CHEX.GD.ZS")
print(df.head())
print(f"Missing value share: {df['value'].isna().mean():.1%}")

print("\n" + "=" * 60)
print("WHO – TB incidence")
df_who = transform_who_file(RAW_WHO / "MDG_0000000020_from2000.json", "MDG_0000000020")
print(df_who.head())
print(f"Missing value share: {df_who['value'].isna().mean():.1%}")