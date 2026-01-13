import pandas as pd

# Create question schema from Excel file
# User must create Excel file and ensure it is formatted correctly
# Instructions provided in README and in Excel template file

def load_question_schema(path):
    df = pd.read_excel(path, header=None) # read in grading criteria
    question_types = ["Single Select", "Annotation"] # dynamic for future expansion

    # Find header row with grading criteria, question type, options, etc
    header_row_idx = None
    header_map = {}
    for i, row in df.iterrows():
        normalized = {
            str(cell).strip().lower(): idx
            for idx, cell in enumerate(row)
            if pd.notna(cell)
        }

        if "grading criteria" in normalized and "question type" in normalized:
            header_row_idx = i
            header_map = normalized
            break

    if header_row_idx is None:
        raise ValueError(
            "Could not find header row containing "
            "'Grading Criteria' and 'Question Type'"
        )

    # Find option columns based on new header
    option_cols = [
        idx for name, idx in header_map.items()
        if name.startswith("option")
    ]

    question_col = header_map["grading criteria"]
    type_col = header_map["question type"]

    # Parse questions from rows below the found header
    questions = []
    for i in range(header_row_idx + 1, len(df)):
            print(question_types)
            print(f"Processing row index: {i}")
            row = df.iloc[i]
            print(f"{row}")
            question_text = row.iloc[question_col]
            if pd.isna(question_text):
                continue
            question_text = str(question_text).strip()
            if not question_text:
                continue
            question_type = str(row.iloc[type_col])
            print(f"Question type: {question_type}")
            if question_type not in question_types:
                print(question_types)
                raise ValueError(
                    f"Invalid question type '{question_type}' "
                    f"in row {i + 1}"
                )
            
            options = df.iloc[i, option_cols]
            print(f"Options raw data: {options}")

            options = []
            if question_type == question_types[0]: # "single select"
                for col in option_cols:
                    cell = row.iloc[col]
                    print(f"Option cell at col {col}: {cell}")
                    if pd.notna(cell):
                        options.append(str(cell).strip())

                if not options:
                    raise ValueError(
                        f"Select question has no options: "
                        f"'{question_text}' (row {i + 1})"
                    )

            print(options)
            questions.append({
                "question_id": len(questions) + 1,
                "question_text": question_text,
                "question_type": question_type,
                "options": options
            })
            print(questions)

    if not questions:
        raise ValueError("No valid questions found below header row")

    return questions

