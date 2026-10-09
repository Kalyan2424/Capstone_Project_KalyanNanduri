# Mamaearth Returns & Growth Intelligence Pipeline

This repository implements a complete end‑to‑end analytics pipeline for Mamaearth’s order and returns data. It connects three layers seamlessly:

1. **SQL relational layer** to store and query raw customer, product, and order data.  
2. **Python/Pandas analysis layer** to clean, reconcile, and explore the data, producing verified figures and visualizations.  
3. **GenAI narrative layer** powered by Gemini, which transforms the verified numbers into a structured Situation–Complication–Resolution (SCR) business narrative for regional operations and finance heads.  

Every number reported in this project is computed directly from the raw CSVs and flows through the pipeline without manual editing. The design ensures reproducibility, transparency, and accuracy: SQL feeds Python, Python feeds GenAI, and the outputs are validated with numeric accuracy checks. By following the README step‑by‑step, any reader can recreate the database, run the analysis, generate the charts, and produce both online and offline narratives with identical results.

---

## 📂 Step‑by‑Step Pipeline

### 1. SQL Relational Layer (Part 1)
```
Create tables:
MySQL DB15 < sql/schema.sql
```
```
Load seed data:
MySQL DB15 < sql/seed_data.sql
```
```
Run reports:
MySQL DB15 < sql/reports.sql
```

Verify counts: Customers = 45, Products = 16, Orders = 180.
Reports produce totals, return rates, rankings, and category revenues.


### 2. Python Analysis & EDA (Part 2)
```
Run cleaning and EDA:
python analysis/clean_and_eda.py
```

This prints intermediate results (shapes, duplicates, imputations, reconciliation note, outlier flags, segmentation, correlations, monthly totals).

```
Generate visualizations:
python analysis/visualize.py
```

Charts are saved into the visualizations folder.


### 3. GenAI Narrative Layer (Part 3)
```
Generate_scr_narrative, Parameter locking and error handling and Offline fallback path
python narrator/generate_narrative.py
```
```
Option A (online): Set Gemini API key:
export GEMINI_API_KEY="your_free_key"
```
Produces narrative via Gemini and saves sample_output.txt.
```
Option B (offline fallback): Run with no key.
Generates deterministic SCR narrative locally.
```
Numeric accuracy checker validates five required figures in both offline and sample outputs.






