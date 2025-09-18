#!/usr/bin/env python3
"""Web Debugging MCP Server for NexusKnowledge

This MCP server provides web debugging capabilities for the NexusKnowledge project,
including HTTP request testing, API endpoint debugging, and web error analysis.
"""

import asyncio
import json
import logging
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("NexusKnowledge-WebDebug")

# HTTP client for making requests
http_client = httpx.AsyncClient(timeout=30.0)


@mcp.tool()
def test_api_endpoint(
    url: str,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    data: dict[str, Any] | None = None,
    params: dict[str, str] | None = None,
) -> str:
    """Test an API endpoint with custom HTTP method, headers, and data.

    Args:
    ----
        url: The API endpoint URL to test
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        headers: Optional headers to include in the request
        data: Optional JSON data for POST/PUT requests
        params: Optional query parameters

    Returns:
    -------
        JSON string with response details including status, headers, and body

    """
    try:
        # Prepare request parameters
        request_kwargs = {
            "method": method.upper(),
            "url": url,
            "headers": headers or {},
            "params": params or {},
        }

        # Add data for POST/PUT requests
        if data and method.upper() in ["POST", "PUT", "PATCH"]:
            request_kwargs["json"] = data

        # Make the request
        response = httpx.request(**request_kwargs)

        # Prepare response data
        response_data = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.text,
            "url": str(response.url),
            "method": method.upper(),
            "success": response.status_code < 400,
        }

        # Try to parse JSON response
        try:
            response_data["json"] = response.json()
        except:
            response_data["json"] = None

        return json.dumps(response_data, indent=2)

    except Exception as e:
        return json.dumps(
            {"error": str(e), "url": url, "method": method.upper(), "success": False},
            indent=2,
        )


@mcp.tool()
def debug_nexus_api(
    endpoint: str = "/api/v1/status", base_url: str = "http://localhost:8000",
) -> str:
    """Debug NexusKnowledge API endpoints with common test cases.

    Args:
    ----
        endpoint: API endpoint to test (default: /api/v1/status)
        base_url: Base URL for the API (default: http://localhost:8000)

    Returns:
    -------
        JSON string with debugging information

    """
    try:
        full_url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        # Test basic connectivity
        response = httpx.get(full_url, timeout=10.0)

        debug_info = {
            "endpoint": endpoint,
            "full_url": full_url,
            "status_code": response.status_code,
            "response_time_ms": response.elapsed.total_seconds() * 1000,
            "headers": dict(response.headers),
            "body": response.text,
            "success": response.status_code < 400,
        }

        # Test with different HTTP methods
        methods_to_test = ["GET", "POST", "PUT", "DELETE"]
        method_results = {}

        for method in methods_to_test:
            try:
                test_response = httpx.request(method, full_url, timeout=5.0)
                method_results[method] = {
                    "status_code": test_response.status_code,
                    "success": test_response.status_code < 400,
                }
            except Exception as e:
                method_results[method] = {"error": str(e), "success": False}

        debug_info["method_tests"] = method_results

        return json.dumps(debug_info, indent=2)

    except Exception as e:
        return json.dumps(
            {
                "error": str(e),
                "endpoint": endpoint,
                "base_url": base_url,
                "success": False,
            },
            indent=2,
        )


