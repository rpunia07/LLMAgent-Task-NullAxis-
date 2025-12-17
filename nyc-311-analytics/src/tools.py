from langchain.tools import tool
import pandas as pd

@tool
def analyze_complaint_types(limit=10):
    return f"SELECT complaint_type, COUNT(*) as count FROM data GROUP BY complaint_type ORDER BY count DESC LIMIT {limit}"

@tool
def analyze_closure_time(complaint_type=None):
    where = f"WHERE complaint_type = '{complaint_type}'" if complaint_type else ""
    return f"""
    SELECT 
        complaint_type,
        AVG(date_diff('hour', created_date, closed_date)) as avg_hours
    FROM data
    {where}
    GROUP BY complaint_type
    ORDER BY avg_hours DESC
    LIMIT 20
    """

@tool
def analyze_zip_codes(limit=10):
    return f"SELECT incident_zip, COUNT(*) as count FROM data GROUP BY incident_zip ORDER BY count DESC LIMIT {limit}"

@tool
def analyze_geocoding():
    return "SELECT COUNT(CASE WHEN latitude IS NOT NULL AND longitude IS NOT NULL THEN 1 END) * 100.0 / COUNT(*) as valid_geo_pct FROM data"
