from pathlib import Path


PROJECT_ROOT = Path.cwd()
DOCUMENT_DIR = PROJECT_ROOT / "data" / "processed" / "claim_documents"

REQUIRED_SECTIONS = [
    "HEALTHCARE CLAIM DOCUMENT",
    "PATIENT",
    "ENCOUNTER",
    "CLAIM",
    "TRANSACTIONS",
    "FINANCIAL SUMMARY",
]


def validate_document(file_path: Path) -> list[str]:
    errors = []

    content = file_path.read_text(encoding="utf-8")

    for section in REQUIRED_SECTIONS:
        if section not in content:
            errors.append(f"Missing section: {section}")

    if "Claim ID: N/A" in content:
        errors.append("Missing Claim ID")

    if "Patient ID: N/A" in content:
        errors.append("Missing Patient ID")

    return errors


def main():
    documents = list(DOCUMENT_DIR.glob("*.txt"))

    total = len(documents)
    valid = 0
    invalid = 0

    for document in documents:
        errors = validate_document(document)

        if errors:
            invalid += 1
            print(f"\nINVALID: {document.name}")

            for error in errors:
                print(f"  - {error}")
        else:
            valid += 1

    print("\nValidation Summary")
    print("------------------")
    print(f"Total documents: {total:,}")
    print(f"Valid documents: {valid:,}")
    print(f"Invalid documents: {invalid:,}")

    if invalid == 0:
        print("Validation PASSED")


if __name__ == "__main__":
    main()