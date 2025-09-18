#!/usr/bin/env python3
"""Performance Monitoring MCP Server for P9 Performance Optimization & P11 Integration Testing.
Provides comprehensive performance monitoring and testing capabilities.
"""

import logging
import queue
import threading
import time
from datetime import datetime
from typing import Any

import psutil
import requests
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Performance Monitoring Server")


class PerformanceMonitor:
    def __init__(self) -> None:
        self.monitoring = False
        self.metrics_queue = queue.Queue()
        self.monitoring_thread = None

    def start_monitoring(self, duration: int = 60):
        """Start performance monitoring for specified duration."""
        self.monitoring = True
        self.monitoring_thread = threading.Thread(
            target=self._collect_metrics,
            args=(duration,),
        )
        self.monitoring_thread.start()
        return {"status": "monitoring_started", "duration": duration}

    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        return {"status": "monitoring_stopped"}

    def _collect_metrics(self, duration: int) -> None:
        """Collect performance metrics in background thread."""
        start_time = time.time()

        while self.monitoring and (time.time() - start_time) < duration:
            try:
                # System metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage("/")

                # Network metrics
                network = psutil.net_io_counters()

                # Process metrics
                process = psutil.Process()
                process_memory = process.memory_info()
                process_cpu = process.cpu_percent()

                metrics = {
                    "timestamp": datetime.now().isoformat(),
                    "system": {
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory.percent,
                        "memory_used_gb": memory.used / (1024**3),
                        "memory_available_gb": memory.available / (1024**3),
                        "disk_percent": disk.percent,
                        "disk_used_gb": disk.used / (1024**3),
                        "disk_free_gb": disk.free / (1024**3),
                    },
                    "network": {
                        "bytes_sent": network.bytes_sent,
                        "bytes_recv": network.bytes_recv,
                        "packets_sent": network.packets_sent,
                        "packets_recv": network.packets_recv,
                    },
                    "process": {
                        "cpu_percent": process_cpu,
                        "memory_rss_mb": process_memory.rss / (1024**2),
                        "memory_vms_mb": process_memory.vms / (1024**2),
                    },
                }

                self.metrics_queue.put(metrics)
                time.sleep(1)  # Collect metrics every second

            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
                time.sleep(1)

    def get_metrics(self) -> list[dict]:
        """Get collected metrics."""
        metrics = []
        while not self.metrics_queue.empty():
            try:
                metrics.append(self.metrics_queue.get_nowait())
            except queue.Empty:
                break
        return metrics


# Global performance monitor instance
perf_monitor = PerformanceMonitor()


@mcp.tool()
def start_performance_monitoring(duration: int = 60) -> dict[str, Any]:
    """Start performance monitoring for specified duration.

    Args:
    ----
        duration: Monitoring duration in seconds

    Returns:
    -------
        Monitoring start status

    """
    try:
        result = perf_monitor.start_monitoring(duration)
        logger.info(f"Performance monitoring started for {duration} seconds")
        return result
    except Exception as e:
        logger.error(f"Failed to start performance monitoring: {e}")
        return {"error": str(e), "success": False}


@mcp.tool()
def stop_performance_monitoring() -> dict[str, Any]:
    """Stop performance monitoring.

    Returns
    -------
        Monitoring stop status

    """
    try:
        result = perf_monitor.stop_monitoring()
        logger.info("Performance monitoring stopped")
        return result
    except Exception as e:
        logger.error(f"Failed to stop performance monitoring: {e}")
        return {"error": str(e), "success": False}


