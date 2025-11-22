# System Architecture Diagram - Carbon Emission Prediction (CEP) System

## High-Level Architecture Flow

```mermaid
graph TB
    subgraph "User Interface Layer"
        UI[Web Dashboard<br/>HTML/CSS/JavaScript]
    end
    
    subgraph "Application Layer (Flask)"
        API1[/api/stats<br/>Get System Stats]
        API2[/api/optimize<br/>Apply Optimization]
        API3[/api/optimization-data<br/>Before/After Data]
        API4[/api/graph/<type><br/>Generate Graphs]
        API5[/api/savings<br/>Estimate Savings]
    end
    
    subgraph "Data Collection Layer"
        MONITOR[BPFNetworkMonitor<br/>bpf_monitor.py]
        PSUTIL[psutil Library<br/>System Metrics]
    end
    
    subgraph "Core Calculation Engine"
        CALC[CarbonCalculator<br/>carbon_calculator.py]
        OPT[CarbonOptimizer<br/>optimizer.py]
    end
    
    subgraph "Data Storage"
        HIST[Historical Data<br/>Circular Buffer]
        OPT_DATA[Optimization Data<br/>Before/After Tracking]
    end
    
    subgraph "System Resources"
        CPU[CPU Usage %]
        MEM[Memory Usage]
        NET[Network I/O<br/>Bytes/Packets]
        PROC[Process List]
    end
    
    subgraph "Output/Visualization"
        GRAPH[Matplotlib Graphs<br/>CPU/Network/Carbon/Energy]
        METRICS[Carbon Metrics<br/>g CO₂ / kg CO₂]
        COMPARE[Before/After<br/>Comparison]
    end
    
    %% User interactions
    UI -->|HTTP Requests| API1
    UI -->|HTTP Requests| API2
    UI -->|HTTP Requests| API3
    UI -->|HTTP Requests| API4
    UI -->|HTTP Requests| API5
    
    %% API to Monitor
    API1 -->|Get Stats| MONITOR
    API2 -->|Get Stats| MONITOR
    API3 -->|Read Data| OPT_DATA
    API4 -->|Read Data| HIST
    API5 -->|Get Savings| CALC
    
    %% Monitor to psutil
    MONITOR -->|Collect Metrics| PSUTIL
    PSUTIL -->|Read| CPU
    PSUTIL -->|Read| MEM
    PSUTIL -->|Read| NET
    PSUTIL -->|Read| PROC
    
    %% Monitor to Calculator
    MONITOR -->|Network Stats| CALC
    PSUTIL -->|CPU/Memory Data| CALC
    
    %% Calculator processing
    CALC -->|Calculate Carbon| METRICS
    CALC -->|Store Metrics| HIST
    CALC -->|Calculate Power/Energy| METRICS
    
    %% Optimization flow
    API2 -->|Apply Strategy| OPT
    OPT -->|Analyze Processes| PSUTIL
    OPT -->|Get Current Carbon| CALC
    OPT -->|Store Results| OPT_DATA
    OPT -->|Calculate Reduction| OPT_DATA
    
    %% Graph generation
    API4 -->|Generate| GRAPH
    HIST -->|Time Series Data| GRAPH
    
    %% Response flow
    API1 -->|JSON Response| UI
    API2 -->|JSON Response| UI
    API3 -->|JSON Response| UI
    API4 -->|Base64 Image| UI
    API5 -->|JSON Response| UI
    
    %% Comparison display
    OPT_DATA -->|Before/After Data| COMPARE
    COMPARE -->|Display| UI
    
    style UI fill:#e1f5ff
    style CALC fill:#fff4e1
    style OPT fill:#fff4e1
    style MONITOR fill:#e8f5e9
    style PSUTIL fill:#fce4ec
    style HIST fill:#f3e5f5
    style OPT_DATA fill:#f3e5f5
    style METRICS fill:#fff9c4
    style GRAPH fill:#fff9c4
    style COMPARE fill:#fff9c4
```

