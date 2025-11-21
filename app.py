#!/usr/bin/env python3
"""
Carbon Emission Monitoring Flask Application
Main application file with API endpoints and graph generation
"""

from flask import Flask, render_template, jsonify, request
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
import time
import threading
import os

from bpf_monitor import BPFNetworkMonitor
from carbon_calculator import CarbonCalculator
from optimizer import CarbonOptimizer

app = Flask(__name__)

# Initialize components
monitor = BPFNetworkMonitor()
calculator = CarbonCalculator()
optimizer = CarbonOptimizer()

# Data storage for graphs
historical_data = {
    'timestamps': [],
    'cpu_usage': [],
    'network_bytes': [],
    'carbon_emissions': [],
    'energy_consumption': []
}

# Track optimization before/after values
optimization_data = {
    'before_carbon_g': None,
    'after_carbon_g': None,
    'reduction_g': None,
    'reduction_percent': None,
    'optimization_applied': False,
    'optimization_type': None
}

# Start monitoring in background
monitoring_active = False

def start_background_monitoring():
    """Start background monitoring thread"""
    global monitoring_active
    
    # Try to start eBPF monitoring
    bpf_started = monitor.start_monitoring()
    
    if not bpf_started:
        print("[*] Running in psutil-only mode (no root access for eBPF)")
    
    monitoring_active = True
    
    def collect_data():
        while monitoring_active:
            try:
                # Collect stats every 5 seconds
                time.sleep(5)
                
                # Get current stats
                net_stats = monitor.get_stats()
                carbon_metrics = calculator.get_carbon_metrics(net_stats)
                
                # Store historical data (keep last 100 points)
                current_time = datetime.now().strftime('%H:%M:%S')
                historical_data['timestamps'].append(current_time)
                historical_data['cpu_usage'].append(carbon_metrics['cpu']['usage_percent'])
                historical_data['network_bytes'].append(net_stats['total_bytes'] / (1024*1024))  # MB
                historical_data['carbon_emissions'].append(carbon_metrics['total']['carbon_grams'])
                historical_data['energy_consumption'].append(carbon_metrics['total']['total_energy_kwh'] * 1000)  # Wh
                
                # Keep only last 100 data points
                for key in historical_data:
                    if len(historical_data[key]) > 100:
                        historical_data[key] = historical_data[key][-100:]
                
            except Exception as e:
                print(f"Error in data collection: {e}")
    
    # Start collection thread
    collection_thread = threading.Thread(target=collect_data, daemon=True)
    collection_thread.start()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    """Get current system statistics"""
    try:
        net_stats = monitor.get_stats()
        carbon_metrics = calculator.get_carbon_metrics(net_stats)
        processes = monitor.get_process_list()
        
        return jsonify({
            'success': True,
            'network': {
                'packets': net_stats['packet_count'],
                'bytes_sent_mb': net_stats['bytes_sent'] / (1024*1024),
                'bytes_received_mb': net_stats['bytes_received'] / (1024*1024),
                'total_mb': net_stats['total_bytes'] / (1024*1024),
                'active_connections': net_stats['active_connections']
            },
            'carbon': {
                'cpu_carbon_g': carbon_metrics['cpu']['carbon_grams'],
                'network_carbon_g': carbon_metrics['network']['carbon_grams'],
                'total_carbon_g': carbon_metrics['total']['carbon_grams'],
                'total_carbon_kg': carbon_metrics['total']['carbon_kg']
            },
            'energy': {
                'cpu_power_w': carbon_metrics['cpu']['power_watts'],
                'total_energy_kwh': carbon_metrics['total']['total_energy_kwh'],
                'runtime_hours': carbon_metrics['total']['runtime_hours']
            },
            'system': {
                'cpu_percent': carbon_metrics['cpu']['usage_percent'],
                'memory_percent': carbon_metrics['memory']['usage_percent'],
                'memory_used_gb': carbon_metrics['memory']['used_gb'],
                'memory_total_gb': carbon_metrics['memory']['total_gb']
            },
            'processes': processes[:10]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/optimize', methods=['POST'])
def optimize():
    """Apply optimization strategy"""
    try:
        data = request.get_json()
        optimization_type = data.get('type', 'reduce_cpu')
        
        # Capture carbon emission BEFORE optimization
        net_stats_before = monitor.get_stats()
        carbon_metrics_before = calculator.get_carbon_metrics(net_stats_before)
        before_carbon = carbon_metrics_before['total']['carbon_grams']
        
        # Apply optimization
        result = optimizer.apply_optimization(optimization_type)
        
        # Calculate estimated carbon emission AFTER optimization
        # Get reduction percentage from the optimization result
        reduction_percent_str = result.get('estimated_reduction', '30%').replace('%', '')
        try:
            reduction_percent = float(reduction_percent_str) / 100.0
        except:
            reduction_percent = 0.30  # Default 30%
        
        after_carbon = before_carbon * (1 - reduction_percent)
        reduction_carbon = before_carbon - after_carbon
        
        # Store optimization data
        optimization_data['before_carbon_g'] = before_carbon
        optimization_data['after_carbon_g'] = after_carbon
        optimization_data['reduction_g'] = reduction_carbon
        optimization_data['reduction_percent'] = reduction_percent * 100
        optimization_data['optimization_applied'] = True
        optimization_data['optimization_type'] = optimization_type
        
        return jsonify({
            'success': result['success'],
            'optimization_type': optimization_type,
            'actions': result.get('actions', []),
            'estimated_reduction': result.get('estimated_reduction', 'N/A'),
            'before_carbon_g': before_carbon,
            'after_carbon_g': after_carbon,
            'reduction_g': reduction_carbon,
            'reduction_percent': reduction_percent * 100,
            'error': result.get('error')
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/graph/<graph_type>')
def get_graph(graph_type):
    """Generate and return graphs as base64 encoded images"""
    try:
        plt.figure(figsize=(10, 5))
        plt.style.use('seaborn-v0_8-darkgrid')
        
        if graph_type == 'cpu':
            plt.plot(historical_data['timestamps'], historical_data['cpu_usage'], 
                    color='#3498db', linewidth=2, marker='o', markersize=4)
            plt.title('CPU Usage Over Time', fontsize=16, fontweight='bold')
            plt.ylabel('CPU Usage (%)', fontsize=12)
            plt.ylim(0, 100)
            
        elif graph_type == 'network':
            plt.plot(historical_data['timestamps'], historical_data['network_bytes'], 
                    color='#2ecc71', linewidth=2, marker='s', markersize=4)
            plt.title('Network Traffic Over Time', fontsize=16, fontweight='bold')
            plt.ylabel('Data (MB)', fontsize=12)
            
        elif graph_type == 'carbon':
            plt.plot(historical_data['timestamps'], historical_data['carbon_emissions'], 
                    color='#e74c3c', linewidth=2, marker='^', markersize=4)
            plt.title('Carbon Emissions Over Time', fontsize=16, fontweight='bold')
            plt.ylabel('Carbon (grams CO₂)', fontsize=12)
            
        elif graph_type == 'energy':
            plt.plot(historical_data['timestamps'], historical_data['energy_consumption'], 
                    color='#f39c12', linewidth=2, marker='d', markersize=4)
            plt.title('Energy Consumption Over Time', fontsize=16, fontweight='bold')
            plt.ylabel('Energy (Wh)', fontsize=12)
        
        plt.xlabel('Time', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.grid(True, alpha=0.3)
        
        # Convert plot to base64 encoded image
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{image_base64}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/savings')
def get_savings():
    """Get estimated savings for different optimization strategies"""
    try:
        savings = {
            'reduce_cpu': calculator.estimate_savings('reduce_cpu'),
            'optimize_network': calculator.estimate_savings('optimize_network'),
            'power_management': calculator.estimate_savings('power_management')
        }
        
        return jsonify({
            'success': True,
            'savings': savings
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/optimization-data')
def get_optimization_data():
    """Get before/after optimization data"""
    try:
        return jsonify({
            'success': True,
            'optimization_data': optimization_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('static/graphs', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # Start background monitoring
    print("[+] Starting background monitoring...")
    start_background_monitoring()
    
    # Run Flask app
    print("[+] Starting Flask application on http://0.0.0.0:5000")
    print("[+] Access the dashboard at: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)