@mcp.tool()
def get_performance_metrics() -> dict[str, Any]:
    """Get collected performance metrics.

    Returns
    -------
        Performance metrics data

    """
    try:
        metrics = perf_monitor.get_metrics()

        if not metrics:
            return {"message": "No metrics collected", "metrics": []}

        # Calculate summary statistics
        cpu_values = [m["system"]["cpu_percent"] for m in metrics]
        memory_values = [m["system"]["memory_percent"] for m in metrics]

        summary = {
            "total_samples": len(metrics),
            "duration_seconds": len(metrics),
            "cpu": {
                "avg": sum(cpu_values) / len(cpu_values),
                "max": max(cpu_values),
                "min": min(cpu_values),
            },
            "memory": {
                "avg": sum(memory_values) / len(memory_values),
                "max": max(memory_values),
                "min": min(memory_values),
            },
        }

        return {
            "summary": summary,
            "metrics": metrics,
            "success": True,
        }

    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        return {"error": str(e), "success": False}


@mcp.tool()
def test_api_performance(
    url: str = "http://localhost:8000/api/v1/status",
    requests_count: int = 10,
    concurrent_requests: int = 5,
) -> dict[str, Any]:
    """Test API performance with multiple requests.

    Args:
    ----
        url: API endpoint to test
        requests_count: Total number of requests
        concurrent_requests: Number of concurrent requests

    Returns:
    -------
        API performance test results

    """
    results = {
        "url": url,
        "requests_count": requests_count,
        "concurrent_requests": concurrent_requests,
        "timestamp": datetime.now().isoformat(),
    }

    try:
        import concurrent.futures

        def make_request():
            start_time = time.time()
            try:
                response = requests.get(url, timeout=10)
                end_time = time.time()
                return {
                    "status_code": response.status_code,
                    "latency": end_time - start_time,
                    "success": response.status_code == 200,
                    "response_size": len(response.content),
                }
            except Exception as e:
                end_time = time.time()
                return {
                    "status_code": 0,
                    "latency": end_time - start_time,
                    "success": False,
                    "error": str(e),
                }

        # Execute requests with concurrency
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=concurrent_requests,
        ) as executor:
            futures = [executor.submit(make_request) for _ in range(requests_count)]
            request_results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        total_time = time.time() - start_time

        # Calculate metrics
        successful_requests = [r for r in request_results if r["success"]]
        failed_requests = [r for r in request_results if not r["success"]]

        latencies = [r["latency"] for r in request_results]

        results.update(
            {
                "total_time": total_time,
                "successful_requests": len(successful_requests),
                "failed_requests": len(failed_requests),
                "success_rate": len(successful_requests) / requests_count,
                "avg_latency": sum(latencies) / len(latencies),
                "min_latency": min(latencies),
                "max_latency": max(latencies),
                "requests_per_second": requests_count / total_time,
                "request_results": request_results,
                "success": True,
            },
        )

        logger.info(
            f"API Performance Test: {results['success_rate']:.1%} success rate, {results['avg_latency']:.3f}s avg latency",
        )

    except Exception as e:
        results["error"] = str(e)
        results["success"] = False
        logger.error(f"API Performance Test Failed: {e}")

    return results


@mcp.tool()
def test_database_performance(
    connection_string: str = "postgresql://test:test@localhost:5432/test_db",
    query_count: int = 100,
) -> dict[str, Any]:
    """Test database performance with multiple queries.

    Args:
    ----
        connection_string: Database connection string
        query_count: Number of queries to execute

    Returns:
    -------
        Database performance test results

    """
    results = {
        "connection_string": connection_string,
        "query_count": query_count,
        "timestamp": datetime.now().isoformat(),
    }

    try:
        import psycopg2
        import psycopg2.extras

        # Test connection
        start_time = time.time()
        conn = psycopg2.connect(connection_string)
        connection_time = time.time() - start_time

        if not conn:
            results["error"] = "Failed to connect to database"
            results["success"] = False
            return results

        # Test queries
        query_times = []
        successful_queries = 0

        for i in range(query_count):
            start_time = time.time()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")  # Simple test query
                cursor.fetchone()
                cursor.close()
                query_time = time.time() - start_time
                query_times.append(query_time)
                successful_queries += 1
            except Exception as e:
                query_times.append(0)
                logger.warning(f"Query {i} failed: {e}")

        conn.close()

        # Calculate metrics
        results.update(
            {
                "connection_time": connection_time,
                "successful_queries": successful_queries,
                "failed_queries": query_count - successful_queries,
                "success_rate": successful_queries / query_count,
                "avg_query_time": sum(query_times) / len(query_times),
                "min_query_time": min(query_times),
                "max_query_time": max(query_times),
                "queries_per_second": query_count / sum(query_times),
                "success": True,
            },
        )

        logger.info(
            f"Database Performance Test: {results['success_rate']:.1%} success rate, {results['avg_query_time']:.3f}s avg query time",
        )

    except Exception as e:
        results["error"] = str(e)
        results["success"] = False
        logger.error(f"Database Performance Test Failed: {e}")

    return results