## Detailed Component Flow

```mermaid
sequenceDiagram
    participant User
    participant UI as Web Dashboard
    participant API as Flask API
    participant Monitor as BPFNetworkMonitor
    participant psutil as psutil Library
    participant Calc as CarbonCalculator
    participant Opt as CarbonOptimizer
    participant Storage as Data Storage
    
    Note over User,Storage: System Initialization
    Monitor->>psutil: Initialize monitoring
    Monitor->>Monitor: Start background thread
    
    Note over User,Storage: Real-time Data Collection (Every 5 seconds)
    loop Continuous Monitoring
        Monitor->>psutil: Get CPU usage %
        psutil-->>Monitor: cpu_percent
        Monitor->>psutil: Get network I/O
        psutil-->>Monitor: bytes_sent, bytes_recv
        Monitor->>psutil: Get memory stats
        psutil-->>Monitor: memory_percent
        Monitor->>Calc: Pass network stats
        Calc->>psutil: Get CPU usage
        psutil-->>Calc: cpu_percent
        Calc->>Calc: Calculate CPU power (Custom formula)
        Calc->>Calc: Calculate network carbon (Custom formula)
        Calc->>Calc: Calculate total carbon (Custom aggregation)
        Calc->>Storage: Store historical data
    end
    
    Note over User,Storage: User Requests Stats
    User->>UI: Load dashboard
    UI->>API: GET /api/stats
    API->>Monitor: Get current stats
    Monitor->>psutil: Get latest metrics
    psutil-->>Monitor: System metrics
    Monitor-->>API: Network stats
    API->>Calc: Calculate carbon metrics
    Calc->>Calc: Apply custom formulas
    Calc-->>API: Carbon metrics (g CO₂)
    API-->>UI: JSON response
    UI-->>User: Display stats
    
    Note over User,Storage: User Applies Optimization
    User->>UI: Click "Apply Optimization"
    UI->>API: POST /api/optimize
    API->>Calc: Get current carbon (BEFORE)
    Calc-->>API: before_carbon_g
    API->>Opt: Apply optimization strategy
    Opt->>psutil: Get process list
    psutil-->>Opt: Process data
    Opt->>Opt: Analyze high-CPU processes (Custom algorithm)
    Opt->>Opt: Generate recommendations (Custom logic)
    Opt-->>API: Optimization result
    API->>API: Calculate AFTER carbon (Custom formula)
    API->>API: Calculate reduction (Custom formula)
    API->>Storage: Store before/after data
    API-->>UI: Optimization result + before/after data
    UI-->>User: Show comparison
    
    Note over User,Storage: User Views Graphs
    User->>UI: View graphs
    UI->>API: GET /api/graph/carbon
    API->>Storage: Get historical data
    Storage-->>API: Time series data
    API->>API: Generate matplotlib graph
    API-->>UI: Base64 encoded image
    UI-->>User: Display graph
```

## Package/Module Flow Diagram

```mermaid
graph LR
    subgraph "External Libraries"
        PSUTIL[psutil<br/>System Metrics]
        FLASK[Flask<br/>Web Framework]
        MATPLOT[Matplotlib<br/>Graph Generation]
    end
    
    subgraph "Custom Modules"
        BPF[bpf_monitor.py<br/>BPFNetworkMonitor]
        CALC[carbon_calculator.py<br/>CarbonCalculator]
        OPT[optimizer.py<br/>CarbonOptimizer]
        APP[app.py<br/>Flask Application]
    end
    
    subgraph "Data Flow"
        RAW[Raw System Data<br/>CPU%, Memory, Network]
        PROCESSED[Processed Data<br/>Carbon Metrics]
        STORED[Stored Data<br/>Historical + Tracking]
    end
    
    PSUTIL -->|Provides| RAW
    RAW -->|Input| BPF
    RAW -->|Input| CALC
    
    BPF -->|Uses| PSUTIL
    CALC -->|Uses| PSUTIL
    OPT -->|Uses| PSUTIL
    
    CALC -->|Generates| PROCESSED
    OPT -->|Generates| PROCESSED
    
    PROCESSED -->|Stores| STORED
    
    APP -->|Uses| BPF
    APP -->|Uses| CALC
    APP -->|Uses| OPT
    APP -->|Uses| FLASK
    APP -->|Uses| MATPLOT
    
    APP -->|Reads| STORED
    APP -->|Serves| UI[Web Interface]
    
    style PSUTIL fill:#ffcccc
    style FLASK fill:#ccffcc
    style MATPLOT fill:#ccccff
    style BPF fill:#ffffcc
    style CALC fill:#ffffcc
    style OPT fill:#ffffcc
    style APP fill:#ffffcc
```

