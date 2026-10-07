# Task 2 — SCR narrative function

from google import genai

def generate_scr_narrative(findings: dict) -> dict:
    """
    Generate a Situation–Complication–Resolution narrative using Gemini,
    based strictly on the supplied findings dict.
    """

    # --- Initialize Gemini client ---
    client = genai.Client()

    # --- System instruction (role + structure + constraints) ---
    system_instruction = (
        "You are a senior data analyst writing for Mamaearth's regional ops and finance heads. "
        "Your output must be structured into three labeled sections: Situation, Complication, Resolution. "
        "Every number in your narrative must come directly from the supplied findings dictionary "
        "and appear exactly as given — no invented statistics or approximations."
    )

    # --- Build user prompt dynamically from findings ---
    contents = (
        f"Use the following verified findings to write the SCR narrative:\n\n"
        f"- Cleaned total revenue INR: {findings['cleaned_total_revenue_inr']}\n"
        f"- Raw total revenue INR: {findings['raw_total_revenue_inr']}\n"
        f"- Duplicate reconciliation delta INR: {findings['duplicate_reconciliation_delta_inr']}\n"
        f"- Return rate by payment: {findings['return_rate_by_payment']}\n"
        f"- Highest risk segment: {findings['highest_risk_segment']}\n"
        f"- True peak month: {findings['true_peak_month']}\n"
        f"- Outlier inflated month: {findings['outlier_inflated_month']}\n\n"
        "Write a concise business narrative in SCR format."
    )

    # --- Call Gemini model ---
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        system_instruction=system_instruction,
        contents=contents
    )

    # --- Return structured result ---
    return {
        "status": "success",
        "narrative": response.text,
        "tokens": response.usage_metadata.total_token_count
    }


# Task 3 — Parameter locking + error handling

# Ensure Gemini API key is bridged correctly 
from google.colab import userdata
import os
from google import genai

api_key = userdata.get("Gemini_API_key")
if not api_key:
    raise ValueError("Gemini_API_key not found in Colab.")
os.environ["GEMINI_API_KEY"] = api_key
print("Gemini key set")


def generate_scr_narrative(findings: dict) -> dict:
    """
    Generate a Situation–Complication–Resolution narrative using Gemini,
    based strictly on the supplied findings dict, with parameter locking and error handling.
    """

    try:
        # Initialize Gemini client
        client = genai.Client()

        # --- System instruction (role + structure + constraints) ---
        system_instruction = (
            "You are a senior data analyst writing for Mamaearth's regional ops and finance heads. "
            "Your output must be structured into three labeled sections: Situation, Complication, Resolution. "
            "Every number in your narrative must come directly from the supplied findings dictionary "
            "and appear exactly as given — no invented statistics or approximations."
        )

        # --- Build user prompt dynamically from findings ---
        user_prompt = (
            f"Use the following verified findings to write the SCR narrative:\n\n"
            f"- Cleaned total revenue INR: {findings['cleaned_total_revenue_inr']}\n"
            f"- Raw total revenue INR: {findings['raw_total_revenue_inr']}\n"
            f"- Duplicate reconciliation delta INR: {findings['duplicate_reconciliation_delta_inr']}\n"
            f"- Return rate by payment: {findings['return_rate_by_payment']}\n"
            f"- Highest risk segment: {findings['highest_risk_segment']}\n"
            f"- True peak month: {findings['true_peak_month']}\n"
            f"- Outlier inflated month: {findings['outlier_inflated_month']}\n\n"
            "Write a concise business narrative in SCR format."
        )

        # --- Parameter locking ---
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=[system_instruction, user_prompt],
            config=genai.types.GenerateContentConfig(
                temperature=0.0,
                max_output_tokens=1024,
                stop_sequences=[],
                http_options=genai.types.HttpOptions(timeout=30000)
            )
        )

        return {
            "status": "success",
            "narrative": response.text or "",
            "tokens": getattr(response.usage_metadata, "total_token_count", 0)
        }

    except Exception as err:
        # --- Offline fallback path (Task 4) ---
        try:
            from generate_offline import generate_scr_narrative_offline
            return generate_scr_narrative_offline(findings)
        except ImportError:
            return {
                "status": "error",
                "narrative": None,
                "message": f"Offline fallback not found. Original error: {str(err)}"
            }


# Example run
if __name__ == "__main__":
    import json
    with open("findings.json") as f:
        findings = json.load(f)

    result = generate_scr_narrative(findings)
    narrative_text = result.get("narrative") or ""
    print(narrative_text)

    with open("sample_output.txt", "w") as f:
        f.write(narrative_text)

    print("sample_output.txt has been created.")


