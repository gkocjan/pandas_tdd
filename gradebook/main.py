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

    homework_scores = students_with_scores.filter(
        regex=r"^homework_\d\d?$",
        axis=1,
    )
    homework_max_points = students_with_scores.filter(
        regex=r"^homework_\d\d?_max_points$",
        axis=1,
    ).set_axis(homework_scores.columns, axis=1)
    sum_of_homework_averages = (homework_scores / homework_max_points).sum(axis=1)
    number_of_homeworks = homework_scores.shape[1]

    result["homework_average"] = sum_of_homework_averages / number_of_homeworks
    return result


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
