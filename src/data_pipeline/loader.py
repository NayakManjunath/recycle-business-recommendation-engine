from pathlib import Path

import pandas as pd


def load_csv(file_path: str | Path) -> pd.DataFrame:
    """
    Load a CSV file into a pandas DataFrame.

    Parameters
    ----------
    file_path:
        Path to the CSV file.

    Returns
    -------
    pd.DataFrame
        Data loaded from the CSV file.

    Raises
    ------
    FileNotFoundError
        If the supplied file does not exist.
    ValueError
        If the supplied path does not point to a file.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    if not path.is_file():
        raise ValueError(f"CSV path is not a file: {path}")

    return pd.read_csv(path)