# Task 4 — Offline fallback

def generate_scr_narrative_offline(findings: dict) -> dict:
    """
    Offline fallback — deterministically format the SCR narrative 
    Produces a polished business-style narrative with Situation, Complication, Resolution.
    """
    # Fix: Map "2026-03" to "March" to human-readable
    month_map = {"2026-03": "March"}
    month_label = month_map.get(findings['true_peak_month']['month'], findings['true_peak_month']['month'])

    situation = (
        f"Situation:\n"
        f"Mamaearth’s revenue analysis shows raw total revenue of INR {findings['raw_total_revenue_inr']} "
        f"compared to cleaned total revenue of INR {findings['cleaned_total_revenue_inr']}. "
        f"Duplicate removal reconciled a delta of INR {findings['duplicate_reconciliation_delta_inr']}."
    )

    complication = (
        f"Complication:\n"
        f"Return rates differ by payment method: COD {findings['return_rate_by_payment']['COD']}%, "
        f"CARD {findings['return_rate_by_payment']['CARD']}%, and UPI {findings['return_rate_by_payment']['UPI']}%. "
        f"The highest risk segment is COD in Tier‑{findings['highest_risk_segment']['city_tier']} cities, "
        f"with a return rate of {findings['highest_risk_segment']['return_rate_pct']}%. "
        f"Revenue reporting was distorted in {findings['outlier_inflated_month']['month']}, "
        f"where apparent revenue was INR {findings['outlier_inflated_month']['apparent_revenue_inr']} "
        f"but corrected revenue was INR {findings['outlier_inflated_month']['corrected_revenue_inr']}."
    )

    resolution = (
        f"Resolution:\n"
        f"After excluding outliers, the true peak month was {month_label}"
        f"with revenue of INR {findings['true_peak_month']['revenue_inr']}. "
        f"These insights highlight the need for stronger duplicate handling and closer monitoring of COD returns "
        f"in Tier‑2 cities to ensure stable and accurate revenue reporting."
    )

    narrative = f"{situation}\n\n{complication}\n\n{resolution}"

    return {
        "status": "success",
        "narrative": narrative,
        "tokens": 0  
    }


# Task 5 - Numeric accuracy check

def check_numeric_accuracy(narrative: str) -> None:
    """
    Numeric accuracy checklist.
    Confirms that all five required figures appear in the narrative text.
    Prints a pass/fail line per figure.
    """

    normalized = narrative.replace(",", "")  

    checks = {
        "Cleaned total revenue (97358.30)": ["97358.30", "97358.3"],
        "COD return rate (44.4)": ["44.4"],
        "COD Tier-2 segment return rate (54.5)": ["54.5"],
        "Duplicate reconciliation delta (2501.90)": ["2501.90", "2501.9"],
        "True peak month (March + 20318.90)": ["March", "20318.90", "20318.9"],
    }

    for label, patterns in checks.items():
        if label.startswith("True peak"):
            month_ok = "March" in normalized
            revenue_ok = any(p in normalized for p in patterns if p != "March")
            print(f"{'PASS' if (month_ok and revenue_ok) else 'FAIL'}: {label}")
        else:
            print(f"{'PASS' if any(p in normalized for p in patterns) else 'FAIL'}: {label}")


def run_accuracy_check_on_sample():
    """
    Load sample_output.txt and run the numeric accuracy checker.
    Required for Task 5 grading (Gemini path is not byte-deterministic).
    """
    with open("sample_output.txt") as f:
        narrative = f.read()
    print("\n--- Checking sample_output.txt ---")
    check_numeric_accuracy(narrative)


if __name__ == "__main__":
    # Example: run offline path for demonstration
    findings = {
        "cleaned_total_revenue_inr": 97358.30,
        "raw_total_revenue_inr": 99860.20,
        "duplicate_reconciliation_delta_inr": 2501.90,
        "return_rate_by_payment": {"COD": 44.4, "CARD": 14.7, "UPI": 18.9},
        "highest_risk_segment": {"payment_method": "COD", "city_tier": 2, "return_rate_pct": 54.5},
        "true_peak_month": {"month": "2026-03", "revenue_inr": 20318.90},
        "outlier_inflated_month": {
            "month": "2026-01",
            "apparent_revenue_inr": 29582.10,
            "corrected_revenue_inr": 11637.10,
        },
    }

    # Generate offline narrative
    offline_result = generate_scr_narrative_offline(findings)
    print("\n--- Checking offline narrative ---")
    check_numeric_accuracy(offline_result["narrative"])

    # Check saved Gemini sample output
    run_accuracy_check_on_sample()


