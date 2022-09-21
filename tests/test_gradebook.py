import pandas as pd
from typing import cast


def _create_group(raw_students_group: pd.DataFrame) -> pd.DataFrame:
    result = pd.DataFrame()
    return result.assign(
        net_id=raw_students_group["NetID"].str.lower(),
        email_address=raw_students_group["Email Address"].str.lower(),
    )


def generate_grade_book(students_df: pd.DataFrame) -> dict[int, pd.DataFrame]:
    return {
        cast(int, group): _create_group(raw_students_group=table)
        for group, table in students_df.groupby("Group")
    }


def test_results_are_grouped_by_student_group_for_students_in_one_group():
    students = [
        {
            "ID": 1,
            "Name": "Doe, John",
            "NetID": "JXD12345",
            "Email Address": "JOHN.DOE@EXAMPLE.EDU",
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
            "Email Address": "JOHN.DOE@EXAMPLE.EDU",
            "Group": 1,
        },
        {
            "ID": 2,
            "Name": "Doe, Second",
            "NetID": "SXD54321",
            "Email Address": "SECOND.DOE@EXAMPLE.EDU",
            "Group": 2,
        },
    ]
    students_df = pd.DataFrame(data=students).set_index("ID")

    result = generate_grade_book(students_df=students_df)

    assert list(result.keys()) == [1, 2]


def test_results_group_contains_students_net_id_lowercase():
    students = [
        {
            "ID": 1,
            "Name": "Doe, John",
            "NetID": "JXD12345",
            "Email Address": "JOHN.DOE@EXAMPLE.EDU",
            "Group": 1,
        },
        {
            "ID": 2,
            "Name": "Doe, Second",
            "NetID": "SXD54321",
            "Email Address": "SECOND.DOE@EXAMPLE.EDU",
            "Group": 1,
        },
    ]
    students_df = pd.DataFrame(data=students).set_index("ID")

    result = generate_grade_book(students_df=students_df)

    assert result[1]["net_id"].to_list() == ["jxd12345", "sxd54321"]


def test_results_group_contains_students_email_adress_lowercase():
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
            "Group": 1,
        },
    ]
    students_df = pd.DataFrame(data=students).set_index("ID")

    result = generate_grade_book(students_df=students_df)

    assert result[1]["email_address"].to_list() == [
        "john.doe@example.edu",
        "second.doe@example.edu",
    ]
