from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path.cwd()
DATA_DIR = PROJECT_ROOT / "data" / "raw" / "synthea"
DOCUMENT_DIR = PROJECT_ROOT / "data" / "processed" / "claim_documents"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "claim_document_manifest.csv"


def main():
    claims = pd.read_csv(DATA_DIR / "claims.csv")
    encounters = pd.read_csv(DATA_DIR / "encounters.csv")
    patients = pd.read_csv(DATA_DIR / "patients.csv")

    rows = []

    for _, claim in claims.iterrows():
        patient = patients[patients["Id"] == claim["PATIENTID"]]
        encounter = encounters[encounters["Id"] == claim["APPOINTMENTID"]]

        if patient.empty or encounter.empty:
            continue

        patient = patient.iloc[0]
        encounter = encounter.iloc[0]

        document_id = str(claim["Id"])
        document_path = DOCUMENT_DIR / f"{document_id}.txt"

        rows.append(
            {
                "document_id": document_id,
                "document_type": "healthcare_claim",
                "claim_id": document_id,
                "patient_id": claim["PATIENTID"],
                "encounter_id": claim["APPOINTMENTID"],
                "provider_id": claim["PROVIDERID"],
                "payer_id": encounter["PAYER"],
                "encounter_type": encounter["ENCOUNTERCLASS"],
                "service_date": claim["SERVICEDATE"],
                "claim_status": claim["STATUSP"],
                "claim_type": claim["HEALTHCARECLAIMTYPEID1"],
                "document_path": str(document_path),
            }
        )

    manifest = pd.DataFrame(rows)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(OUTPUT_FILE, index=False)

    print(f"Manifest created: {OUTPUT_FILE}")
    print(f"Manifest records: {len(manifest):,}")


if __name__ == "__main__":
    main()