@mcp.tool()
def analyze_http_error(status_code: int, response_body: str, request_url: str) -> str:
    """Analyze HTTP errors and provide debugging suggestions.

    Args:
    ----
        status_code: HTTP status code
        response_body: Response body content
        request_url: URL that caused the error

    Returns:
    -------
        Analysis of the error with debugging suggestions

    """
    analysis = {
        "status_code": status_code,
        "url": request_url,
        "error_type": "unknown",
        "suggestions": [],
        "common_causes": [],
    }

    # Analyze status code
    if status_code == 404:
        analysis["error_type"] = "not_found"
        analysis["suggestions"] = [
            "Check if the endpoint URL is correct",
            "Verify the API server is running",
            "Check if the route is properly defined",
        ]
        analysis["common_causes"] = [
            "Incorrect endpoint path",
            "API server not running",
            "Route not registered",
        ]
    elif status_code == 500:
        analysis["error_type"] = "server_error"
        analysis["suggestions"] = [
            "Check server logs for detailed error information",
            "Verify database connectivity",
            "Check for unhandled exceptions in the code",
        ]
        analysis["common_causes"] = [
            "Database connection issues",
            "Unhandled exceptions",
            "Configuration problems",
        ]
    elif status_code == 422:
        analysis["error_type"] = "validation_error"
        analysis["suggestions"] = [
            "Check request data format",
            "Verify required fields are provided",
            "Check data types and constraints",
        ]
        analysis["common_causes"] = [
            "Invalid JSON format",
            "Missing required fields",
            "Type validation failures",
        ]
    elif status_code == 401:
        analysis["error_type"] = "unauthorized"
        analysis["suggestions"] = [
            "Check authentication credentials",
            "Verify API key or token",
            "Check authorization headers",
        ]
        analysis["common_causes"] = [
            "Missing authentication",
            "Invalid credentials",
            "Expired tokens",
        ]

    # Analyze response body for additional clues
    if "database" in response_body.lower():
        analysis["suggestions"].append("Check database connection and configuration")
    if "timeout" in response_body.lower():
        analysis["suggestions"].append("Check for timeout issues in external services")
    if "permission" in response_body.lower():
        analysis["suggestions"].append("Check file and directory permissions")

    return json.dumps(analysis, indent=2)


@mcp.tool()
def test_nexus_search_api(
    query: str = "test query", limit: int = 10, base_url: str = "http://localhost:8000",
) -> str:
    """Test the NexusKnowledge search API endpoint.

    Args:
    ----
        query: Search query to test
        limit: Maximum number of results
        base_url: Base URL for the API

    Returns:
    -------
        JSON string with search results and debugging information

    """
    try:
        search_url = f"{base_url.rstrip('/')}/api/v1/search"
        params = {"q": query, "limit": limit}

        response = httpx.get(search_url, params=params, timeout=30.0)

        result = {
            "query": query,
            "limit": limit,
            "url": str(response.url),
            "status_code": response.status_code,
            "response_time_ms": response.elapsed.total_seconds() * 1000,
            "success": response.status_code < 400,
        }

        if response.status_code == 200:
            try:
                search_results = response.json()
                result["results"] = search_results
                result["result_count"] = len(search_results)
            except:
                result["raw_response"] = response.text
        else:
            result["error"] = response.text

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e), "query": query, "success": False}, indent=2)


@mcp.tool()
def monitor_api_health(
    base_url: str = "http://localhost:8000", endpoints: list[str] | None = None,
) -> str:
    """Monitor the health of multiple API endpoints.

    Args:
    ----
        base_url: Base URL for the API
        endpoints: List of endpoints to check (default: common endpoints)

    Returns:
    -------
        JSON string with health status of all endpoints

    """
    if endpoints is None:
        endpoints = [
            "/api/v1/status",
            "/api/v1/search",
            "/api/v1/feedback",
            "/api/v1/ingest",
        ]

    health_results = {
        "base_url": base_url,
        "timestamp": asyncio.get_event_loop().time(),
        "endpoints": {},
    }

    for endpoint in endpoints:
        try:
            full_url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
            response = httpx.get(full_url, timeout=5.0)

            health_results["endpoints"][endpoint] = {
                "status_code": response.status_code,
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "healthy": response.status_code < 400,
                "url": full_url,
            }

        except Exception as e:
            health_results["endpoints"][endpoint] = {
                "error": str(e),
                "healthy": False,
                "url": f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}",
            }

    return json.dumps(health_results, indent=2)


@mcp.resource("nexus://api/status")
def api_status_resource() -> str:
    """Get the current status of the NexusKnowledge API."""
    try:
        response = httpx.get("http://localhost:8000/api/v1/status", timeout=5.0)
        return f"API Status: {response.status_code}\nResponse: {response.text}"
    except Exception as e:
        return f"API Status: Error - {e!s}"


@mcp.resource("nexus://api/endpoints")
def api_endpoints_resource() -> str:
    """Get available API endpoints for debugging."""
    endpoints = [
        "GET /api/v1/status - API health check",
        "GET /api/v1/search?q=<query>&limit=<int> - Search conversations",
        "POST /api/v1/feedback - Submit feedback",
        "POST /api/v1/ingest - Ingest new data",
        "GET /api/v1/feedback - List feedback items",
        "POST /api/v1/analysis - Queue analysis",
        "POST /api/v1/correlation - Queue correlation",
        "GET /api/v1/correlation/{id} - Get correlation candidates",
    ]
    return "\n".join(endpoints)


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
