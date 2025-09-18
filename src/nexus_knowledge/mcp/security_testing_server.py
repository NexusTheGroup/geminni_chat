#!/usr/bin/env python3
"""Security Testing MCP Server for P8-P12 Security Testing.
Provides comprehensive security testing and validation capabilities.
"""

import logging
import time
from datetime import datetime
from typing import Any

import requests
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Security Testing Server")


@mcp.tool()
def test_sql_injection(
    base_url: str = "http://localhost:8000",
    endpoints: list[str] | None = None,
) -> dict[str, Any]:
    """Test for SQL injection vulnerabilities.

    Args:
    ----
        base_url: Base URL to test
        endpoints: List of endpoints to test

    Returns:
    -------
        SQL injection test results

    """
    if endpoints is None:
        endpoints = [
            "/api/v1/search",
            "/api/v1/ingest",
            "/api/v1/analysis",
        ]

    results = {
        "base_url": base_url,
        "endpoints": endpoints,
        "timestamp": datetime.now().isoformat(),
        "vulnerabilities": [],
        "tests_performed": 0,
    }

    # Common SQL injection payloads
    sql_payloads = [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "' UNION SELECT * FROM users --",
        "1' OR '1'='1",
        "admin'--",
        "' OR 1=1 --",
        "'; INSERT INTO users VALUES ('hacker', 'password'); --",
    ]

    try:
        for endpoint in endpoints:
            url = f"{base_url}{endpoint}"

            for payload in sql_payloads:
                results["tests_performed"] += 1

                # Test GET parameters
                try:
                    response = requests.get(url, params={"q": payload}, timeout=10)
                    if (
                        "error" in response.text.lower()
                        or "sql" in response.text.lower()
                    ):
                        results["vulnerabilities"].append(
                            {
                                "endpoint": endpoint,
                                "method": "GET",
                                "payload": payload,
                                "status_code": response.status_code,
                                "response_snippet": response.text[:200],
                            },
                        )
                except Exception as e:
                    logger.warning(f"GET test failed for {endpoint}: {e}")

                # Test POST parameters
                try:
                    response = requests.post(url, json={"query": payload}, timeout=10)
                    if (
                        "error" in response.text.lower()
                        or "sql" in response.text.lower()
                    ):
                        results["vulnerabilities"].append(
                            {
                                "endpoint": endpoint,
                                "method": "POST",
                                "payload": payload,
                                "status_code": response.status_code,
                                "response_snippet": response.text[:200],
                            },
                        )
                except Exception as e:
                    logger.warning(f"POST test failed for {endpoint}: {e}")

        results["vulnerability_count"] = len(results["vulnerabilities"])
        results["success"] = True

        logger.info(
            f"SQL Injection Test: {results['vulnerability_count']} vulnerabilities found",
        )

    except Exception as e:
        results["error"] = str(e)
        results["success"] = False
        logger.error(f"SQL Injection Test Failed: {e}")

    return results


@mcp.tool()
def test_xss_vulnerabilities(
    base_url: str = "http://localhost:8000",
    endpoints: list[str] | None = None,
) -> dict[str, Any]:
    """Test for Cross-Site Scripting (XSS) vulnerabilities.

    Args:
    ----
        base_url: Base URL to test
        endpoints: List of endpoints to test

    Returns:
    -------
        XSS test results

    """
    if endpoints is None:
        endpoints = [
            "/api/v1/search",
            "/api/v1/ingest",
            "/api/v1/analysis",
        ]

    results = {
        "base_url": base_url,
        "endpoints": endpoints,
        "timestamp": datetime.now().isoformat(),
        "vulnerabilities": [],
        "tests_performed": 0,
    }

    # Common XSS payloads
    xss_payloads = [
        "<script>alert('XSS')</script>",
        "javascript:alert('XSS')",
        "<img src=x onerror=alert('XSS')>",
        "<svg onload=alert('XSS')>",
        "';alert('XSS');//",
        "\"><script>alert('XSS')</script>",
        "<iframe src=javascript:alert('XSS')>",
    ]

    try:
        for endpoint in endpoints:
            url = f"{base_url}{endpoint}"

            for payload in xss_payloads:
                results["tests_performed"] += 1

                # Test GET parameters
                try:
                    response = requests.get(url, params={"q": payload}, timeout=10)
                    if payload in response.text or "<script>" in response.text:
                        results["vulnerabilities"].append(
                            {
                                "endpoint": endpoint,
                                "method": "GET",
                                "payload": payload,
                                "status_code": response.status_code,
                                "response_snippet": response.text[:200],
                            },
                        )
                except Exception as e:
                    logger.warning(f"GET XSS test failed for {endpoint}: {e}")

                # Test POST parameters
                try:
                    response = requests.post(url, json={"query": payload}, timeout=10)
                    if payload in response.text or "<script>" in response.text:
                        results["vulnerabilities"].append(
                            {
                                "endpoint": endpoint,
                                "method": "POST",
                                "payload": payload,
                                "status_code": response.status_code,
                                "response_snippet": response.text[:200],
                            },
                        )
                except Exception as e:
                    logger.warning(f"POST XSS test failed for {endpoint}: {e}")

        results["vulnerability_count"] = len(results["vulnerabilities"])
        results["success"] = True

        logger.info(f"XSS Test: {results['vulnerability_count']} vulnerabilities found")

    except Exception as e:
        results["error"] = str(e)
        results["success"] = False
        logger.error(f"XSS Test Failed: {e}")

    return results


