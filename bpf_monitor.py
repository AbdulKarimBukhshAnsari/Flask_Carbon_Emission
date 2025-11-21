#!/usr/bin/env python3
"""
eBPF-based Network and Process Monitoring
Monitors network packets, connections, and process activity
"""

from bcc import BPF
import psutil
import time
from collections import defaultdict
import threading

class BPFNetworkMonitor:
    def __init__(self):
        self.packet_count = 0
        self.bytes_sent = 0
        self.bytes_received = 0
        self.active_connections = 0
        self.process_stats = defaultdict(lambda: {'packets': 0, 'bytes': 0})
        self.running = False
        self.lock = threading.Lock()
        
        # eBPF program for network monitoring
        self.bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/in.h>
#include <linux/socket.h>
#include <bcc/proto.h>

struct event_data_t {
    u32 pid;
    u32 saddr;
    u32 daddr;
    u16 sport;
    u16 dport;
    u64 bytes;
    char comm[16];
    u8 event_type;
};

BPF_PERF_OUTPUT(events);
BPF_HASH(packet_stats, u32, u64);

// Trace TCP send
int trace_tcp_sendmsg(struct pt_regs *ctx, struct sock *sk, struct msghdr *msg, size_t size) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    
    struct event_data_t data = {};
    data.pid = pid;
    data.bytes = size;
    data.event_type = 1; // send
    bpf_get_current_comm(&data.comm, sizeof(data.comm));
    
    u16 family = sk->__sk_common.skc_family;
    if (family == AF_INET) {
        data.saddr = sk->__sk_common.skc_rcv_saddr;
        data.daddr = sk->__sk_common.skc_daddr;
        data.sport = sk->__sk_common.skc_num;
        data.dport = sk->__sk_common.skc_dport;
        data.dport = ntohs(data.dport);
    }
    
    events.perf_submit(ctx, &data, sizeof(data));
    
    u64 *val, zero = 0;
    val = packet_stats.lookup_or_init(&pid, &zero);
    (*val) += size;
    
    return 0;
}

// Trace TCP receive
int trace_tcp_recvmsg(struct pt_regs *ctx, struct sock *sk) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    
    struct event_data_t data = {};
    data.pid = pid;
    data.event_type = 2; // receive
    bpf_get_current_comm(&data.comm, sizeof(data.comm));
    
    events.perf_submit(ctx, &data, sizeof(data));
    
    return 0;
}

// Trace UDP send
int trace_udp_sendmsg(struct pt_regs *ctx, struct sock *sk, struct msghdr *msg, size_t size) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    
    struct event_data_t data = {};
    data.pid = pid;
    data.bytes = size;
    data.event_type = 3; // udp send
    bpf_get_current_comm(&data.comm, sizeof(data.comm));
    
    events.perf_submit(ctx, &data, sizeof(data));
    
    u64 *val, zero = 0;
    val = packet_stats.lookup_or_init(&pid, &zero);
    (*val) += size;
    
    return 0;
}
"""
        self.bpf = None
        
    def start_monitoring(self):
        """Initialize and start eBPF monitoring"""
        try:
            self.bpf = BPF(text=self.bpf_text)
            
            # Attach to kernel functions
            self.bpf.attach_kprobe(event="tcp_sendmsg", fn_name="trace_tcp_sendmsg")
            self.bpf.attach_kprobe(event="tcp_recvmsg", fn_name="trace_tcp_recvmsg")
            self.bpf.attach_kprobe(event="udp_sendmsg", fn_name="trace_udp_sendmsg")
            
            self.running = True
            
            # Start event processing thread
            self.monitor_thread = threading.Thread(target=self._process_events, daemon=True)
            self.monitor_thread.start()
            
            print("[+] eBPF monitoring started successfully")
            return True
            
        except Exception as e:
            print(f"[-] Failed to start eBPF monitoring: {e}")
            print("[*] Falling back to psutil monitoring")
            return False
    
    def _process_events(self):
        """Process eBPF events"""
        def handle_event(cpu, data, size):
            event = self.bpf["events"].event(data)
            
            with self.lock:
                self.packet_count += 1
                
                if event.event_type == 1 or event.event_type == 3:  # send
                    self.bytes_sent += event.bytes
                    comm = event.comm.decode('utf-8', 'replace')
                    self.process_stats[comm]['packets'] += 1
                    self.process_stats[comm]['bytes'] += event.bytes
                elif event.event_type == 2:  # receive
                    self.bytes_received += 1024  # estimate
        
        if self.bpf:
            self.bpf["events"].open_perf_buffer(handle_event)
            
            while self.running:
                try:
                    self.bpf.perf_buffer_poll(timeout=100)
                except KeyboardInterrupt:
                    break
    
    def get_stats(self):
        """Get current monitoring statistics"""
        # Fallback to psutil if eBPF not available
        if not self.bpf:
            net_io = psutil.net_io_counters()
            with self.lock:
                self.packet_count = net_io.packets_sent + net_io.packets_recv
                self.bytes_sent = net_io.bytes_sent
                self.bytes_received = net_io.bytes_recv
        
        # Get active connections
        self.active_connections = len(psutil.net_connections())
        
        with self.lock:
            return {
                'packet_count': self.packet_count,
                'bytes_sent': self.bytes_sent,
                'bytes_received': self.bytes_received,
                'total_bytes': self.bytes_sent + self.bytes_received,
                'active_connections': self.active_connections,
                'process_stats': dict(self.process_stats)
            }
    
    def get_process_list(self):
        """Get list of running processes with their resource usage"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                pinfo = proc.info
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'cpu': pinfo['cpu_percent'],
                    'memory': pinfo['memory_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return sorted(processes, key=lambda x: x['cpu'], reverse=True)[:20]
    
    def stop_monitoring(self):
        """Stop eBPF monitoring"""
        self.running = False
        if self.bpf:
            print("[+] Stopping eBPF monitoring...")
            time.sleep(1)

if __name__ == "__main__":
    monitor = BPFNetworkMonitor()
    monitor.start_monitoring()
    
    try:
        while True:
            time.sleep(5)
            stats = monitor.get_stats()
            print(f"\n[Stats] Packets: {stats['packet_count']}, "
                  f"Sent: {stats['bytes_sent']/(1024*1024):.2f}MB, "
                  f"Recv: {stats['bytes_received']/(1024*1024):.2f}MB")
    except KeyboardInterrupt:
        monitor.stop_monitoring()