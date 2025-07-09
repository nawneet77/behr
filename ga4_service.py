from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric, GetMetadataRequest
from models import GA4QueryInput, BasicQueryInput
from database import get_user_credentials
from auth import always_refresh_user_tokens

async def get_ga4_data(input: GA4QueryInput) -> dict:
    """
    Query Google Analytics 4 data with specific dimensions and metrics.
    
    Common GA4 dimensions: date, country, city, deviceCategory, pagePath, source, medium, campaign
    Common GA4 metrics: sessions, users, pageviews, bounceRate, sessionDuration, conversions, revenue
    """
    try:
        refresh_token, property_id = get_user_credentials(input.user_id)
        if input.property_id:
            property_id = input.property_id
            
        creds = always_refresh_user_tokens(refresh_token)
        client = BetaAnalyticsDataClient(credentials=creds)
        
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name=d) for d in input.dimensions],
            metrics=[Metric(name=m) for m in input.metrics],
            date_ranges=[DateRange(start_date=input.start_date, end_date=input.end_date)],
            limit=input.limit
        )
        
        response = client.run_report(request)
        
        # Convert response to readable format
        rows = []
        for row in response.rows:
            row_data = {}
            # Add dimensions
            for i, dim_value in enumerate(row.dimension_values):
                dim_name = response.dimension_headers[i].name
                row_data[dim_name] = dim_value.value
            # Add metrics
            for i, metric_value in enumerate(row.metric_values):
                metric_name = response.metric_headers[i].name
                row_data[metric_name] = metric_value.value
            rows.append(row_data)
        
        return {
            "success": True,
            "data": rows,
            "rowCount": len(rows),
            "dimensions": input.dimensions,
            "metrics": input.metrics,
            "dateRange": f"{input.start_date} to {input.end_date}",
            "propertyId": property_id
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": [],
            "rowCount": 0
        }

async def list_ga4_dimensions(input: BasicQueryInput) -> dict:
    """List all available GA4 dimensions for the user's property."""
    try:
        refresh_token, property_id = get_user_credentials(input.user_id)
        creds = always_refresh_user_tokens(refresh_token)
        client = BetaAnalyticsDataClient(credentials=creds)
        
        metadata = client.get_metadata(GetMetadataRequest(name=f"properties/{property_id}/metadata"))
        
        dimensions = []
        for d in metadata.dimensions:
            dimensions.append({
                "name": d.api_name,
                "displayName": d.ui_name,
                "description": d.description
            })
        
        return {
            "success": True,
            "dimensions": dimensions,
            "count": len(dimensions),
            "propertyId": property_id
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "dimensions": [],
            "count": 0
        }

async def list_ga4_metrics(input: BasicQueryInput) -> dict:
    """List all available GA4 metrics for the user's property."""
    try:
        refresh_token, property_id = get_user_credentials(input.user_id)
        creds = always_refresh_user_tokens(refresh_token)
        client = BetaAnalyticsDataClient(credentials=creds)
        
        metadata = client.get_metadata(GetMetadataRequest(name=f"properties/{property_id}/metadata"))
        
        metrics = []
        for m in metadata.metrics:
            metrics.append({
                "name": m.api_name,
                "displayName": m.ui_name,
                "description": m.description
            })
        
        return {
            "success": True,
            "metrics": metrics,
            "count": len(metrics),
            "propertyId": property_id
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "metrics": [],
            "count": 0
        }