@mcp.tool()
def test_authentication_security(
    base_url: str = "http://localhost:8000",
    auth_endpoints: list[str] | None = None,
) -> dict[str, Any]:
    """Test authentication security.

    Args:
    ----
        base_url: Base URL to test
        auth_endpoints: List of authentication endpoints

    Returns:
    -------
        Authentication security test results

    """
    if auth_endpoints is None:
        auth_endpoints = [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
        ]

    results = {
        "base_url": base_url,
        "auth_endpoints": auth_endpoints,
        "timestamp": datetime.now().isoformat(),
        "vulnerabilities": [],
        "tests_performed": 0,
    }

    # Common authentication bypass attempts
    auth_tests = [
        {"username": "admin", "password": "admin"},
        {"username": "admin", "password": "password"},
        {"username": "admin", "password": "123456"},
        {"username": "' OR '1'='1", "password": "' OR '1'='1"},
        {"username": "admin'--", "password": "anything"},
        {"username": "admin", "password": ""},
        {"username": "", "password": "admin"},
        {"username": "admin", "password": None},
    ]

    try:
        for endpoint in auth_endpoints:
            url = f"{base_url}{endpoint}"

            for test_case in auth_tests:
                results["tests_performed"] += 1

                try:
                    response = requests.post(url, json=test_case, timeout=10)

                    # Check for successful authentication (should not happen with test credentials)
                    if response.status_code == 200 and "token" in response.text.lower():
                        results["vulnerabilities"].append(
                            {
                                "endpoint": endpoint,
                                "test_case": test_case,
                                "status_code": response.status_code,
                                "response_snippet": response.text[:200],
                            },
                        )

                    # Check for information disclosure
                    if (
                        "password" in response.text.lower()
                        or "user" in response.text.lower()
                    ):
                        results["vulnerabilities"].append(
                            {
                                "endpoint": endpoint,
                                "test_case": test_case,
                                "issue": "Information disclosure",
                                "status_code": response.status_code,
                                "response_snippet": response.text[:200],
                            },
                        )

                except Exception as e:
                    logger.warning(f"Auth test failed for {endpoint}: {e}")

        results["vulnerability_count"] = len(results["vulnerabilities"])
        results["success"] = True

        logger.info(
            f"Authentication Security Test: {results['vulnerability_count']} vulnerabilities found",
        )

    except Exception as e:
        results["error"] = str(e)
        results["success"] = False
        logger.error(f"Authentication Security Test Failed: {e}")

    return results


