import os

try:
    import pandas as pd
except ImportError:
    pd = None

def get_excel_data(filepath):
    """
    Reads an Excel file and returns (columns, rows).
    Raises ImportError if pandas is not installed.
    """
    if pd is None:
        raise ImportError("pandas/openpyxl not installed")
    
    ext = os.path.splitext(filepath)[1].lower()
    engine = 'openpyxl' if ext == '.xlsx' else None
    
    # Read first 50 rows
    df = pd.read_excel(filepath, engine=engine, nrows=50)
    
    # Handle NaN values for display
    df = df.fillna("")
    
    return list(df.columns), df.values.tolist()
