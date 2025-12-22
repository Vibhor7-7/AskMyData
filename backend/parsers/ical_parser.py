from icalendar import Calendar
import pandas as pd
from datetime import datetime
import os
from .parser_utils import standardize_dataframe


def parse_ical_file(file_path):
    """
    Parse iCal file and return standardized DataFrame
    
    Args:
        file_path: Path to .ics file
    
    Returns:
        Standardized DataFrame with calendar events
    """
    try:
        with open(file_path, "rb") as f:
            cal = Calendar.from_ical(f.read())

        events = []
        for component in cal.walk():
            if component.name == "VEVENT":
                start_dt = component.get("dtstart").dt
                end_dt = component.get("dtend").dt
                
                # Calculate duration
                if hasattr(start_dt, 'date') and hasattr(end_dt, 'date'):
                    duration = (end_dt - start_dt).total_seconds() / 3600
                else:
                    duration = 0
                
                events.append({
                    "summary": str(component.get("summary", "")),
                    "start": start_dt,
                    "end": end_dt,
                    "duration_hours": duration,
                    "location": str(component.get("location", "")),
                    "description": str(component.get("description", ""))
                })

        df = pd.DataFrame(events)
        
        # Standardize output
        filename = os.path.basename(file_path)
        standardized_df = standardize_dataframe(df, filename, 'ical')
        
        return standardized_df
        
    except Exception as e:
        print(f"Error reading iCal file: {e}")
        return None


def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'sch.ics')
    
    df = parse_ical_file(file_path)
    if df is not None:
        print("=== iCal Parser Output ===")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print("\nFirst 3 rows:")
        print(df.head(3))


if __name__ == "__main__":
    main()