@mcp.tool()
def test_rate_limiting(
    base_url: str = "http://localhost:8000",
    endpoint: str = "/api/v1/search",
    rate_limit: int = 100,
) -> dict[str, Any]:
    """Test rate limiting implementation.

    Args:
    ----
        base_url: Base URL to test
        endpoint: Endpoint to test
        rate_limit: Expected rate limit

    Returns:
    -------
        Rate limiting test results

    """
    results = {
        "base_url": base_url,
        "endpoint": endpoint,
        "expected_rate_limit": rate_limit,
        "timestamp": datetime.now().isoformat(),
        "requests_sent": 0,
        "successful_requests": 0,
        "rate_limited_requests": 0,
    }

    try:
        url = f"{base_url}{endpoint}"

        # Send requests at a rate that should trigger rate limiting
        for i in range(rate_limit + 20):  # Send more than the limit
            try:
                response = requests.get(url, params={"q": f"test_query_{i}"}, timeout=5)
                results["requests_sent"] += 1

                if response.status_code == 200:
                    results["successful_requests"] += 1
                elif response.status_code == 429:  # Too Many Requests
                    results["rate_limited_requests"] += 1

                # Small delay to avoid overwhelming the server
                time.sleep(0.01)

            except Exception as e:
                logger.warning(f"Request {i} failed: {e}")

        # Calculate metrics
        results["rate_limiting_effectiveness"] = (
            results["rate_limited_requests"] / results["requests_sent"]
            if results["requests_sent"] > 0
            else 0
        )
        results["success"] = True

        logger.info(
            f"Rate Limiting Test: {results['rate_limited_requests']} requests rate limited out of {results['requests_sent']}",
        )

    except Exception as e:
        results["error"] = str(e)
        results["success"] = False
        logger.error(f"Rate Limiting Test Failed: {e}")

    return results


@mcp.tool()
def test_ssl_tls_security(
    base_url: str = "https://localhost:8000",
) -> dict[str, Any]:
    """Test SSL/TLS security configuration.

    Args:
    ----
        base_url: HTTPS URL to test

    Returns:
    -------
        SSL/TLS security test results

    """
    results = {
        "base_url": base_url,
        "timestamp": datetime.now().isoformat(),
        "ssl_info": {},
        "vulnerabilities": [],
    }

    try:
        import socket
        import ssl
        from urllib.parse import urlparse

        parsed_url = urlparse(base_url)
        hostname = parsed_url.hostname
        port = parsed_url.port or 443

        # Test SSL connection
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()
                version = ssock.version()

                results["ssl_info"] = {
                    "version": version,
                    "cipher": cipher,
                    "certificate": {
                        "subject": dict(x[0] for x in cert.get("subject", [])),
                        "issuer": dict(x[0] for x in cert.get("issuer", [])),
                        "not_before": cert.get("notBefore"),
                        "not_after": cert.get("notAfter"),
                    },
                }

                # Check for vulnerabilities
                if version in ["SSLv2", "SSLv3", "TLSv1", "TLSv1.1"]:
                    results["vulnerabilities"].append(
                        {
                            "type": "Weak SSL/TLS Version",
                            "version": version,
                            "severity": "High",
                        },
                    )

                if cipher and cipher[1] in ["RC4", "DES", "3DES"]:
                    results["vulnerabilities"].append(
                        {
                            "type": "Weak Cipher Suite",
                            "cipher": cipher[1],
                            "severity": "Medium",
                        },
                    )

        results["vulnerability_count"] = len(results["vulnerabilities"])
        results["success"] = True

        logger.info(
            f"SSL/TLS Security Test: {results['vulnerability_count']} vulnerabilities found",
        )

    except Exception as e:
        results["error"] = str(e)
        results["success"] = False
        logger.error(f"SSL/TLS Security Test Failed: {e}")

    return results


