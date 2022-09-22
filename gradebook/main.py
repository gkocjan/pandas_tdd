import pandas as pd
from typing import cast


def generate_gradebook(
    students_df: pd.DataFrame,
    homework_exams_df: pd.DataFrame,
    quizes_results: dict[int, pd.DataFrame] | None = None,
    max_quiz_scores: dict | None = None,
) -> dict[int, pd.DataFrame]:
    return Gradebook(
        students_df=students_df,
        homework_exams_df=homework_exams_df,
        quizes_results=quizes_results,
        max_quiz_scores=max_quiz_scores,
    ).generate()


class Gradebook:
    def __init__(
        self,
        students_df: pd.DataFrame,
        homework_exams_df: pd.DataFrame,
        quizes_results: dict[int, pd.DataFrame] | None = None,
        max_quiz_scores: dict | None = None,
    ):
        self._students_df = students_df
        self._homework_exams_df = homework_exams_df
        self._quizes_results: dict[int, pd.DataFrame] = (
            quizes_results if quizes_results is not None else {}
        )
        self._max_quiz_scores: dict = (
            max_quiz_scores if max_quiz_scores is not None else {}
        )

    def generate(self) -> dict[int, pd.DataFrame]:
        self._students_df.index = self._students_df.index.str.lower()
        students_with_scores = pd.merge(
            self._students_df,
            self._homework_exams_df,
            left_index=True,
            right_index=True,
        )
        students_with_scores["Email Address"] = students_with_scores[
            "Email Address"
        ].str.lower()

        all_quizes_results = pd.DataFrame(index=students_with_scores["Email Address"])
        for quiz_number, quiz_results in self._quizes_results.items():
            quiz_name = f"quiz_{quiz_number}"
            quiz_results = quiz_results.drop(
                columns=["First Name", "Last Name"]
            ).rename(columns={"Grade": quiz_name})
            all_quizes_results = pd.concat([all_quizes_results, quiz_results], axis=1)

        students_with_scores = pd.merge(
            students_with_scores,
            all_quizes_results,
            left_on="Email Address",
            right_index=True,
        )

        result = pd.DataFrame(index=students_with_scores.index)
        result = result.assign(
            net_id=students_with_scores.index,
            group=students_with_scores["Group"],
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

        result["homework_score"] = sum_of_homework_averages / number_of_homeworks

        number_of_exams = students_with_scores.filter(
            regex=r"^exam_\d\d?$", axis=1
        ).shape[1]

        for exam_numer in range(1, number_of_exams + 1):
            result[f"exam_{exam_numer}_score"] = (
                students_with_scores[f"exam_{exam_numer}"]
                / students_with_scores[f"exam_{exam_numer}_max_points"]
            )

        sum_of_quiz_scores = students_with_scores.filter(
            regex=r"^quiz_\d$", axis=1
        ).sum(axis=1)
        result["quiz_score"] = (sum_of_quiz_scores / self._sum_of_quiz_max()).round(2)

        return {cast(int, group): table for group, table in result.groupby("group")}

    def _sum_of_quiz_max(self) -> int:
        return sum(self._max_quiz_scores.values())
