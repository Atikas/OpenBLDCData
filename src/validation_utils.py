from pathlib import Path
import re
from collections import defaultdict

import pandas as pd
from IPython.display import Markdown, display


FILE_RE = re.compile(
    r"^analize_(?P<state>[a-z_]+?)(?P<id>\d+)(?:_(?P<quality>ENV|SF))?_(?P<rpm>\d+)rpm_(?P<ma>\d+)mA_(?P<source>[a-zA-Z0-9]+)\.csv$",
    re.IGNORECASE,
)


def decode_motor_from_id(exp_id: str) -> int:
    motor_prefix = exp_id[:-1]
    return int(motor_prefix or "0")


def currents_for_rpm(current_grid: dict[int, list[int]], rpm: int) -> list[int]:
    return current_grid.get(rpm, [])


def build_current_validation_df(
    data_dir: Path,
    source: str,
    expected_states: dict[int, list[str]],
    current_grid: dict[int, list[int]],
) -> tuple[pd.DataFrame, list[tuple[str, str]]]:
    group_stats = defaultdict(lambda: {"sum": 0.0, "count": 0, "file_count": 0})
    read_errors = []
    expected_state_rank = {
        motor: {state: i for i, state in enumerate(states)}
        for motor, states in expected_states.items()
    }

    all_csv = sorted(data_dir.glob("analize_*.csv"))

    for csv_path in all_csv:
        if csv_path.name.lower() == "analize_0rpm_0ma.csv":
            continue

        name_upper = csv_path.name.upper()
        if "_ENV_" in name_upper or "_SF_" in name_upper:
            continue

        match = FILE_RE.match(csv_path.name)
        if not match:
            continue

        if match.group("source").lower() != source.lower():
            continue

        state = match.group("state").lower()
        exp_id = match.group("id")
        rpm = int(match.group("rpm"))
        ma = int(match.group("ma"))
        motor = decode_motor_from_id(exp_id)

        if motor not in expected_states or state not in expected_states[motor]:
            continue
        if rpm not in current_grid or ma not in currents_for_rpm(current_grid, rpm):
            continue

        key = (motor, state, rpm, ma)
        group_stats[key]["file_count"] += 1

        try:
            current_series = pd.read_csv(csv_path, usecols=["curr_raw"])["curr_raw"].dropna()
            if current_series.empty:
                continue

            group_stats[key]["sum"] += float(current_series.sum())
            group_stats[key]["count"] += int(current_series.size)
        except Exception as exc:
            read_errors.append((csv_path.name, str(exc)))

    rows = []
    for motor in sorted(expected_states):
        for state in expected_states[motor]:
            for rpm in current_grid:
                for ma in currents_for_rpm(current_grid, rpm):
                    key = (motor, state, rpm, ma)
                    stats = group_stats.get(key)

                    if stats and stats["count"] > 0:
                        avg_current = stats["sum"] / stats["count"]
                        is_missing = False
                    else:
                        avg_current = None
                        is_missing = True

                    rows.append(
                        {
                            "motor": motor,
                            "state": state,
                            "rpm": rpm,
                            "mA": ma,
                            "file_count": int(stats["file_count"]) if stats else 0,
                            "avg_current_num": avg_current,
                            "avg_current": "-" if is_missing else f"{avg_current:.6f}",
                            "is_missing": is_missing,
                        }
                    )

    avg_df = pd.DataFrame(rows)
    avg_df["state_rank"] = avg_df.apply(
        lambda row: expected_state_rank.get(row["motor"], {}).get(row["state"], 999),
        axis=1,
    )
    avg_df = avg_df.sort_values(["motor", "state_rank", "rpm", "mA"]).reset_index(drop=True)

    avg_df["decreasing_current_vs_previous_ma"] = False
    for (_, _, _), group in avg_df.groupby(["motor", "state", "rpm"], sort=False):
        prev_avg = None
        for idx in group.index.tolist():
            curr = avg_df.at[idx, "avg_current_num"]
            if curr is None:
                continue
            if prev_avg is not None and curr < prev_avg:
                avg_df.at[idx, "decreasing_current_vs_previous_ma"] = True
            prev_avg = curr

    return avg_df, read_errors


def render_current_validation_report(
    avg_df: pd.DataFrame,
    read_errors: list[tuple[str, str]],
    title: str,
    expected_states: dict[int, list[str]],
) -> None:
    view_cols = ["motor", "state", "rpm", "mA", "file_count", "avg_current"]

    def style_table(display_df: pd.DataFrame) -> pd.DataFrame:
        style_df = pd.DataFrame("", index=display_df.index, columns=display_df.columns)
        style_df.loc[display_df["is_missing"], "avg_current"] = "color: red; font-weight: 700;"
        violation_col = "current_decreased_vs_previous_ma"
        style_df.loc[display_df[violation_col].eq(True), :] = "color: red; font-weight: 700;"
        return style_df

    display(Markdown(f"## {title}"))
    for motor in sorted(expected_states):
        motor_df = avg_df[avg_df["motor"] == motor].copy()
        print(f"\nMotor {motor}")
        display_df = (
            motor_df[view_cols + ["decreasing_current_vs_previous_ma", "is_missing"]]
            .rename(columns={"decreasing_current_vs_previous_ma": "current_decreased_vs_previous_ma"})
        )
        display_df["current_decreased_vs_previous_ma"] = display_df["current_decreased_vs_previous_ma"].astype("object")
        display_df.loc[display_df["is_missing"], "current_decreased_vs_previous_ma"] = "-"
        styled = (
            display_df.style.apply(style_table, axis=None)
            .hide(axis="columns", subset=["is_missing"])
            .hide(axis="index")
        )
        display(styled)

    missing_count = int(avg_df["is_missing"].sum())
    violations = int(avg_df["decreasing_current_vs_previous_ma"].sum())
    print(f"\nMissing combinations: {missing_count}")
    print(f"Current decrease flags found: {violations}")

    if read_errors:
        print("\nSome files could not be read:")
        for fname, err in read_errors[:10]:
            print(f"- {fname}: {err}")
        if len(read_errors) > 10:
            print(f"... and {len(read_errors) - 10} more files with errors")
