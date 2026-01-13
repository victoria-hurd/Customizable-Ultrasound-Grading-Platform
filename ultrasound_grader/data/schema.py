import pandas as pd

# Create question schema from Excel file
# User must create Excel file and ensure it is formatted correctly
# Instructions provided in README and in Excel template file

def load_question_schema(path):
    df = pd.read_excel(path)

    required_columns = {"Grading Criteria", "Question Type"}
    if not required_columns.issubset(df.columns):
        raise ValueError(
            "Spreadsheet must contain 'Grading Criteria' and 'Question Type' columns"
        )

    questions = []

    for idx, row in df.iterrows():
        question_text = str(row["Grading Criteria"]).strip()

        if not question_text or question_text.lower() == "nan":
            continue

        question_type = str(row["Question Type"]).strip().lower()

        if question_type not in {"select", "annotate"}:
            raise ValueError(
                f"Invalid question type '{question_type}' "
                f"for question: {question_text}"
            )

        options = []
        if question_type == "select":
            for col in df.columns:
                if col.startswith("Option"):
                    cell = row[col]
                    if pd.notna(cell):
                        options.append(str(cell).strip())

            if not options:
                raise ValueError(
                    f"Select question has no options: {question_text}"
                )

        questions.append({
            "question_id": len(questions) + 1,
            "question_text": question_text,
            "question_type": question_type,
            "options": options
        })

    if not questions:
        raise ValueError("No valid questions detected")

    return questions