## Data Flow Architecture

```mermaid
flowchart TD
    START([System Start]) --> INIT[Initialize Components]
    INIT --> MONITOR[Start Background Monitoring]
    
    MONITOR --> COLLECT[Collect Data Every 5s]
    
    COLLECT --> PSUTIL_CALL[Call psutil Functions]
    PSUTIL_CALL --> GET_CPU[psutil.cpu_percent]
    PSUTIL_CALL --> GET_MEM[psutil.virtual_memory]
    PSUTIL_CALL --> GET_NET[psutil.net_io_counters]
    PSUTIL_CALL --> GET_PROC[psutil.process_iter]
    
    GET_CPU --> RAW_DATA[Raw System Metrics]
    GET_MEM --> RAW_DATA
    GET_NET --> RAW_DATA
    GET_PROC --> RAW_DATA
    
    RAW_DATA --> CALC_ENGINE[CarbonCalculator Engine]
    
    CALC_ENGINE --> CPU_POWER[Calculate CPU Power<br/>Power = 50W + 65W × CPU%/100]
    CALC_ENGINE --> NET_CARBON[Calculate Network Carbon<br/>Bytes → GB → kWh → CO₂]
    CALC_ENGINE --> CPU_CARBON[Calculate CPU Carbon<br/>Energy × Carbon Intensity]
    
    CPU_POWER --> AGGREGATE[Aggregate Metrics]
    NET_CARBON --> AGGREGATE
    CPU_CARBON --> AGGREGATE
    
    AGGREGATE --> TOTAL_CARBON[Total Carbon Emission<br/>g CO₂ / kg CO₂]
    
    TOTAL_CARBON --> STORE_HIST[Store in Historical Buffer<br/>Last 100 points]
    TOTAL_CARBON --> API_RESPONSE[API Response]
    
    STORE_HIST --> GRAPH_GEN[Generate Graphs<br/>Matplotlib]
    GRAPH_GEN --> GRAPH_OUT[Graph Images]
    
    API_RESPONSE --> USER_REQ{User Request Type}
    
    USER_REQ -->|Stats| SHOW_STATS[Display Current Stats]
    USER_REQ -->|Optimize| OPT_FLOW[Optimization Flow]
    USER_REQ -->|Graph| SHOW_GRAPH[Display Graph]
    USER_REQ -->|Compare| SHOW_COMPARE[Show Before/After]
    
    OPT_FLOW --> CAPTURE_BEFORE[Capture BEFORE Carbon]
    CAPTURE_BEFORE --> APPLY_OPT[Apply Optimization Strategy]
    APPLY_OPT --> OPT_ENGINE[CarbonOptimizer]
    
    OPT_ENGINE --> ANALYZE[Analyze Processes<br/>Custom Algorithm]
    OPT_ENGINE --> RECOMMEND[Generate Recommendations<br/>Custom Logic]
    
    ANALYZE --> CALC_AFTER[Calculate AFTER Carbon<br/>Before × 1 - Reduction%]
    CALC_AFTER --> CALC_REDUCTION[Calculate Reduction<br/>Before - After]
    
    CALC_REDUCTION --> STORE_OPT[Store Optimization Data]
    STORE_OPT --> SHOW_COMPARE
    
    SHOW_STATS --> END1([Display to User])
    SHOW_GRAPH --> END1
    SHOW_COMPARE --> END1
    
    COLLECT -.->|Loop Every 5s| COLLECT
    
    style CALC_ENGINE fill:#fff4e1
    style OPT_ENGINE fill:#fff4e1
    style CPU_POWER fill:#e8f5e9
    style NET_CARBON fill:#e8f5e9
    style CPU_CARBON fill:#e8f5e9
    style TOTAL_CARBON fill:#fff9c4
    style PSUTIL_CALL fill:#fce4ec
```

