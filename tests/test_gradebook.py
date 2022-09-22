import factory
import pandas as pd
import pytest

from gradebook.main import generate_gradebook


class DataFrameFactory(factory.DictFactory):
    @classmethod
    def build_df_batch(cls, size, **kwargs) -> pd.DataFrame:
        """Build a batch of instances of the given class, with overridden attrs.

        Args:
            size (int): the number of instances to build

        Returns:
            object pd.DataFrame: the built instances with js_round(ed) values
        """
        raw_rows = cls.build_batch(size=size, **kwargs)
        return cls._converted_rows_to_df(raw_rows)

    @classmethod
    def _converted_rows_to_df(cls, converterd_rows: list[dict]) -> pd.DataFrame:
        return pd.DataFrame(data=converterd_rows)


@pytest.fixture
def students_factory() -> type[DataFrameFactory]:
    class StudentsFactory(DataFrameFactory):
        class Meta:
            rename = {"Email_Address": "Email Address"}

        ID = factory.Sequence(lambda n: n + 1)
        Name = factory.Iterator(["Doe, John", "Doe, Second"])
        NetID = factory.Iterator(["JXD12345", "SXD54321"])
        Email_Address = factory.LazyAttribute(
            lambda o: f'{o.Name.split(", ")[1]}.{o.Name.split(", ")[0]}@EXAMPLE.EDU'.upper()
        )
        Group = 1

        @classmethod
        def _converted_rows_to_df(cls, converterd_rows: list[dict]) -> pd.DataFrame:
            return pd.DataFrame(data=converterd_rows).set_index("NetID")

    return StudentsFactory


@pytest.fixture
def homework_factory() -> type[DataFrameFactory]:
    class HomeworkFactory(DataFrameFactory):
        class Meta:
            rename = {
                "First_Name": "First Name",
                "Last_Name": "Last Name",
            }

        First_Name = factory.Iterator(["John", "Second"])
        Last_Name = factory.Iterator(["Doe", "Doe"])
        SID = factory.Iterator(["jxd12345", "sxd54321"])
        homework_1 = factory.Iterator([25, 40])
        homework_1_max_points = factory.Iterator([50, 50])

        @classmethod
        def _converted_rows_to_df(cls, converterd_rows: list[dict]) -> pd.DataFrame:
            return pd.DataFrame(data=converterd_rows).set_index("SID")

    return HomeworkFactory


@pytest.fixture
def multiple_homework_factory(homework_factory) -> type[DataFrameFactory]:
    class MultipleHomeworkFactory(homework_factory):
        homework_2 = factory.Iterator([25, 40])
        homework_2_max_points = factory.Iterator([50, 50])
        homework_3 = factory.Iterator([30, 10])
        homework_3_max_points = factory.Iterator([50, 50])
        homework_4 = factory.Iterator([0, 50])
        homework_4_max_points = factory.Iterator([50, 50])

    return MultipleHomeworkFactory


@pytest.fixture
def multiple_homework_exams_factory(
    multiple_homework_factory,
) -> type[DataFrameFactory]:
    class MultipleHomeworkExamsFactory(multiple_homework_factory):
        exam_1 = factory.Iterator([95, 95])
        exam_1_max_points = factory.Iterator([100, 100])
        exam_2 = factory.Iterator([90, 77])
        exam_2_max_points = factory.Iterator([100, 100])
        exam_3 = factory.Iterator([73, 79])
        exam_3_max_points = factory.Iterator([100, 100])

    return MultipleHomeworkExamsFactory


def test_students_factory(students_factory):
    assert students_factory.create() == {
        "ID": 1,
        "Name": "Doe, John",
        "NetID": "JXD12345",
        "Email Address": "JOHN.DOE@EXAMPLE.EDU",
        "Group": 1,
    }
    assert students_factory.create() == {
        "ID": 2,
        "Name": "Doe, Second",
        "NetID": "SXD54321",
        "Email Address": "SECOND.DOE@EXAMPLE.EDU",
        "Group": 1,
    }


def test_homework_factory(homework_factory):
    assert homework_factory.create() == {
        "First Name": "John",
        "Last Name": "Doe",
        "SID": "jxd12345",
        "homework_1": 25,
        "homework_1_max_points": 50,
    }
    assert homework_factory.create() == {
        "First Name": "Second",
        "Last Name": "Doe",
        "SID": "sxd54321",
        "homework_1": 40,
        "homework_1_max_points": 50,
    }


def test_results_are_grouped_by_student_group_for_students_in_one_group(
    students_factory, homework_factory
):
    students_df = students_factory.build_df_batch(size=1)
    homework_exams_df = homework_factory.build_df_batch(size=1)

    result = generate_gradebook(
        students_df=students_df, homework_exams_df=homework_exams_df
    )

    assert list(result.keys()) == [1]


def test_results_are_grouped_by_student_group_for_students_in_multiple_groups(
    students_factory, homework_factory
):
    students_df = pd.concat(
        [
            students_factory.build_df_batch(size=1),
            students_factory.build_df_batch(size=1, Group=2),
        ]
    )
    homework_exams_df = homework_factory.build_df_batch(size=2)

    result = generate_gradebook(
        students_df=students_df, homework_exams_df=homework_exams_df
    )

    assert list(result.keys()) == [1, 2]
    assert result[1]["net_id"].to_list() == ["jxd12345"]
    assert result[2]["net_id"].to_list() == ["sxd54321"]


@pytest.fixture
def two_students_in_the_same_group_with_homeworks(
    students_factory, homework_factory
) -> tuple[pd.DataFrame, pd.DataFrame]:
    students_df = students_factory.build_df_batch(size=2)
    homework_exams_df = homework_factory.build_df_batch(size=2)

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


def test_results_group_contains_students_homework_average_for_single_homework(
    students_factory, homework_factory
):
    students_df = students_factory.build_df_batch(size=1)
    homework_exams_df = homework_factory.build_df_batch(size=1)

    result = generate_gradebook(
        students_df=students_df,
        homework_exams_df=homework_exams_df,
    )

    assert result[1]["homework_score"].to_list() == [0.5]


def test_results_group_contains_students_homework_score_for_multiple_homeworks(
    students_factory, multiple_homework_factory
):
    students_df = students_factory.build_df_batch(size=2)
    homework_exams_df = multiple_homework_factory.build_df_batch(size=2)

    result = generate_gradebook(
        students_df=students_df,
        homework_exams_df=homework_exams_df,
    )

    assert result[1]["homework_score"].to_list() == [0.4, 0.7]


def test_results_group_contains_students_exam_score_for_multiple_homeworks(
    students_factory, multiple_homework_exams_factory
):
    students_df = students_factory.build_df_batch(size=2)
    homework_exams_df = multiple_homework_exams_factory.build_df_batch(size=2)

    result = generate_gradebook(
        students_df=students_df,
        homework_exams_df=homework_exams_df,
    )

    assert result[1]["exam_1_score"].to_list() == [0.95, 0.95]
    assert result[1]["exam_2_score"].to_list() == [0.9, 0.77]
    assert result[1]["exam_3_score"].to_list() == [0.73, 0.79]
