import pandas as pd
from typing import cast


def _create_group(students_with_scores: pd.DataFrame) -> pd.DataFrame:
    result = pd.DataFrame(index=students_with_scores.index)
    result = result.assign(
        net_id=students_with_scores.index,
        email_address=students_with_scores["Email Address"].str.lower(),
    )
    result[["last_name", "first_name"]] = students_with_scores["Name"].str.split(
        ", ", expand=True
    )
    result["homework_average"] = (
        students_with_scores["homework_1"]
        / students_with_scores["homework_1_max_points"]
    )
    return result


def generate_grade_book(
    students_df: pd.DataFrame, homework_exams_df: pd.DataFrame
) -> dict[int, pd.DataFrame]:
    return generate_gradebook(
        students_df=students_df, homework_exams_df=homework_exams_df
    )


def generate_gradebook(
    students_df: pd.DataFrame, homework_exams_df: pd.DataFrame
) -> dict[int, pd.DataFrame]:
    students_df.index = students_df.index.str.lower()
    students_with_scores = pd.merge(
        students_df,
        homework_exams_df,
        left_index=True,
        right_index=True,
    )
    return {
        cast(int, group): _create_group(students_with_scores=table)
        for group, table in students_with_scores.groupby("Group")
    }