## Component Interaction Diagram

```mermaid
graph TB
    subgraph "Input Layer"
        SYS[System Resources<br/>CPU, Memory, Network]
    end
    
    subgraph "Data Collection (psutil)"
        P1[psutil.cpu_percent<br/>Returns: CPU %]
        P2[psutil.virtual_memory<br/>Returns: Memory stats]
        P3[psutil.net_io_counters<br/>Returns: Bytes sent/received]
        P4[psutil.process_iter<br/>Returns: Process list]
        P5[psutil.net_connections<br/>Returns: Connection list]
    end
    
    subgraph "Custom Processing Layer"
        C1[CarbonCalculator<br/>calculate_cpu_power<br/>Custom Formula]
        C2[CarbonCalculator<br/>calculate_network_carbon<br/>Custom Formula]
        C3[CarbonCalculator<br/>calculate_total_energy<br/>Custom Formula]
        C4[CarbonCalculator<br/>get_carbon_metrics<br/>Custom Aggregation]
        O1[CarbonOptimizer<br/>reduce_cpu_usage<br/>Custom Algorithm]
        O2[CarbonOptimizer<br/>optimize_network<br/>Custom Algorithm]
        O3[CarbonOptimizer<br/>enable_power_management<br/>Custom Algorithm]
    end
    
    subgraph "Output Layer"
        OUT1[Carbon Metrics<br/>g CO₂, kg CO₂]
        OUT2[Optimization Results<br/>Before/After/Reduction]
        OUT3[Historical Graphs<br/>Time Series Data]
        OUT4[API Responses<br/>JSON/Images]
    end
    
    SYS --> P1
    SYS --> P2
    SYS --> P3
    SYS --> P4
    SYS --> P5
    
    P1 --> C1
    P3 --> C2
    C1 --> C3
    C2 --> C4
    C3 --> C4
    C4 --> OUT1
    
    P4 --> O1
    P5 --> O2
    O1 --> OUT2
    O2 --> OUT2
    O3 --> OUT2
    
    OUT1 --> OUT3
    OUT1 --> OUT4
    OUT2 --> OUT4
    
    style P1 fill:#fce4ec
    style P2 fill:#fce4ec
    style P3 fill:#fce4ec
    style P4 fill:#fce4ec
    style P5 fill:#fce4ec
    style C1 fill:#fff4e1
    style C2 fill:#fff4e1
    style C3 fill:#fff4e1
    style C4 fill:#fff4e1
    style O1 fill:#fff4e1
    style O2 fill:#fff4e1
    style O3 fill:#fff4e1
```

