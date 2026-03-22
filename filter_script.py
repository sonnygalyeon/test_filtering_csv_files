import argparse
import csv
import statistics
from collections import defaultdict

from tabulate import tabulate


SUPPORTED_REPORTS = {"median-coffee"}


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Формирование отчетов по данным подготовки студентов к экзаменам"
    )
    parser.add_argument(
        "--files",
        nargs="+",
        required=True,
        help="Список CSV-файлов для обработки"
    )
    parser.add_argument(
        "--report",
        required=True,
        help="Название отчета. Поддерживается: median-coffee"
    )
    return parser.parse_args()


def read_csv_files(file_paths):
    rows = []

    for file_path in file_paths:
        try:
            with open(file_path, mode="r", encoding="utf-8") as csv_file:
                reader = csv.DictReader(csv_file)

                required_columns = {
                    "student",
                    "date",
                    "coffee_spent",
                    "sleep_hours",
                    "study_hours",
                    "mood",
                    "exam",
                }

                if reader.fieldnames is None:
                    raise ValueError(f"Файл '{file_path}' пустой или поврежден.")

                missing_columns = required_columns - set(reader.fieldnames)
                if missing_columns:
                    missing_str = ", ".join(sorted(missing_columns))
                    raise ValueError(
                        f"В файле '{file_path}' отсутствуют колонки: {missing_str}"
                    )

                for row in reader:
                    rows.append(row)

        except FileNotFoundError:
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        except UnicodeDecodeError:
            raise ValueError(
                f"Не удалось прочитать файл '{file_path}' в кодировке UTF-8."
            )

    return rows


def build_median_coffee_report(rows):
    student_coffee = defaultdict(list)

    for row in rows:
        student_name = row["student"].strip()
        coffee_spent_raw = row["coffee_spent"].strip()

        if not student_name:
            continue

        try:
            coffee_spent = float(coffee_spent_raw)
        except ValueError:
            raise ValueError(
                f"Некорректное значение coffee_spent '{coffee_spent_raw}' "
                f"у студента '{student_name}'."
            )

        student_coffee[student_name].append(coffee_spent)

    report_data = []

    for student_name, coffee_values in student_coffee.items():
        median_value = statistics.median(coffee_values)

        if median_value.is_integer():
            median_value = int(median_value)

        report_data.append(
            {
                "student": student_name,
                "median_coffee": median_value,
            }
        )

    report_data.sort(key=lambda item: item["median_coffee"], reverse=True)

    return report_data


def print_median_coffee_report(report_data):
    table_data = [
        [item["student"], item["median_coffee"]]
        for item in report_data
    ]

    print(
        tabulate(
            table_data,
            headers=["student", "median_coffee"],
            tablefmt="grid",
            colalign=("left", "right"),
        )
    )


def main():
    args = parse_arguments()

    if args.report not in SUPPORTED_REPORTS:
        supported = ", ".join(sorted(SUPPORTED_REPORTS))
        raise ValueError(
            f"Отчет '{args.report}' не поддерживается. "
            f"Доступные отчеты: {supported}"
        )

    rows = read_csv_files(args.files)

    if args.report == "median-coffee":
        report_data = build_median_coffee_report(rows)
        print_median_coffee_report(report_data)


if __name__ == "__main__":
    main()
