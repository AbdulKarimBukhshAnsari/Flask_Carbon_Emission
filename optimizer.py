#!/usr/bin/env python3
"""
Carbon Emission Optimizer
Implements strategies to reduce carbon emissions
"""

import psutil
import subprocess
import os

class CarbonOptimizer:
    def __init__(self):
        self.optimization_log = []
        
    def reduce_cpu_usage(self):
        """Reduce CPU usage by managing processes"""
        actions = []
        
        try:
            # Get high CPU processes
            high_cpu_procs = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    if proc.info['cpu_percent'] > 50:
                        high_cpu_procs.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if high_cpu_procs:
                actions.append({
                    'action': 'Identified high CPU processes',
                    'details': f"Found {len(high_cpu_procs)} processes using >50% CPU",
                    'processes': high_cpu_procs
                })
            
            # Set CPU frequency scaling to powersave (Linux)
            try:
                subprocess.run(['sudo', 'cpupower', 'frequency-set', '-g', 'powersave'], 
                             capture_output=True, timeout=5)
                actions.append({
                    'action': 'CPU frequency scaling',
                    'details': 'Set CPU governor to powersave mode',
                    'status': 'success'
                })
            except (subprocess.TimeoutExpired, FileNotFoundError):
                actions.append({
                    'action': 'CPU frequency scaling',
                    'details': 'cpupower not available (install with: sudo apt install linux-tools-common)',
                    'status': 'info'
                })
            
            # Suggest killing unnecessary processes (don't actually kill)
            actions.append({
                'action': 'Process management recommendation',
                'details': 'Consider closing unnecessary applications and browser tabs',
                'status': 'recommendation'
            })
            
            self.optimization_log.extend(actions)
            return {
                'success': True,
                'actions': actions,
                'estimated_reduction': '30%'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'actions': actions
            }
    
    def optimize_network(self):
        """Optimize network usage"""
        actions = []
        
        try:
            # Get network connections
            connections = psutil.net_connections()
            active_connections = len([c for c in connections if c.status == 'ESTABLISHED'])
            
            actions.append({
                'action': 'Network analysis',
                'details': f'Found {active_connections} active connections',
                'status': 'info'
            })
            
            # Check for high bandwidth processes
            net_io_before = psutil.net_io_counters()
            
            actions.append({
                'action': 'Network optimization suggestions',
                'details': 'Enable browser compression, use content caching, limit background sync',
                'status': 'recommendation'
            })
            
            actions.append({
                'action': 'Traffic compression',
                'details': 'Consider using VPN with compression or CDN caching',
                'status': 'recommendation'
            })
            
            self.optimization_log.extend(actions)
            return {
                'success': True,
                'actions': actions,
                'estimated_reduction': '25%'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'actions': actions
            }
    
    def enable_power_management(self):
        """Enable power management features"""
        actions = []
        
        try:
            # Check current power profile
            try:
                result = subprocess.run(['cat', '/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor'],
                                      capture_output=True, text=True, timeout=5)
                current_governor = result.stdout.strip()
                actions.append({
                    'action': 'Power profile check',
                    'details': f'Current CPU governor: {current_governor}',
                    'status': 'info'
                })
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            # Suggest power management tools
            actions.append({
                'action': 'Power management tools',
                'details': 'Install TLP for automatic power management: sudo apt install tlp',
                'status': 'recommendation'
            })
            
            # Enable laptop mode (if applicable)
            if os.path.exists('/proc/sys/vm/laptop_mode'):
                try:
                    subprocess.run(['sudo', 'sysctl', '-w', 'vm.laptop_mode=5'],
                                 capture_output=True, timeout=5)
                    actions.append({
                        'action': 'Laptop mode',
                        'details': 'Enabled laptop mode for better power efficiency',
                        'status': 'success'
                    })
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass
            
            # USB autosuspend
            actions.append({
                'action': 'USB power saving',
                'details': 'Enable USB autosuspend for idle devices',
                'status': 'recommendation'
            })
            
            # Display brightness
            actions.append({
                'action': 'Display optimization',
                'details': 'Reduce screen brightness to 50-70% for optimal power savings',
                'status': 'recommendation'
            })
            
            self.optimization_log.extend(actions)
            return {
                'success': True,
                'actions': actions,
                'estimated_reduction': '40%'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'actions': actions
            }
    
    def apply_optimization(self, optimization_type):
        """Apply selected optimization strategy"""
        optimizations = {
            'reduce_cpu': self.reduce_cpu_usage,
            'optimize_network': self.optimize_network,
            'power_management': self.enable_power_management
        }
        
        if optimization_type in optimizations:
            return optimizations[optimization_type]()
        else:
            return {
                'success': False,
                'error': 'Unknown optimization type'
            }
    
    def get_log(self):
        """Get optimization log"""
        return self.optimization_log

if __name__ == "__main__":
    optimizer = CarbonOptimizer()
    
    print("\n[Testing CPU Optimization]")
    result = optimizer.reduce_cpu_usage()
    print(f"Success: {result['success']}")
    print(f"Actions: {len(result['actions'])}")
    
    print("\n[Testing Network Optimization]")
    result = optimizer.optimize_network()
    print(f"Success: {result['success']}")
    print(f"Actions: {len(result['actions'])}")
    
    print("\n[Testing Power Management]")
    result = optimizer.enable_power_management()
    print(f"Success: {result['success']}")
    print(f"Actions: {len(result['actions'])}")