## System Architecture Overview (Text-Based)

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                         │
│              (Web Dashboard - HTML/CSS/JavaScript)              │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP Requests
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FLASK APPLICATION LAYER                      │
│                          (app.py)                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │/api/stats│  │/api/     │  │/api/     │  │/api/     │      │
│  │          │  │optimize  │  │optimization│ │graph/   │      │
│  │          │  │          │  │-data     │  │<type>    │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
└───────┼─────────────┼─────────────┼─────────────┼────────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA COLLECTION LAYER                        │
│              (BPFNetworkMonitor - bpf_monitor.py)               │
│                                                                 │
│  Uses psutil for:                                              │
│  • psutil.cpu_percent()      → CPU usage %                    │
│  • psutil.virtual_memory()   → Memory stats                   │
│  • psutil.net_io_counters()  → Network bytes                  │
│  • psutil.process_iter()      → Process list                  │
│  • psutil.net_connections()  → Connection list               │
└────────────────────────────┬────────────────────────────────────┘
                             │ Raw System Metrics
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              CORE CALCULATION ENGINE                            │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  CarbonCalculator (carbon_calculator.py)                 │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │ calculate_cpu_power()                              │  │  │
│  │  │   Power = 50W + (65W × CPU%/100)  [CUSTOM]        │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │ calculate_network_carbon()                         │  │  │
│  │  │   Bytes → GB → kWh → CO₂  [CUSTOM]                 │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │ calculate_total_energy()                            │  │  │
│  │  │   Energy = (Power × Time) / 1000  [CUSTOM]         │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │ get_carbon_metrics()                               │  │  │
│  │  │   Aggregates all metrics  [CUSTOM]                  │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  CarbonOptimizer (optimizer.py)                         │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │ reduce_cpu_usage()                                 │  │  │
│  │  │   Analyzes processes >50% CPU  [CUSTOM]            │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │ optimize_network()                                 │  │  │
│  │  │   Network analysis & recommendations  [CUSTOM]    │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │ enable_power_management()                         │  │  │
│  │  │   Power saving strategies  [CUSTOM]               │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ Processed Data
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA STORAGE LAYER                           │
│                                                                 │
│  Historical Data (Circular Buffer - Last 100 points):          │
│  • Timestamps                                                  │
│  • CPU usage history                                           │
│  • Network traffic history                                     │
│  • Carbon emissions history                                    │
│  • Energy consumption history                                  │
│                                                                 │
│  Optimization Data (Before/After Tracking):                   │
│  • before_carbon_g                                             │
│  • after_carbon_g                                              │
│  • reduction_g                                                 │
│  • reduction_percent                                           │
│  • optimization_type                                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  OUTPUT/VISUALIZATION LAYER                     │
│                                                                 │
│  • Carbon Metrics (g CO₂, kg CO₂)                              │
│  • Before/After Comparison                                     │
│  • Matplotlib Graphs (CPU/Network/Carbon/Energy)                │
│  • API JSON Responses                                          │
│  • Real-time Dashboard Updates                                 │
└─────────────────────────────────────────────────────────────────┘
```

## How to Use These Diagrams

1. **Mermaid Diagrams**: 
   - Can be viewed in GitHub, GitLab, or any Markdown viewer with Mermaid support
   - Can be exported as images using tools like:
     - [Mermaid Live Editor](https://mermaid.live/) - Copy the mermaid code and export as PNG/SVG
     - VS Code with Mermaid extension
     - Online Mermaid renderers

2. **Text-Based Diagram**: 
   - Already in text format, can be copied directly
   - Can be converted to image using ASCII art tools

3. **Recommended Tool**: 
   - Use [Mermaid Live Editor](https://mermaid.live/)
   - Copy any of the mermaid code blocks
   - Click "Actions" → "Download PNG" or "Download SVG"

## Key Points Shown in Diagrams

1. **psutil Usage**: Only in Data Collection Layer (shown in pink/red)
2. **Custom Components**: Calculation Engine and Optimizer (shown in yellow)
3. **Data Flow**: From system → psutil → custom processing → output
4. **Package Flow**: How different modules interact
5. **Sequence Diagram**: Step-by-step process flow
6. **Component Interaction**: Detailed interaction between components

---

**Note**: To download these diagrams as images:
1. Go to https://mermaid.live/
2. Copy the mermaid code from any diagram above
3. Paste it in the editor
4. Click "Actions" → "Download PNG" or "Download SVG"

