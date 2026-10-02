# SYSTEM ARCHITECTURE & DESIGN DIAGRAMS
## AI-BASED SMART TRAFFIC MONITORING & CONTROL SYSTEM

---

### 1. High-Level System Architecture Diagram

```mermaid
flowchart TD
    subgraph SENSING["1. Sensing & Ingestion Layer"]
        CAM1["HD CCTV Camera 1"]
        CAM2["HD CCTV Camera 2"]
        SIM["Synthetic Scenario Engine"]
        WEB["USB Webcam / RTSP Stream"]
    end

    subgraph PERCEPTION["2. AI Perception & Vision Engine"]
        MOG["MOG2 Background Subtraction & Blur"]
        MORPH["Morphological Dilation & Closing"]
        DET["Contour & Multi-Scale Classifier"]
        EMG["Emergency Siren & Beacon HSV Classifier"]
    end

    subgraph TRACKING["3. Multi-Object Tracking Engine"]
        CENTROID["Euclidean Centroid Tracker"]
        ID_MGR["Unique Vehicle ID Registry (#VID)"]
        SPEED["Kinematic Speed Estimator (km/h)"]
        LANE["Lane Mapping & Trajectory Tracing"]
    end

    subgraph DECISION["4. Adaptive Control & Incident Matrix"]
        PCE["PCE Weighted Density Calculator"]
        DATSA["D-ATSA Dynamic Green Time Engine"]
        PREEMPT["Emergency Green-Wave Preemption FSM"]
        INCIDENT["Safety Rule Auditor (Speed/Red/Wrong)"]
    end

    subgraph UI_LAYER["5. Operations & Visualization Dashboard"]
        STREAM["MJPEG Real-Time Video Stream"]
        SCHEMATIC["4-Way Animated LED Signal Display"]
        CHARTS["Live Chart.js Visualizations"]
        EXPORTS["CSV & JSON Audit Reports"]
    end

    SENSING --> PERCEPTION
    PERCEPTION --> TRACKING
    TRACKING --> DECISION
    DECISION --> UI_LAYER
```

---

### 2. Data Flow Diagram (DFD Level 0 - Context Level)

```mermaid
flowchart LR
    CAM["Traffic Cameras / Video Sources"] -->|"Raw Video Frames"| SYSTEM(("Traffic-Vision AI System"))
    OPERATOR["Traffic Controller / Operator"] -->|"Manual Mode / Speed Thresholds"| SYSTEM
    SYSTEM -->|"Live HUD Stream & Density Telemetry"| OPERATOR
    SYSTEM -->|"Adaptive Signal Light States (N, S, E, W)"| SIGNALS["4-Way Intersection Physical Lights"]
    SYSTEM -->|"Violation Logs & Snapshots"| POLICE["Traffic Police / Municipal Authority"]
```

---

### 3. Data Flow Diagram (DFD Level 1 - Subsystems Level)

```mermaid
flowchart TD
    STREAM["Video Stream"] --> P1["1.0 Frame Pre-Processing & Detection"]
    P1 -->|"Bounding Boxes & Classes"| P2["2.0 Multi-Object Vehicle Tracking"]
    P2 -->|"Vehicle IDs & Trajectories"| P3["3.0 Speed & Lane Calculation"]
    P3 -->|"Lane Counts & PCE Load"| P4["4.0 Dynamic Signal Timing (D-ATSA)"]
    P3 -->|"Speed & Trajectory Vectors"| P5["5.0 Safety Incident Evaluator"]
    P4 -->|"Signal States & Timers"| P6["6.0 Dashboard Web Server"]
    P5 -->|"Violation Snapshots & CSV"| P6
```

---

### 4. Sequence Diagram: Emergency Green-Wave Preemption Flow

```mermaid
sequenceDiagram
    autonumber
    participant Cam as Video Camera Feed
    participant AI as Vision Detector
    participant Ctrl as Traffic Signal Controller
    participant Light as Physical Signal Lights
    participant Dash as Web Dashboard

    Cam->>AI: Video Frame with approaching Ambulance
    AI->>AI: Detect vehicle + Emergency Beacon HSV Match
    AI->>Ctrl: Trigger Emergency Preemption (Lane: West)
    Ctrl->>Dash: Broadcast Emergency Alert Banner
    Ctrl->>Light: Switch active phase to Yellow (2s clearance)
    Note over Ctrl,Light: 2 seconds safety clearance interval
    Ctrl->>Light: Switch Westbound Approach to GREEN (45s hold)
    Note over AI,Ctrl: Ambulance clears intersection box
    AI->>Ctrl: Emergency clearance confirmed
    Ctrl->>Ctrl: Restore standard D-ATSA adaptive cycle
    Ctrl->>Dash: Clear Emergency Alert Banner
```

---

### 5. Finite State Machine (FSM): Signal Controller State Transitions

```mermaid
stateDiagram-v2
    [*] --> NS_GREEN : System Startup

    state NS_GREEN {
        [*] --> Timing_NS
        Timing_NS --> NS_Extended : Density High
        Timing_NS --> NS_Timeout : Timer Reached
    }

    NS_GREEN --> NS_YELLOW : Timer Expired
    NS_YELLOW --> EW_GREEN : Yellow Clearance (3s)

    state EW_GREEN {
        [*] --> Timing_EW
        Timing_EW --> EW_Extended : Density High
        Timing_EW --> EW_Timeout : Timer Reached
    }

    EW_GREEN --> EW_YELLOW : Timer Expired
    EW_YELLOW --> NS_GREEN : Yellow Clearance (3s)

    NS_GREEN --> EMERGENCY_PREEMPTION : Emergency in E/W Lane
    EW_GREEN --> EMERGENCY_PREEMPTION : Emergency in N/S Lane

    state EMERGENCY_PREEMPTION {
        [*] --> Quick_Yellow_Clearance
        Quick_Yellow_Clearance --> Priority_Green_Hold
        Priority_Green_Hold --> Emergency_Cleared
    }

    EMERGENCY_PREEMPTION --> NS_GREEN : Resume Normal Adaptive Flow
```
