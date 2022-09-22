import pandas as pd
import pytest

from gradebook.main import generate_gradebook


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
    students_df = pd.DataFrame(data=students).set_index("NetID")
    homework_exams = [
        {
            "First Name": "John",
            "Last Name": "Doe",
            "SID": "jxd12345",
            "homework_1": 25,
            "homework_1_max_points": 50,
        }
    ]
    homework_exams_df = pd.DataFrame(data=homework_exams).set_index("SID")

    result = generate_gradebook(
        students_df=students_df, homework_exams_df=homework_exams_df
    )

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
    homework_exams = [
        {
            "First Name": "John",
            "Last Name": "Doe",
            "SID": "jxd12345",
            "homework_1": 25,
            "homework_1_max_points": 50,
        },
        {
            "First Name": "Second",
            "Last Name": "Doe",
            "SID": "sxd54321",
            "homework_1": 40,
            "homework_1_max_points": 50,
        },
    ]
    students_df = pd.DataFrame(data=students).set_index("NetID")
    homework_exams_df = pd.DataFrame(data=homework_exams).set_index("SID")

    result = generate_gradebook(
        students_df=students_df, homework_exams_df=homework_exams_df
    )

    assert list(result.keys()) == [1, 2]
    assert result[1]["net_id"].to_list() == ["jxd12345"]
    assert result[2]["net_id"].to_list() == ["sxd54321"]


@pytest.fixture
def two_students_in_the_same_group_with_homeworks() -> tuple[
    pd.DataFrame, pd.DataFrame
]:
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
    homework_exams = [
        {
            "First Name": "John",
            "Last Name": "Doe",
            "SID": "jxd12345",
            "homework_1": 25,
            "homework_1_max_points": 50,
        },
        {
            "First Name": "Second",
            "Last Name": "Doe",
            "SID": "sxd54321",
            "homework_1": 40,
            "homework_1_max_points": 50,
        },
    ]
    students_df = pd.DataFrame(data=students).set_index("NetID")
    homework_exams_df = pd.DataFrame(data=homework_exams).set_index("SID")

    return students_df, homework_exams_df


def test_results_group_contains_students_net_id_lowercase(
    two_students_in_the_same_group_with_homeworks,
):
    students_df, homework_exams_df = two_students_in_the_same_group_with_homeworks
    result = generate_gradebook(
        students_df=students_df, homework_exams_df=homework_exams_df
    )

    assert result[1]["net_id"].to_list() == ["jxd12345", "sxd54321"]


def test_results_group_contains_students_email_adress_lowercase(
    two_students_in_the_same_group_with_homeworks,
):
    students_df, homework_exams_df = two_students_in_the_same_group_with_homeworks
    result = generate_gradebook(
        students_df=students_df, homework_exams_df=homework_exams_df
    )

    assert result[1]["email_address"].to_list() == [
        "john.doe@example.edu",
        "second.doe@example.edu",
    ]


def test_results_group_contains_students_first_name(
    two_students_in_the_same_group_with_homeworks,
):
    students_df, homework_exams_df = two_students_in_the_same_group_with_homeworks
    result = generate_gradebook(
        students_df=students_df, homework_exams_df=homework_exams_df
    )

    assert result[1]["first_name"].to_list() == [
        "John",
        "Second",
    ]


def test_results_group_contains_students_last_name(
    two_students_in_the_same_group_with_homeworks,
):
    students_df, homework_exams_df = two_students_in_the_same_group_with_homeworks
    result = generate_gradebook(
        students_df=students_df, homework_exams_df=homework_exams_df
    )

    assert result[1]["last_name"].to_list() == [
        "Doe",
        "Doe",
    ]


def test_results_group_contains_students_homework_average_for_single_homework():
    students = [
        {
            "ID": 1,
            "Name": "Doe, John",
            "NetID": "JXD12345",
            "Email Address": "JOHN.DOE@EXAMPLE.EDU",
            "Group": 1,
        }
    ]
    students_df = pd.DataFrame(data=students).set_index("NetID")
    homework_exams = [
        {
            "First Name": "John",
            "Last Name": "Doe",
            "SID": "jxd12345",
            "homework_1": 25,
            "homework_1_max_points": 50,
        }
    ]
    homework_exams_df = pd.DataFrame(data=homework_exams).set_index("SID")

    result = generate_gradebook(
        students_df=students_df,
        homework_exams_df=homework_exams_df,
    )

    assert result[1]["homework_average"].to_list() == [0.5]