@mcp.tool()
def test_redis_performance(
    redis_url: str = "redis://localhost:6379",
    operations_count: int = 1000,
) -> dict[str, Any]:
    """Test Redis performance with multiple operations.

    Args:
    ----
        redis_url: Redis connection URL
        operations_count: Number of operations to perform

    Returns:
    -------
        Redis performance test results

    """
    results = {
        "redis_url": redis_url,
        "operations_count": operations_count,
        "timestamp": datetime.now().isoformat(),
    }

    try:
        import redis

        # Connect to Redis
        r = redis.from_url(redis_url)

        # Test connection
        start_time = time.time()
        r.ping()
        connection_time = time.time() - start_time

        # Test operations
        operation_times = []
        successful_operations = 0

        for i in range(operations_count):
            start_time = time.time()
            try:
                # Set operation
                r.set(f"test_key_{i}", f"test_value_{i}")
                # Get operation
                r.get(f"test_key_{i}")
                # Delete operation
                r.delete(f"test_key_{i}")

                operation_time = time.time() - start_time
                operation_times.append(operation_time)
                successful_operations += 1

            except Exception as e:
                operation_times.append(0)
                logger.warning(f"Operation {i} failed: {e}")

        # Calculate metrics
        results.update(
            {
                "connection_time": connection_time,
                "successful_operations": successful_operations,
                "failed_operations": operations_count - successful_operations,
                "success_rate": successful_operations / operations_count,
                "avg_operation_time": sum(operation_times) / len(operation_times),
                "min_operation_time": min(operation_times),
                "max_operation_time": max(operation_times),
                "operations_per_second": operations_count / sum(operation_times),
                "success": True,
            },
        )

        logger.info(
            f"Redis Performance Test: {results['success_rate']:.1%} success rate, {results['avg_operation_time']:.3f}s avg operation time",
        )

    except Exception as e:
        results["error"] = str(e)
        results["success"] = False
        logger.error(f"Redis Performance Test Failed: {e}")

    return results