@mcp.tool()
def test_headers_security(
    base_url: str = "http://localhost:8000",
    endpoints: list[str] | None = None,
) -> dict[str, Any]:
    """Test security headers.

    Args:
    ----
        base_url: Base URL to test
        endpoints: List of endpoints to test

    Returns:
    -------
        Security headers test results

    """
    if endpoints is None:
        endpoints = ["/", "/api/v1/status", "/api/v1/search"]

    results = {
        "base_url": base_url,
        "endpoints": endpoints,
        "timestamp": datetime.now().isoformat(),
        "missing_headers": [],
        "vulnerabilities": [],
    }

    # Required security headers
    required_headers = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": ["DENY", "SAMEORIGIN"],
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": None,  # Should be present for HTTPS
        "Content-Security-Policy": None,
        "Referrer-Policy": None,
    }

    try:
        for endpoint in endpoints:
            url = f"{base_url}{endpoint}"

            try:
                response = requests.get(url, timeout=10)
                headers = response.headers

                endpoint_results = {
                    "endpoint": endpoint,
                    "status_code": response.status_code,
                    "missing_headers": [],
                    "vulnerabilities": [],
                }

                # Check for required headers
                for header, expected_value in required_headers.items():
                    if header not in headers:
                        endpoint_results["missing_headers"].append(header)
                    elif expected_value and headers[header] not in expected_value:
                        endpoint_results["vulnerabilities"].append(
                            {
                                "header": header,
                                "expected": expected_value,
                                "actual": headers[header],
                            },
                        )

                # Check for dangerous headers
                dangerous_headers = ["Server", "X-Powered-By", "X-AspNet-Version"]
                for header in dangerous_headers:
                    if header in headers:
                        endpoint_results["vulnerabilities"].append(
                            {
                                "header": header,
                                "issue": "Information disclosure",
                                "value": headers[header],
                            },
                        )

                results["missing_headers"].append(endpoint_results)

            except Exception as e:
                logger.warning(f"Header test failed for {endpoint}: {e}")

        # Calculate summary
        total_missing = sum(
            len(ep["missing_headers"]) for ep in results["missing_headers"]
        )
        total_vulnerabilities = sum(
            len(ep["vulnerabilities"]) for ep in results["missing_headers"]
        )

        results["summary"] = {
            "total_missing_headers": total_missing,
            "total_vulnerabilities": total_vulnerabilities,
            "endpoints_tested": len(endpoints),
        }
        results["success"] = True

        logger.info(
            f"Security Headers Test: {total_missing} missing headers, {total_vulnerabilities} vulnerabilities",
        )

    except Exception as e:
        results["error"] = str(e)
        results["success"] = False
        logger.error(f"Security Headers Test Failed: {e}")

    return results


@mcp.tool()
def run_comprehensive_security_test() -> dict[str, Any]:
    """Run comprehensive security testing suite.

    Returns
    -------
        Complete security test results

    """
    logger.info("🚀 Starting Comprehensive Security Testing Suite")

    test_results = {
        "timestamp": datetime.now().isoformat(),
        "tests": {},
        "overall_success": True,
        "summary": {},
    }

    try:
        # Test SQL Injection
        logger.info("Testing SQL Injection vulnerabilities...")
        sql_results = test_sql_injection()
        test_results["tests"]["sql_injection"] = sql_results

        # Test XSS vulnerabilities
        logger.info("Testing XSS vulnerabilities...")
        xss_results = test_xss_vulnerabilities()
        test_results["tests"]["xss"] = xss_results

        # Test Authentication Security
        logger.info("Testing Authentication Security...")
        auth_results = test_authentication_security()
        test_results["tests"]["authentication"] = auth_results

        # Test Rate Limiting
        logger.info("Testing Rate Limiting...")
        rate_results = test_rate_limiting()
        test_results["tests"]["rate_limiting"] = rate_results

        # Test SSL/TLS Security
        logger.info("Testing SSL/TLS Security...")
        ssl_results = test_ssl_tls_security()
        test_results["tests"]["ssl_tls"] = ssl_results

        # Test Security Headers
        logger.info("Testing Security Headers...")
        headers_results = test_headers_security()
        test_results["tests"]["security_headers"] = headers_results

        # Calculate overall security score
        total_vulnerabilities = 0
        for test_result in test_results["tests"].values():
            if "vulnerability_count" in test_result:
                total_vulnerabilities += test_result["vulnerability_count"]
            elif "vulnerabilities" in test_result:
                total_vulnerabilities += len(test_result["vulnerabilities"])

        test_results["summary"] = {
            "total_vulnerabilities": total_vulnerabilities,
            "security_score": max(
                0,
                100 - total_vulnerabilities * 10,
            ),  # Simple scoring
            "overall_success": total_vulnerabilities == 0,
        }

        logger.info(
            f"✅ Security Testing Complete: {total_vulnerabilities} vulnerabilities found",
        )

    except Exception as e:
        test_results["error"] = str(e)
        test_results["overall_success"] = False
        logger.error(f"Comprehensive Security Test Failed: {e}")

    return test_results


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
