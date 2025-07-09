from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric, GetMetadataRequest
from models import GA4QueryInput, BasicQueryInput
from database import get_user_credentials
from auth import always_refresh_user_tokens
import logging
import traceback

logger = logging.getLogger(__name__)

async def get_ga4_data(input: GA4QueryInput) -> dict:
    """
    Query Google Analytics 4 data with specific dimensions and metrics.
    
    Common GA4 dimensions: date, country, city, deviceCategory, pagePath, source, medium, campaign
    Common GA4 metrics: sessions, users, pageviews, bounceRate, sessionDuration, conversions, revenue
    """
    try:
        logger.info(f"Starting GA4 data query for user: {input.user_id}")
        
        # Get user credentials
        try:
            refresh_token, property_id = get_user_credentials(input.user_id)
            logger.info(f"Retrieved credentials for user {input.user_id}, property: {property_id}")
        except Exception as e:
            logger.error(f"Failed to get user credentials: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to retrieve user credentials: {str(e)}",
                "data": [],
                "rowCount": 0
            }
        
        # Override property ID if provided
        if input.property_id:
            property_id = input.property_id
            logger.info(f"Using override property ID: {property_id}")
        
        # Refresh tokens
        try:
            creds = always_refresh_user_tokens(refresh_token)
            logger.info("Successfully refreshed user tokens")
        except Exception as e:
            logger.error(f"Failed to refresh tokens: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to refresh authentication tokens: {str(e)}",
                "data": [],
                "rowCount": 0
            }
        
        # Create GA4 client
        try:
            client = BetaAnalyticsDataClient(credentials=creds)
            logger.info("Created GA4 client successfully")
        except Exception as e:
            logger.error(f"Failed to create GA4 client: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to create GA4 client: {str(e)}",
                "data": [],
                "rowCount": 0
            }
        
        # Validate inputs
        if not input.dimensions and not input.metrics:
            return {
                "success": False,
                "error": "At least one dimension or metric must be specified",
                "data": [],
                "rowCount": 0
            }
        
        # Build the request
        try:
            request = RunReportRequest(
                property=f"properties/{property_id}",
                dimensions=[Dimension(name=d) for d in input.dimensions],
                metrics=[Metric(name=m) for m in input.metrics],
                date_ranges=[DateRange(start_date=input.start_date, end_date=input.end_date)],
                limit=input.limit
            )
            logger.info(f"Built request - Property: {property_id}, Dimensions: {input.dimensions}, Metrics: {input.metrics}")
        except Exception as e:
            logger.error(f"Failed to build request: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to build GA4 request: {str(e)}",
                "data": [],
                "rowCount": 0
            }
        
        # Execute the request
        try:
            logger.info("Executing GA4 request...")
            response = client.run_report(request)
            logger.info(f"GA4 request completed successfully, got {len(response.rows)} rows")
        except Exception as e:
            logger.error(f"GA4 API request failed: {str(e)}")
            return {
                "success": False,
                "error": f"GA4 API request failed: {str(e)}",
                "data": [],
                "rowCount": 0
            }
        
        # Convert response to readable format
        try:
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
            
            logger.info(f"Successfully processed {len(rows)} rows")
            
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
            logger.error(f"Failed to process response: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to process GA4 response: {str(e)}",
                "data": [],
                "rowCount": 0
            }
            
    except Exception as e:
        logger.error(f"Unexpected error in get_ga4_data: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "data": [],
            "rowCount": 0
        }

async def list_ga4_dimensions(input: BasicQueryInput) -> dict:
    """List all available GA4 dimensions for the user's property."""
    try:
        logger.info(f"Getting dimensions for user: {input.user_id}")
        
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
        
        logger.info(f"Retrieved {len(dimensions)} dimensions")
        
        return {
            "success": True,
            "dimensions": dimensions,
            "count": len(dimensions),
            "propertyId": property_id
        }
    except Exception as e:
        logger.error(f"Error in list_ga4_dimensions: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "error": str(e),
            "dimensions": [],
            "count": 0
        }

async def list_ga4_metrics(input: BasicQueryInput) -> dict:
    """List all available GA4 metrics for the user's property."""
    try:
        logger.info(f"Getting metrics for user: {input.user_id}")
        
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
        
        logger.info(f"Retrieved {len(metrics)} metrics")
        
        return {
            "success": True,
            "metrics": metrics,
            "count": len(metrics),
            "propertyId": property_id
        }
    except Exception as e:
        logger.error(f"Error in list_ga4_metrics: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "error": str(e),
            "metrics": [],
            "count": 0
        }