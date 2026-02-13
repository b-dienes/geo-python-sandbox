from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"

def get_input_path(filename: str) -> Path:
    """
    Returns the absolute path to a file in the data/inputs folder.

    Parameters
    ----------
    filename: str
        Name of the input file.

    Returns
    -------
    input_path: Path
        Absolute Path object pointing to the input file.

    Raises
    ------
    FileNotFoundError: If the input file does not exist.
    """
    input_path = DATA_DIR / "inputs" / filename

    if not input_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {input_path}")
    
    return input_path

def get_output_path(filename: str) -> Path:
    """
    Returns the absolute path to a file in the data/outputs folder.

    Parameters
    ----------
    filename: str
        Name of the output file.

    Returns
    -------
    output_path: Path
        Absolute Path object pointing to the output file.
    """
    output_path = DATA_DIR/ "outputs" / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path
