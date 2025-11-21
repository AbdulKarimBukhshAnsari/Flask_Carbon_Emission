#!/usr/bin/env python3
"""
Carbon Emission Calculator
Calculates carbon footprint based on network usage, CPU, and energy consumption
"""

import psutil
import time

class CarbonCalculator:
    def __init__(self):
        # Carbon intensity factors (kg CO2 per kWh)
        self.GRID_CARBON_INTENSITY = 0.5  # Average global grid
        
        # Power consumption estimates
        self.CPU_TDP = 65  # Watts (typical desktop CPU)
        self.NETWORK_POWER_PER_GB = 0.06  # kWh per GB transmitted
        self.IDLE_POWER = 50  # Watts for system idle
        
        self.start_time = time.time()
        self.total_carbon = 0
        
    def calculate_cpu_power(self):
        """Calculate CPU power consumption based on usage"""
        cpu_percent = psutil.cpu_percent(interval=1)
        # Power = TDP * (CPU_usage/100)
        power_watts = self.IDLE_POWER + (self.CPU_TDP * (cpu_percent / 100))
        return power_watts
    
    def calculate_network_carbon(self, bytes_transferred):
        """Calculate carbon emissions from network traffic"""
        gb_transferred = bytes_transferred / (1024 ** 3)
        energy_kwh = gb_transferred * self.NETWORK_POWER_PER_GB
        carbon_kg = energy_kwh * self.GRID_CARBON_INTENSITY
        return carbon_kg * 1000  # Convert to grams
    
    def calculate_total_energy(self, duration_hours):
        """Calculate total energy consumption"""
        cpu_power = self.calculate_cpu_power()
        energy_kwh = (cpu_power * duration_hours) / 1000
        return energy_kwh
    
    def get_carbon_metrics(self, network_stats):
        """Get comprehensive carbon metrics"""
        # Calculate runtime
        runtime_hours = (time.time() - self.start_time) / 3600
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_power = self.calculate_cpu_power()
        cpu_energy = self.calculate_total_energy(runtime_hours)
        cpu_carbon = cpu_energy * self.GRID_CARBON_INTENSITY * 1000  # grams
        
        # Network metrics
        total_bytes = network_stats.get('total_bytes', 0)
        network_carbon = self.calculate_network_carbon(total_bytes)
        
        # Memory metrics
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Total carbon
        total_carbon = cpu_carbon + network_carbon
        self.total_carbon = total_carbon
        
        return {
            'cpu': {
                'usage_percent': cpu_percent,
                'power_watts': cpu_power,
                'energy_kwh': cpu_energy,
                'carbon_grams': cpu_carbon
            },
            'network': {
                'total_gb': total_bytes / (1024 ** 3),
                'carbon_grams': network_carbon
            },
            'memory': {
                'usage_percent': memory_percent,
                'used_gb': memory.used / (1024 ** 3),
                'total_gb': memory.total / (1024 ** 3)
            },
            'total': {
                'carbon_grams': total_carbon,
                'carbon_kg': total_carbon / 1000,
                'runtime_hours': runtime_hours,
                'total_energy_kwh': cpu_energy
            }
        }
    
    def estimate_savings(self, optimization_type):
        """Estimate carbon savings for different optimization strategies"""
        savings = {
            'reduce_cpu': {
                'name': 'Reduce CPU Usage',
                'description': 'Limit background processes and CPU-intensive tasks',
                'potential_reduction_percent': 30,
                'estimated_savings_grams': self.total_carbon * 0.30
            },
            'optimize_network': {
                'name': 'Optimize Network Traffic',
                'description': 'Compress data, cache content, reduce unnecessary requests',
                'potential_reduction_percent': 25,
                'estimated_savings_grams': self.total_carbon * 0.25
            },
            'power_management': {
                'name': 'Enable Power Management',
                'description': 'Use power-saving modes, reduce screen brightness, sleep idle processes',
                'potential_reduction_percent': 40,
                'estimated_savings_grams': self.total_carbon * 0.40
            }
        }
        
        return savings.get(optimization_type, savings['reduce_cpu'])

if __name__ == "__main__":
    calc = CarbonCalculator()
    time.sleep(2)
    
    # Test calculation
    test_stats = {'total_bytes': 1024 * 1024 * 1024}  # 1 GB
    metrics = calc.get_carbon_metrics(test_stats)
    
    print("\n[Carbon Metrics]")
    print(f"CPU Carbon: {metrics['cpu']['carbon_grams']:.2f}g")
    print(f"Network Carbon: {metrics['network']['carbon_grams']:.2f}g")
    print(f"Total Carbon: {metrics['total']['carbon_grams']:.2f}g")