import pandas as pd

# Create question schema from Excel file
# User must create Excel file and ensure it is formatted correctly
# Instructions provided in README and in Excel template file

def load_question_schema(path):
    # Read Excel file without headers
    df = pd.read_excel(path, header=None)

    questions = []
    option_row_idx = None

    # Find option header row: contains "Option 1"
    for i, row in df.iterrows():
        if any(str(cell).strip().lower() == "option 1" for cell in row):
            option_row_idx = i
            break

    if option_row_idx is None:
        raise ValueError("Could not find option header row")

    # Question rows start AFTER option row
    for i in range(option_row_idx + 1, len(df)):
        row = df.iloc[i]
        question_text = str(row.iloc[0]).strip()

        if not question_text or question_text.lower() == "nan":
            continue

        # Extract options
        options = [
            str(cell).strip()
            for cell in row.iloc[1:]
            if pd.notna(cell)
        ]

        question_type = "select" if options else "annotate"

        questions.append({
            "question_id": len(questions) + 1,
            "question_text": question_text,
            "question_type": question_type,
            "options": options
        })

    return questions
