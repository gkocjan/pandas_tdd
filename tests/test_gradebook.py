import pandas as pd


def generate_grade_book(students_df: pd.DataFrame) -> dict[int, pd.DataFrame]:
    return {1: pd.DataFrame()}


def test_results_are_grouped_by_student_group_for_students_in_one_group():
    students = [
        {
            "ID": 1,
            "Name": "Doe, John",
            "NetID": "JXD12345",
            "Email Adress": "JOHN.DOE@EXAMPLE.EDU",
            "Group": 1,
        }
    ]
    students_df = pd.DataFrame(data=students).set_index("ID")

    result = generate_grade_book(students_df=students_df)

    assert list(result.keys()) == [1]


def test_results_are_grouped_by_student_group_for_students_in_multiple_groups():
    students = [
        {
            "ID": 1,
            "Name": "Doe, John",
            "NetID": "JXD12345",
            "Email Adress": "JOHN.DOE@EXAMPLE.EDU",
            "Group": 1,
        },
        {
            "ID": 2,
            "Name": "Doe, Second",
            "NetID": "SXD54321",
            "Email Adress": "SECOND.DOE@EXAMPLE.EDU",
            "Group": 2,
        },
    ]
    students_df = pd.DataFrame(data=students).set_index("ID")

    result = generate_grade_book(students_df=students_df)

    assert list(result.keys()) == [1, 2]