@mcp.tool()
def test_websocket_performance(
    websocket_url: str = "ws://localhost:8000/ws",
    connections_count: int = 10,
    messages_per_connection: int = 10,
) -> dict[str, Any]:
    """Test WebSocket performance with multiple connections.

    Args:
    ----
        websocket_url: WebSocket URL to test
        connections_count: Number of concurrent connections
        messages_per_connection: Messages per connection

    Returns:
    -------
        WebSocket performance test results

    """
    results = {
        "websocket_url": websocket_url,
        "connections_count": connections_count,
        "messages_per_connection": messages_per_connection,
        "timestamp": datetime.now().isoformat(),
    }

    try:
        import asyncio

        import websockets

        async def test_connection(connection_id):
            connection_results = {
                "connection_id": connection_id,
                "messages_sent": 0,
                "messages_received": 0,
                "connection_time": 0,
                "total_time": 0,
                "errors": [],
            }

            try:
                start_time = time.time()
                async with websockets.connect(websocket_url) as websocket:
                    connection_time = time.time() - start_time
                    connection_results["connection_time"] = connection_time

                    # Send and receive messages
                    for i in range(messages_per_connection):
                        message = f"test_message_{connection_id}_{i}"

                        # Send message
                        await websocket.send(message)
                        connection_results["messages_sent"] += 1

                        # Receive response
                        try:
                            await asyncio.wait_for(websocket.recv(), timeout=5.0)
                            connection_results["messages_received"] += 1
                        except TimeoutError:
                            connection_results["errors"].append(
                                f"Timeout on message {i}",
                            )

                    connection_results["total_time"] = time.time() - start_time

            except Exception as e:
                connection_results["errors"].append(str(e))

            return connection_results

        # Run WebSocket tests
        start_time = time.time()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        tasks = [test_connection(i) for i in range(connections_count)]
        connection_results = loop.run_until_complete(asyncio.gather(*tasks))

        total_time = time.time() - start_time

        # Calculate metrics
        total_messages_sent = sum(r["messages_sent"] for r in connection_results)
        total_messages_received = sum(
            r["messages_received"] for r in connection_results
        )
        successful_connections = len([r for r in connection_results if not r["errors"]])

        results.update(
            {
                "total_time": total_time,
                "successful_connections": successful_connections,
                "failed_connections": connections_count - successful_connections,
                "success_rate": successful_connections / connections_count,
                "total_messages_sent": total_messages_sent,
                "total_messages_received": total_messages_received,
                "message_success_rate": (
                    total_messages_received / total_messages_sent
                    if total_messages_sent > 0
                    else 0
                ),
                "messages_per_second": total_messages_sent / total_time,
                "connection_results": connection_results,
                "success": True,
            },
        )

        logger.info(
            f"WebSocket Performance Test: {results['success_rate']:.1%} connection success, {results['messages_per_second']:.1f} msg/s",
        )

    except Exception as e:
        results["error"] = str(e)
        results["success"] = False
        logger.error(f"WebSocket Performance Test Failed: {e}")

    return results


@mcp.tool()
def run_comprehensive_performance_test() -> dict[str, Any]:
    """Run comprehensive performance testing suite.

    Returns
    -------
        Complete performance test results

    """
    logger.info("🚀 Starting Comprehensive Performance Testing Suite")

    test_results = {
        "timestamp": datetime.now().isoformat(),
        "tests": {},
        "overall_success": True,
        "summary": {},
    }

    try:
        # Start performance monitoring
        logger.info("Starting performance monitoring...")
        perf_monitor.start_monitoring(30)  # Monitor for 30 seconds

        # Test API Performance
        logger.info("Testing API Performance...")
        api_results = test_api_performance()
        test_results["tests"]["api_performance"] = api_results

        # Test Database Performance
        logger.info("Testing Database Performance...")
        db_results = test_database_performance()
        test_results["tests"]["database_performance"] = db_results

        # Test Redis Performance
        logger.info("Testing Redis Performance...")
        redis_results = test_redis_performance()
        test_results["tests"]["redis_performance"] = redis_results

        # Test WebSocket Performance
        logger.info("Testing WebSocket Performance...")
        ws_results = test_websocket_performance()
        test_results["tests"]["websocket_performance"] = ws_results

        # Stop monitoring and get metrics
        logger.info("Stopping performance monitoring...")
        perf_monitor.stop_monitoring()
        perf_metrics = get_performance_metrics()
        test_results["tests"]["system_performance"] = perf_metrics

        # Calculate overall success rate
        success_count = sum(
            1 for test in test_results["tests"].values() if test.get("success", False)
        )
        total_tests = len(test_results["tests"])
        success_rate = success_count / total_tests if total_tests > 0 else 0

        test_results["summary"] = {
            "total_tests": total_tests,
            "successful_tests": success_count,
            "success_rate": success_rate,
            "overall_success": success_rate >= 0.8,
        }

        logger.info(f"✅ Performance Testing Complete: {success_rate:.1%} success rate")

    except Exception as e:
        test_results["error"] = str(e)
        test_results["overall_success"] = False
        logger.error(f"Comprehensive Performance Test Failed: {e}")

    return test_results


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
