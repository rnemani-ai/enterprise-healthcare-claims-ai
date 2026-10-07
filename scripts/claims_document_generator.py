from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path.cwd()
DATA_DIR = PROJECT_ROOT / "data" / "raw" / "synthea"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "claim_documents"


def clean_value(value):
    if pd.isna(value):
        return "N/A"
    return str(value)


def clean_code(value):
    if pd.isna(value):
        return None

    value = str(value)

    if value.endswith(".0"):
        value = value[:-2]

    return value


def load_data():
    claims = pd.read_csv(DATA_DIR / "claims.csv")
    transactions = pd.read_csv(DATA_DIR / "claims_transactions.csv")
    encounters = pd.read_csv(DATA_DIR / "encounters.csv")
    patients = pd.read_csv(DATA_DIR / "patients.csv")

    return patients, encounters, claims, transactions


def build_claim_document(patient, encounter, claim, transactions):
    transaction_lines = []

    for _, tx in transactions.iterrows():
        transaction_lines.append(
            f"""
Transaction Type: {clean_value(tx['TYPE'])}
Procedure Code: {clean_code(tx['PROCEDURECODE']) or 'N/A'}
Description: {clean_value(tx['NOTES'])}
Amount: {clean_value(tx['AMOUNT'])}
Payment Method: {clean_value(tx['METHOD'])}
Units: {clean_value(tx['UNITS'])}
Outstanding: {clean_value(tx['OUTSTANDING'])}
""".strip()
        )

    diagnoses = []

    for i in range(1, 9):
        code = clean_code(claim[f"DIAGNOSIS{i}"])
        if code:
            diagnoses.append(code)

    document = f"""
HEALTHCARE CLAIM DOCUMENT

Claim ID: {clean_value(claim['Id'])}
Patient ID: {clean_value(claim['PATIENTID'])}
Service Date: {clean_value(claim['SERVICEDATE'])}

PATIENT
-------
Name: {clean_value(patient['FIRST'])} {clean_value(patient['LAST'])}
Gender: {clean_value(patient['GENDER'])}
Date of Birth: {clean_value(patient['BIRTHDATE'])}
City: {clean_value(patient['CITY'])}
State: {clean_value(patient['STATE'])}

ENCOUNTER
---------
Encounter ID: {clean_value(encounter['Id'])}
Encounter Type: {clean_value(encounter['ENCOUNTERCLASS'])}
Description: {clean_value(encounter['DESCRIPTION'])}
Start: {clean_value(encounter['START'])}
End: {clean_value(encounter['STOP'])}
Provider ID: {clean_value(encounter['PROVIDER'])}
Payer ID: {clean_value(encounter['PAYER'])}

CLAIM
-----
Claim Status: {clean_value(claim['STATUSP'])}
Department ID: {clean_value(claim['DEPARTMENTID'])}
Diagnosis Codes: {", ".join(diagnoses) if diagnoses else "N/A"}
Claim Type: {clean_value(claim['HEALTHCARECLAIMTYPEID1'])}

TRANSACTIONS
------------
{chr(10).join(transaction_lines)}

FINANCIAL SUMMARY
-----------------
Total Claim Cost: {clean_value(encounter['TOTAL_CLAIM_COST'])}
Payer Coverage: {clean_value(encounter['PAYER_COVERAGE'])}
"""

    return document.strip()


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    patients, encounters, claims, transactions = load_data()

    generated = 0

    for _, claim in claims.iterrows():

        patient_matches = patients[
            patients["Id"] == claim["PATIENTID"]
        ]

        encounter_matches = encounters[
            encounters["Id"] == claim["APPOINTMENTID"]
        ]

        claim_transactions = transactions[
            transactions["CLAIMID"] == claim["Id"]
        ]

        if patient_matches.empty or encounter_matches.empty:
            continue

        patient = patient_matches.iloc[0]
        encounter = encounter_matches.iloc[0]

        document = build_claim_document(
            patient,
            encounter,
            claim,
            claim_transactions,
        )

        output_file = OUTPUT_DIR / f"{claim['Id']}.txt"
        output_file.write_text(document, encoding="utf-8")

        generated += 1

    print(f"Generated {generated:,} claim documents.")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()