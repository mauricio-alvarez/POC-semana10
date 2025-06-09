#!/usr/bin/env python3
"""
Pokemon API Monitoring Bot
Console application for monitoring API performance and availability
"""

import os
import sys
import time
import json
import requests
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from dataclasses import dataclass
from collections import defaultdict
import threading
import subprocess


@dataclass
class RequestResult:
    """Data class to store request results"""
    timestamp: datetime
    status_code: int
    response_time: float
    endpoint: str
    success: bool


class APIMonitor:
    """Main monitoring class for Pokemon API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[RequestResult] = []
        self.running = False
        
    def test_endpoint(self, endpoint: str, method: str = "POST", payload: dict = None) -> RequestResult:
        """Test a single endpoint and return result"""
        start_time = time.time()
        
        try:
            if method == "POST":
                response = requests.post(
                    f"{self.base_url}{endpoint}",
                    json=payload or {"Pokemon_Name": "pikachu"},
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
            else:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=30)
            
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            success = response.status_code == 200
            
            return RequestResult(
                timestamp=datetime.now(),
                status_code=response.status_code,
                response_time=response_time,
                endpoint=endpoint,
                success=success
            )
            
        except requests.RequestException as e:
            response_time = (time.time() - start_time) * 1000
            return RequestResult(
                timestamp=datetime.now(),
                status_code=500,
                response_time=response_time,
                endpoint=endpoint,
                success=False
            )
    
    def check_latency(self, endpoint: str = "/poke/search", duration_minutes: int = 5) -> Dict:
        """Check latency for specified duration"""
        print(f"\n🔍 Checking latency for {endpoint} during {duration_minutes} minutes...")
        print("Press Ctrl+C to stop early\n")
        
        results = []
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        try:
            while time.time() < end_time:
                result = self.test_endpoint(endpoint)
                results.append(result)
                
                status_icon = "✅" if result.success else "❌"
                print(f"{status_icon} {result.timestamp.strftime('%H:%M:%S')} | "
                      f"Status: {result.status_code} | "
                      f"Latency: {result.response_time:.2f}ms")
                
                time.sleep(2)  # Wait 2 seconds between requests
                
        except KeyboardInterrupt:
            print("\n⏹️  Latency check stopped by user")
        
        if results:
            latencies = [r.response_time for r in results]
            return {
                "endpoint": endpoint,
                "duration_minutes": duration_minutes,
                "total_requests": len(results),
                "avg_latency": statistics.mean(latencies),
                "min_latency": min(latencies),
                "max_latency": max(latencies),
                "median_latency": statistics.median(latencies),
                "success_rate": sum(1 for r in results if r.success) / len(results) * 100
            }
        return {}
    
    def check_availability(self, endpoint: str = "/poke/search", days: int = 1) -> Dict:
        """Check availability for specified number of days"""
        print(f"\n📊 Checking availability for {endpoint} over {days} day(s)...")
        print("Simulating historical data with current tests...\n")
        
        # Simulate data collection over time (in real implementation, you'd query historical data)
        total_requests = min(100, days * 50)  # Simulate requests per day
        success_count = 0
        error_count = 0
        
        for i in range(total_requests):
            result = self.test_endpoint(endpoint)
            
            if result.status_code == 200:
                success_count += 1
                status = "✅ SUCCESS"
            elif result.status_code >= 500:
                error_count += 1
                status = "❌ ERROR"
            else:
                status = "⚠️  OTHER"
            
            print(f"Request {i+1:3d}/{total_requests} | {status} | "
                  f"Code: {result.status_code} | "
                  f"Time: {result.response_time:.2f}ms")
            
            if i < total_requests - 1:
                time.sleep(0.5)  # Small delay between requests
        
        # Calculate availability
        total_relevant = success_count + error_count
        if total_relevant > 0:
            availability = (success_count / total_relevant) * 100
        else:
            availability = 0
        
        return {
            "endpoint": endpoint,
            "days": days,
            "total_requests": total_requests,
            "success_count": success_count,
            "error_count": error_count,
            "availability_percentage": availability,
            "success_rate": (success_count / total_requests) * 100 if total_requests > 0 else 0
        }
    
    def render_graph(self, data_type: str = "latency", endpoint: str = "/poke/search", days: int = 7):
        """Render ASCII graph for trends"""
        print(f"\n📈 Rendering {data_type} graph for {endpoint} over {days} days...")
        print("Generating sample data...\n")
        
        # Generate sample data points
        data_points = []
        labels = []
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i-1)
            labels.append(date.strftime("%m/%d"))
            
            if data_type.lower() == "latency":
                # Simulate latency data (50-200ms range)
                value = 50 + (i * 10) + (i % 3 * 20)
                data_points.append(min(value, 200))
            else:  # availability
                # Simulate availability data (85-100% range)
                value = 85 + (i * 2) + (i % 2 * 5)
                data_points.append(min(value, 100))
        
        self._draw_ascii_graph(data_points, labels, data_type)
    
    def _draw_ascii_graph(self, data: List[float], labels: List[str], data_type: str):
        """Draw ASCII line graph"""
        if not data:
            print("No data to display")
            return
        
        # Normalize data for display
        max_val = max(data)
        min_val = min(data)
        height = 15  # Graph height in characters
        width = len(data)
        
        # Create the graph grid
        graph = [[' ' for _ in range(width)] for _ in range(height)]
        
        # Plot the data points
        for i, value in enumerate(data):
            if max_val > min_val:
                normalized = (value - min_val) / (max_val - min_val)
                y = int((height - 1) * (1 - normalized))  # Invert Y axis
            else:
                y = height // 2
            
            graph[y][i] = '●'
            
            # Draw connecting lines
            if i > 0:
                prev_value = data[i-1]
                if max_val > min_val:
                    prev_normalized = (prev_value - min_val) / (max_val - min_val)
                    prev_y = int((height - 1) * (1 - prev_normalized))
                else:
                    prev_y = height // 2
                
                # Draw line between points
                start_y, end_y = sorted([prev_y, y])
                for line_y in range(start_y, end_y + 1):
                    if graph[line_y][i-1] == ' ':
                        graph[line_y][i-1] = '│' if start_y != end_y else '●'
        
        # Print the title
        unit = "ms" if data_type.lower() == "latency" else "%"
        print(f"{data_type.title()} Trend Graph ({min_val:.1f}-{max_val:.1f} {unit})")
        print("─" * (width + 10))
        
        # Print the graph
        for i, row in enumerate(graph):
            # Y-axis labels
            if max_val > min_val:
                y_value = max_val - (i / (height - 1)) * (max_val - min_val)
            else:
                y_value = max_val
            
            print(f"{y_value:6.1f} │{''.join(row)}")
        
        # Print X-axis
        print("       └" + "─" * width)
        print("        " + "".join(f"{label:>4}" for label in labels))
        
        # Print statistics
        avg_val = sum(data) / len(data)
        print(f"\nStatistics:")
        print(f"  Average: {avg_val:.2f} {unit}")
        print(f"  Min: {min_val:.2f} {unit}")
        print(f"  Max: {max_val:.2f} {unit}")


class MonitoringBot:
    """Main bot class with console menu"""
    
    def __init__(self):
        self.monitor = APIMonitor()
        self.running = True
    
    def display_header(self):
        """Display bot header"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                 🤖 POKEMON API MONITORING BOT                ║")
        print("║                        Version 1.0                          ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print(f"📡 Base URL: {self.monitor.base_url}")
        print(f"⏰ Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("─" * 64)
    
    def display_menu(self):
        """Display main menu options"""
        print("\n📋 MAIN MENU - Select an option:")
        print("─" * 40)
        print("1️⃣  Check Latency")
        print("2️⃣  Check Availability") 
        print("3️⃣  Render Latency Graph")
        print("4️⃣  Render Availability Graph")
        print("5️⃣  Run Load Test (Locust)")
        print("6️⃣  Settings")
        print("0️⃣  Exit")
        print("─" * 40)
    
    def handle_check_latency(self):
        """Handle latency check option"""
        print("\n🔍 LATENCY CHECK")
        print("─" * 20)
        
        try:
            endpoint = input("Enter endpoint [/poke/search]: ").strip() or "/poke/search"
            duration = int(input("Enter duration in minutes [5]: ") or "5")
            
            result = self.monitor.check_latency(endpoint, duration)
            
            if result:
                print(f"\n📊 LATENCY REPORT")
                print("─" * 30)
                print(f"Endpoint: {result['endpoint']}")
                print(f"Duration: {result['duration_minutes']} minutes")
                print(f"Total Requests: {result['total_requests']}")
                print(f"Average Latency: {result['avg_latency']:.2f}ms")
                print(f"Min Latency: {result['min_latency']:.2f}ms")
                print(f"Max Latency: {result['max_latency']:.2f}ms")
                print(f"Median Latency: {result['median_latency']:.2f}ms")
                print(f"Success Rate: {result['success_rate']:.1f}%")
        
        except ValueError:
            print("❌ Invalid input. Please enter valid numbers.")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def handle_check_availability(self):
        """Handle availability check option"""
        print("\n📊 AVAILABILITY CHECK")
        print("─" * 25)
        
        try:
            endpoint = input("Enter endpoint [/poke/search]: ").strip() or "/poke/search"
            days = int(input("Enter number of days [1]: ") or "1")
            
            result = self.monitor.check_availability(endpoint, days)
            
            if result:
                print(f"\n📈 AVAILABILITY REPORT")
                print("─" * 35)
                print(f"Endpoint: {result['endpoint']}")
                print(f"Period: {result['days']} day(s)")
                print(f"Total Requests: {result['total_requests']}")
                print(f"Successful Requests: {result['success_count']}")
                print(f"Error Requests (5xx): {result['error_count']}")
                print(f"Availability: {result['availability_percentage']:.2f}%")
                print(f"Success Rate: {result['success_rate']:.1f}%")
                
                # Display availability status
                if result['availability_percentage'] >= 99:
                    print("🟢 Status: EXCELLENT")
                elif result['availability_percentage'] >= 95:
                    print("🟡 Status: GOOD")
                else:
                    print("🔴 Status: NEEDS ATTENTION")
        
        except ValueError:
            print("❌ Invalid input. Please enter valid numbers.")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def handle_render_graph(self, graph_type: str):
        """Handle graph rendering"""
        print(f"\n📈 RENDER {graph_type.upper()} GRAPH")
        print("─" * 30)
        
        try:
            endpoint = input("Enter endpoint [/poke/search]: ").strip() or "/poke/search"
            days = int(input("Enter number of days [7]: ") or "7")
            
            self.monitor.render_graph(graph_type, endpoint, days)
        
        except ValueError:
            print("❌ Invalid input. Please enter valid numbers.")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def handle_load_test(self):
        """Handle load test execution"""
        print("\n🚀 LOAD TEST WITH LOCUST")
        print("─" * 30)
        
        print("Available test configurations:")
        print("1. Light test (50 users, 5 minutes)")
        print("2. Medium test (100 users, 10 minutes)")
        print("3. Heavy test (200 users, 15 minutes)")
        print("4. Custom configuration")
        print("5. Web UI mode")
        
        try:
            choice = input("\nSelect configuration [1]: ").strip() or "1"
            
            if choice == "1":
                cmd = ["locust", "--host=http://localhost:8000", "--users=50", "--spawn-rate=5", "--run-time=300s", "--headless"]
            elif choice == "2":
                cmd = ["locust", "--host=http://localhost:8000", "--users=100", "--spawn-rate=10", "--run-time=600s", "--headless"]
            elif choice == "3":
                cmd = ["locust", "--host=http://localhost:8000", "--users=200", "--spawn-rate=20", "--run-time=900s", "--headless"]
            elif choice == "4":
                users = int(input("Number of users: "))
                spawn_rate = int(input("Spawn rate: "))
                duration = input("Duration (e.g., 300s): ")
                cmd = ["locust", "--host=http://localhost:8000", f"--users={users}", f"--spawn-rate={spawn_rate}", f"--run-time={duration}", "--headless"]
            elif choice == "5":
                print("Starting Locust Web UI...")
                print("Open http://localhost:8089 in your browser")
                cmd = ["locust", "--host=http://localhost:8000"]
            else:
                print("❌ Invalid choice")
                return
            
            print(f"\n🏃 Running: {' '.join(cmd)}")
            print("Press Ctrl+C to stop the test")
            
            # Execute locust command
            subprocess.run(cmd, cwd=".")
            
        except ValueError:
            print("❌ Invalid input. Please enter valid numbers.")
        except FileNotFoundError:
            print("❌ Locust not found. Please install it with: pip install locust")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def handle_settings(self):
        """Handle settings configuration"""
        print("\n⚙️  SETTINGS")
        print("─" * 15)
        
        print(f"Current base URL: {self.monitor.base_url}")
        new_url = input("Enter new base URL (or press Enter to keep current): ").strip()
        
        if new_url:
            self.monitor.base_url = new_url
            print(f"✅ Base URL updated to: {new_url}")
        
        input("\nPress Enter to continue...")
    
    def run(self):
        """Main bot loop"""
        while self.running:
            self.display_header()
            self.display_menu()
            
            try:
                choice = input("\n🤖 Enter your choice: ").strip()
                
                if choice == "1":
                    self.handle_check_latency()
                elif choice == "2":
                    self.handle_check_availability()
                elif choice == "3":
                    self.handle_render_graph("latency")
                elif choice == "4":
                    self.handle_render_graph("availability")
                elif choice == "5":
                    self.handle_load_test()
                elif choice == "6":
                    self.handle_settings()
                elif choice == "0":
                    print("\n👋 Goodbye! Thanks for using Pokemon API Monitoring Bot!")
                    self.running = False
                else:
                    print("❌ Invalid choice. Please select a valid option.")
                    time.sleep(2)
            
            except KeyboardInterrupt:
                print("\n\n⏹️  Bot interrupted. Goodbye!")
                self.running = False
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                input("Press Enter to continue...")


if __name__ == "__main__":
    print("🚀 Starting Pokemon API Monitoring Bot...")
    bot = MonitoringBot()
    bot.run()