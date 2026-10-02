# COMPLETE SYSTEM ARCHITECTURE & UML DESIGN SPECIFICATION
## AI-Based Smart Traffic Monitoring & Dynamic Adaptive Signal Control System
### Major Project Technical Reference & Architecture Document

---

## 📑 Table of Contents
1. [System Overview & Architecture Principles](#1-system-overview--architecture-principles)
2. [Multi-Tier System Architecture Diagram](#2-multi-tier-system-architecture-diagram)
3. [UML Class Diagram](#3-uml-class-diagram)
4. [UML Use Case Diagram](#4-uml-use-case-diagram)
5. [UML Sequence Diagrams](#5-uml-sequence-diagrams)
   - 5.1 [Sequence 1: Real-Time Perception & Adaptive Signal Control](#51-sequence-1-real-time-perception--adaptive-signal-control)
   - 5.2 [Sequence 2: Emergency Vehicle Green-Wave Preemption](#52-sequence-2-emergency-vehicle-green-wave-preemption)
   - 5.3 [Sequence 3: Traffic Violation Detection & Evidence Logging](#53-sequence-3-traffic-violation-detection--evidence-logging)
6. [UML State Machine Diagram (Finite State Machine)](#6-uml-state-machine-diagram)
7. [UML Activity Diagram (Frame Execution Pipeline)](#7-uml-activity-diagram)
8. [UML Component Diagram](#8-uml-component-diagram)
9. [UML Deployment Diagram](#9-uml-deployment-diagram)
10. [Data Flow Diagrams (DFD Level 0, 1 & 2)](#10-data-flow-diagrams)
11. [Data Models & Schema Specifications](#11-data-models--schema-specifications)
12. [Mathematical Algorithms & Control Formulas](#12-mathematical-algorithms--control-formulas)

---

## 1. System Overview & Architecture Principles

The **AI-Based Smart Traffic Monitoring and Dynamic Adaptive Signal Control System** is architected on high-throughput, edge-capable computer vision and decoupled finite state control.

### Core Architectural Patterns:
- **Pipes-and-Filters Pattern:** Successive processing stages (Frame Ingestion $\to$ Background Subtraction $\to$ Contour Classification $\to$ Centroid Association $\to$ Kinematics $\to$ Signal Allocation).
- **Observer / Pub-Sub Telemetry:** The backend streaming thread publishes live state dictionaries consumed asynchronously by the web dashboard over HTTP REST polling and MJPEG multipart streaming.
- **Hierarchical Finite State Machine (FSM):** Deterministic state transitions handling green allocations, yellow clearances, and instantaneous asynchronous emergency preemption interruptions.

---

## 2. Multi-Tier System Architecture Diagram

```mermaid
flowchart TD
    subgraph LAYER_1["1. INGESTION LAYER (Video Sources)"]
        CAM1["CCTV IP Camera 1\n(RTSP / H.264)"]
        CAM2["CCTV IP Camera 2\n(RTSP / H.264)"]
        SYNTH["Synthetic Traffic\nSimulator Engine"]
        UPLOAD["User MP4 Video\nUpload Module"]
    end

    subgraph LAYER_2["2. COMPUTER VISION & PERCEPTION LAYER"]
        MOG["MOG2 Background\nSubtraction Engine"]
        MORPH["Morphological Opening\n& Closing Filters"]
        CONTOUR["Contour Extraction &\nGeometry Filter"]
        EMG_SPEC["Emergency Beacon\nColorimetric Spectrogram"]
        CLASSIFIER["PCE Vehicle Classifier\n(Car, Bus, Truck, Bike, Ambulance)"]
    end

    subgraph LAYER_3["3. TRACKING & KINEMATICS LAYER"]
        EUCLID["Centroid Euclidean\nDistance Matcher"]
        ID_REG["Persistent Vehicle\nID Registry"]
        TRAJ["Trajectory &\nHeading Vector Estimator"]
        SPEED_EST["Kalman-Smoothed\nSpeed Calculator (km/h)"]
    end

    subgraph LAYER_4["4. DECISION & ADAPTIVE CONTROL LAYER"]
        DENSITY["PCE Lane Congestion\nWeighting Engine"]
        DATSA["D-ATSA Webster-Based\nAdaptive Timing Controller"]
        PREEMPT["Emergency Preemption\nGreen-Wave FSM"]
        AUDITOR["Traffic Violation &\nSafety Auditor"]
    end

    subgraph LAYER_5["5. PRESENTATION & AUDITING LAYER"]
        FLASK["Flask REST & Streaming Server\n(Port 5000)"]
        STREAM["MJPEG Annotated\nVideo Stream"]
        DASH["Modern Web Dashboard\n(HTML5 / CSS3 / JS)"]
        CHARTS["Real-Time Chart.js\nVisualizations"]
        CSV_STORE["CSV & Snapshot\nViolation Database"]
    end

    LAYER_1 --> LAYER_2
    LAYER_2 --> LAYER_3
    LAYER_3 --> LAYER_4
    LAYER_4 --> LAYER_5
```

---

## 3. UML Class Diagram

```mermaid
classDiagram
    class TrafficEngine {
        +VehicleDetector detector
        +VehicleTracker tracker
        +TrafficSignalController signal_controller
        +IncidentDetector incident_detector
        +VideoCapture cap
        +bool is_running
        +Mat current_frame
        +Mat annotated_frame
        +set_source(source_key, custom_path)
        +get_annotated_frame_bytes() bytes
        +get_telemetry_payload() dict
        -_process_video_loop()
        -_draw_clean_overlays()
    }

    class VehicleDetector {
        +float conf_thresh
        +int min_area
        +BackgroundSubtractorMOG2 bg_subtractor
        +detect(frame) tuple
        +classify_vehicle_type(w, h, area, aspect_ratio, roi) tuple
        +detect_emergency_features(vehicle_roi) tuple
    }

    class VehicleTracker {
        +int next_object_id
        +dict objects
        +dict disappeared
        +dict trajectories
        +dict vehicle_meta
        +int total_counted
        +dict class_counts
        +update(detections) list
        +register(centroid, det_info) int
        +deregister(obj_id)
        -_calculate_instant_speed(obj_id, new_centroid) float
        -_determine_lane_and_direction(centroid, trajectory) tuple
        +get_active_vehicles() list
    }

    class TrafficSignalController {
        +int min_green
        +int max_green
        +int yellow_time
        +dict weights
        +str current_phase
        +str sub_state
        +int time_remaining
        +int allocated_green_time
        +bool emergency_mode
        +str emergency_lane
        +dict lane_densities
        +update_lane_telemetry(active_vehicles)
        +calculate_weighted_density(vehicles_in_lane) tuple
        +compute_optimal_green_time(phase) int
        +trigger_emergency_preemption(lane_name, reason)
        +step_simulation()
        +get_signal_display() dict
    }

    class IncidentDetector {
        +float speed_limit_kmh
        +str output_dir
        +list violations_log
        +set reported_incident_keys
        +check_violations(active_vehicles, signal_state, current_frame) list
        +get_recent_violations(limit) list
        -_save_snapshot(frame, bbox, filename)
        -_write_to_csv(incident)
    }

    class TrafficVideoSimulator {
        +int width
        +int height
        +int fps
        +generate_video(output_path, scenario, duration_sec)
        -_draw_road_background(frame)
        -_draw_traffic_light_posts(frame, signals)
        -_draw_vehicle(frame, x, y, vtype, color, direction, frame_idx)
        -_get_signal_for_frame(f_idx, scenario) dict
    }

    TrafficEngine --> VehicleDetector : uses
    TrafficEngine --> VehicleTracker : uses
    TrafficEngine --> TrafficSignalController : uses
    TrafficEngine --> IncidentDetector : uses
    TrafficEngine ..> TrafficVideoSimulator : generates test feeds
```

---

## 4. UML Use Case Diagram

```mermaid
flowchart TD
    subgraph ACTORS["System Actors"]
        OPERATOR["👨‍💼 Traffic Control Operator"]
        EMG_VEH["🚑 Emergency Vehicle Driver"]
        POLICE["👮 Traffic Enforcement / Police"]
        ADMIN["🔧 System Administrator"]
    end

    subgraph SYSTEM_BOUNDARY["Traffic-Vision AI System Boundary"]
        UC1["UC-01: View Real-Time Multi-Lane Video Stream"]
        UC2["UC-02: Monitor Live Traffic Density & Speeds"]
        UC3["UC-03: Switch Operational Modes (AI vs Manual)"]
        UC4["UC-04: Force Manual Signal Phase Override"]
        UC5["UC-05: Upload Custom CCTV Video Footage"]
        UC6["UC-06: Automatic Emergency Preemption (Green-Wave)"]
        UC7["UC-07: Real-Time Violation Auditing & Snapshot Capture"]
        UC8["UC-08: Export Incident Logs to CSV / JSON"]
        UC9["UC-09: Configure Speed Violation Limits"]
    end

    OPERATOR --> UC1
    OPERATOR --> UC2
    OPERATOR --> UC3
    OPERATOR --> UC4
    OPERATOR --> UC5
    OPERATOR --> UC8

    EMG_VEH --> UC6

    POLICE --> UC7
    POLICE --> UC8
    POLICE --> UC9

    ADMIN --> UC3
    ADMIN --> UC5
```

---

## 5. UML Sequence Diagrams

### 5.1 Sequence 1: Real-Time Perception & Adaptive Signal Control
```mermaid
sequenceDiagram
    autonumber
    actor Cam as CCTV Video Source
    participant Engine as TrafficEngine
    participant Det as VehicleDetector
    participant Track as VehicleTracker
    participant Sig as TrafficSignalController
    participant UI as Web Dashboard

    Cam->>Engine: Send Raw Frame Matrix (960x540)
    Engine->>Det: detect(frame)
    Det->>Det: MOG2 Background Subtraction & Morphology
    Det->>Det: Extract Contours & Classify Vehicle Classes
    Det-->>Engine: Return Detections List [bbox, class, center]
    
    Engine->>Track: update(detections)
    Track->>Track: Euclidean Centroid Association
    Track->>Track: Calculate Smooth Speed (km/h) & Trajectory
    Track-->>Engine: Return Active Vehicles List
    
    Engine->>Sig: update_lane_telemetry(active_vehicles)
    Sig->>Sig: Compute PCE Density per Approach
    Sig->>Sig: Compute Optimal Green Time (D-ATSA)
    Sig-->>Engine: Return Updated Signal States (N, S, E, W)
    
    Engine->>Engine: Annotate Bounding Boxes & Signal HUD
    Engine->>UI: Stream MJPEG Frame (/video_feed)
    UI->>Engine: Poll Telemetry JSON (/api/telemetry)
    Engine-->>UI: Return JSON Payload (Densities, Speeds, Phase)
```

### 5.2 Sequence 2: Emergency Vehicle Green-Wave Preemption
```mermaid
sequenceDiagram
    autonumber
    participant Cam as CCTV Camera Feed
    participant Det as VehicleDetector
    participant Sig as TrafficSignalController
    participant Hardware as Intersection Signal Lights
    participant UI as Operator Dashboard

    Cam->>Det: Ingest frame with approaching Ambulance
    Det->>Det: Colorimetric strobe signature analysis (Red/Blue flash)
    Det->>Det: Classify as 'Ambulance (Emergency)'
    Det->>Sig: trigger_emergency_preemption('West Lane')
    
    Sig->>Sig: Enter EMERGENCY_PREEMPTION State
    Sig->>Hardware: Force active conflicting phase to YELLOW (2s clearance)
    Sig->>UI: Broadcast Emergency Banner & Sound Alert
    
    Note over Sig,Hardware: 2 Seconds Clearance Transition
    Sig->>Hardware: Switch Westbound Approach to GREEN (Hold 45s)
    Sig->>Hardware: Hold North, South, East at RED
    
    Note over Det,Sig: Ambulance crosses and exits intersection
    Det->>Sig: Confirm lane cleared of emergency vehicle
    Sig->>Sig: Reset Emergency Flag & Restore D-ATSA Adaptive Cycle
    Sig->>UI: Clear Emergency Status Banner
```

### 5.3 Sequence 3: Traffic Violation Detection & Evidence Logging
```mermaid
sequenceDiagram
    autonumber
    participant Track as VehicleTracker
    participant Audit as IncidentDetector
    participant Storage as File System & CSV
    participant UI as Web Dashboard

    Track->>Audit: check_violations(active_vehicles, signal_state, frame)
    loop For each active vehicle
        alt Vehicle Speed > Speed Limit (60 km/h)
            Audit->>Audit: Flag OVERSPEEDING incident
            Audit->>Storage: Crop vehicle bounding box & save JPEG snapshot
            Audit->>Storage: Append row to violations_log.csv
            Audit->>Audit: Add incident to recent memory buffer
        else Signal == RED and Vehicle in Intersection Box and Speed > 48 km/h
            Audit->>Audit: Flag RED_LIGHT_VIOLATION incident
            Audit->>Storage: Save violation snapshot JPEG
            Audit->>Storage: Append row to CSV
        end
    end
    UI->>Audit: Request recent violations (/api/telemetry)
    Audit-->>UI: Return JSON array with snapshots & severity
```

---

## 6. UML State Machine Diagram (Finite State Machine)

```mermaid
stateDiagram-v2
    [*] --> NS_GREEN : System Boot & Init

    state NS_GREEN {
        [*] --> Counting_NS
        Counting_NS --> NS_Green_Extended : Density_NS > High_Threshold
        Counting_NS --> NS_Timeout : Countdown <= 0
    }

    NS_GREEN --> NS_YELLOW : Green Time Expired
    
    state NS_YELLOW {
        [*] --> Yellow_Clearance_3s
    }

    NS_YELLOW --> ALL_RED_1 : Clearance Complete
    ALL_RED_1 --> EW_GREEN : All-Red Interval Complete (1s)

    state EW_GREEN {
        [*] --> Counting_EW
        Counting_EW --> EW_Green_Extended : Density_EW > High_Threshold
        Counting_EW --> EW_Timeout : Countdown <= 0
    }

    EW_GREEN --> EW_YELLOW : Green Time Expired

    state EW_YELLOW {
        [*] --> Yellow_Clearance_3s
    }

    EW_YELLOW --> ALL_RED_2 : Clearance Complete
    ALL_RED_2 --> NS_GREEN : All-Red Interval Complete (1s)

    NS_GREEN --> EMERGENCY_PREEMPTION : Ambulance in East/West Lane
    EW_GREEN --> EMERGENCY_PREEMPTION : Ambulance in North/South Lane
    
    state EMERGENCY_PREEMPTION {
        [*] --> Emergency_Yellow_Flash
        Emergency_Yellow_Flash --> Emergency_Green_Hold
        Emergency_Green_Hold --> Emergency_Exit_Verification
    }

    EMERGENCY_PREEMPTION --> NS_GREEN : Emergency Vehicle Cleared
```

---

## 7. UML Activity Diagram (Frame Execution Pipeline)

```mermaid
flowchart TD
    START([Start Frame Cycle]) --> CAPTURE[Read Next Frame from Video Source]
    CAPTURE --> CHECK_RET{Frame Valid?}
    CHECK_RET -- No --> LOOP_RESET[Reset Video to Frame 0] --> CAPTURE
    CHECK_RET -- Yes --> PREPROCESS[Convert BGR to Grayscale & Gaussian Blur]
    
    PREPROCESS --> MOG2[Apply MOG2 Background Subtraction]
    MOG2 --> MORPH[Morphological Dilation & Closing Filters]
    MORPH --> CONTOURS[Find External Contours]
    
    CONTOURS --> FILTER_CONTOUR{Contour Area >= min_area?}
    FILTER_CONTOUR -- No --> DISCARD[Ignore Noise]
    FILTER_CONTOUR -- Yes --> CLASSIFY[Extract Geometry, Aspect Ratio & Color Spectrum]
    
    CLASSIFY --> MATCH_TRACKER[Compute Euclidean Distances to Existing Objects]
    MATCH_TRACKER --> UPDATE_TRACKS[Assign Persistent IDs & Calculate Smooth Speed]
    
    UPDATE_TRACKS --> COMPUTE_DENSITY[Calculate Lane Densities with PCE Weights]
    COMPUTE_DENSITY --> SIGNAL_STEP[Update D-ATSA Signal State & Timers]
    
    SIGNAL_STEP --> CHECK_VIOLATION{Check Violations: Speeding / Red-Light?}
    CHECK_VIOLATION -- Yes --> SAVE_VIOLATION[Save Crop Snapshot & Append to CSV]
    CHECK_VIOLATION -- No --> OVERLAYS[Render Clean Bounding Boxes & HUD Overlays]
    
    SAVE_VIOLATION --> OVERLAYS
    OVERLAYS --> BROADCAST[Encode MJPEG & Update Telemetry Cache]
    BROADCAST --> END([Yield to Web Stream & Sleep 33ms])
```

---

## 8. UML Component Diagram

```mermaid
flowchart TD
    subgraph CORE_MODULES["Core AI Engine Components (Python / OpenCV)"]
        DET_COMP["[Component]\nVehicleDetector\n(detector.py)"]
        TRACK_COMP["[Component]\nVehicleTracker\n(tracker.py)"]
        SIG_COMP["[Component]\nTrafficSignalController\n(traffic_signal_controller.py)"]
        INC_COMP["[Component]\nIncidentDetector\n(incident_detector.py)"]
        SIM_COMP["[Component]\nTrafficVideoSimulator\n(video_generator.py)"]
    end

    subgraph WEB_SERVER["Web & API Server Layer"]
        APP_COMP["[Component]\nFlask Web Application\n(app.py)"]
    end

    subgraph DATA_STORAGE["Data Storage & Logging"]
        CSV_FILE[("violations_log.csv")]
        SNAP_DIR[("data/violations/*.jpg")]
        VIDEO_DIR[("data/sample_videos/*.mp4")]
    end

    subgraph FRONTEND["Web Client Frontend (Browser)"]
        UI_DASH["[UI]\nDashboard View\n(index.html)"]
        JS_ENGINE["[Script]\nTelemetry Poller & Charts\n(dashboard.js)"]
        CSS_STYLE["[Style]\nDark Glassmorphism Theme\n(style.css)"]
    end

    SIM_COMP --> VIDEO_DIR
    VIDEO_DIR --> DET_COMP
    DET_COMP --> TRACK_COMP
    TRACK_COMP --> SIG_COMP
    TRACK_COMP --> INC_COMP
    INC_COMP --> CSV_FILE
    INC_COMP --> SNAP_DIR

    DET_COMP --> APP_COMP
    TRACK_COMP --> APP_COMP
    SIG_COMP --> APP_COMP
    INC_COMP --> APP_COMP

    APP_COMP --> UI_DASH
    APP_COMP --> JS_ENGINE
    APP_COMP --> CSS_STYLE
```

---

## 9. UML Deployment Diagram

```mermaid
flowchart TD
    subgraph EDGE_HARDWARE["Physical Hardware Node (Local PC / Edge Server)"]
        subgraph OS["Host OS: Windows / Linux / Docker Container"]
            subgraph PYTHON_ENV["Python 3.10+ Execution Runtime"]
                FLASK_INST["Flask WSGI Application Server (:5000)"]
                OPENCV_RUNTIME["OpenCV 4.8+ / NumPy Core Engine"]
                AI_PIPELINE["Perception & Tracking Threads"]
            end
            subgraph STORAGE_NODE["Local File System"]
                VID_STORE["MP4 Simulation Feeds"]
                CSV_DB["Violation Audit Log CSV"]
                IMG_STORE["Violation Snapshots JPEG"]
            end
        end
    end

    subgraph CLIENT_DEVICES["Client Access Devices (Any Network)"]
        DESKTOP_BROWSER["🖥️ Desktop / Laptop Web Browser"]
        MOBILE_BROWSER["📱 Smartphone / Tablet Browser"]
    end

    FLASK_INST <-->|HTTP REST & MJPEG Stream| DESKTOP_BROWSER
    FLASK_INST <-->|HTTP REST & MJPEG Stream| MOBILE_BROWSER
    OPENCV_RUNTIME --> VID_STORE
    AI_PIPELINE --> CSV_DB
    AI_PIPELINE --> IMG_STORE
```

---

## 10. Data Flow Diagrams

### Data Flow Diagram (DFD Level 0 - Context Level)
```mermaid
flowchart LR
    CAM["CCTV Camera / Video Feeds"] -->|"Raw Video Stream"| SYSTEM(("Traffic-Vision AI\nCentral System"))
    OPERATOR["Traffic Control Operator"] -->|"Control Inputs (Modes, Speed Limits)"| SYSTEM
    SYSTEM -->|"Live Video Stream & Traffic Telemetry"| OPERATOR
    SYSTEM -->|"Adaptive Signal Light States"| LIGHTS["4-Way Intersection Physical Lights"]
    SYSTEM -->|"Safety Violation Records & Snapshots"| POLICE["Law Enforcement / Municipal Portal"]
```

### Data Flow Diagram (DFD Level 1 - Subsystem Level)
```mermaid
flowchart TD
    CAM["Video Source"] --> P1["1.0 Pre-Processing & Detection"]
    P1 -->|"Bounding Boxes & Classes"| P2["2.0 Multi-Object Tracking"]
    P2 -->|"Tracked IDs & Centroid Positions"| P3["3.0 Kinematics & Lane Estimation"]
    P3 -->|"Lane Counts & PCE Densities"| P4["4.0 Adaptive Signal Timing (D-ATSA)"]
    P3 -->|"Speed & Trajectories"| P5["5.0 Incident Violation Audit"]
    P4 -->|"Signal Display States"| P6["6.0 Web Dashboard & REST Server"]
    P5 -->|"CSV Rows & Snapshots"| P6
    P6 -->|"MJPEG Stream & JSON Telemetry"| CLIENT["User Web Client"]
```

---

## 11. Data Models & Schema Specifications

### 11.1 Telemetry API Payload Schema (`/api/telemetry`)
```json
{
  "active_vehicle_count": 8,
  "cumulative_counted": 142,
  "class_breakdown": {
    "Car": 95,
    "Bus": 12,
    "Truck": 8,
    "Motorcycle": 24,
    "Ambulance": 3
  },
  "average_speed_kmh": 36.4,
  "congestion_index": 57,
  "current_source": "normal",
  "speed_limit": 60.0,
  "violations_count": 4,
  "signals": {
    "North": "GREEN",
    "South": "GREEN",
    "East": "RED",
    "West": "RED",
    "phase": "NS",
    "state": "GREEN",
    "countdown": 24,
    "allocated_green": 32,
    "emergency_mode": false,
    "emergency_lane": null,
    "co2_saved_kg": 0.48,
    "wait_time_saved_sec": 382,
    "lane_densities": {
      "North": 3.0,
      "South": 2.0,
      "East": 1.0,
      "West": 0.0
    }
  }
}
```

### 11.2 Violation Audit Record Schema (`violations_log.csv`)
| Field Name | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `Incident_ID` | String | Unique sequential incident code | `INC-0014` |
| `Timestamp` | DateTime | ISO Timestamp of occurrence | `2026-10-02 22:45:10` |
| `Vehicle_ID` | Integer | Persistent tracking object ID | `#48` |
| `Vehicle_Type` | String | Classified vehicle category | `Car` |
| `Speed_KMH` | Float | Calculated kinematic speed | `74.2` |
| `Speed_Limit` | Float | Configured urban speed limit | `60.0` |
| `Violation_Type` | String | Specific safety infraction | `Over-speeding` |
| `Lane` | String | Approach lane identifier | `North Approach` |
| `Snapshot_File` | String | Relative path to JPEG snapshot | `speed_viol_48.jpg` |

---

## 12. Mathematical Algorithms & Control Formulas

### 1. Passenger Car Equivalent (PCE) Lane Density:
$$\text{Density}_L = \sum_{i=1}^{N_L} W(v_i)$$

Where:
$$W(\text{Car}) = 1.0, \quad W(\text{Bus}) = 2.8, \quad W(\text{Truck}) = 2.5, \quad W(\text{Motorcycle}) = 0.5, \quad W(\text{Ambulance}) = 15.0$$

### 2. D-ATSA Dynamic Green Time Allocation:
$$G_{\text{allocated}} = \max\left(G_{\min}, \min\left(G_{\min} + \left(\frac{\text{Density}_{\text{Phase}}}{\text{Total Density} + \epsilon}\right) \cdot (G_{\max} - G_{\min}) \cdot 1.3, \; G_{\max}\right)\right)$$

Where:
- $G_{\min} = 12\text{ s}$ (Pedestrian clearance minimum boundary)
- $G_{\max} = 65\text{ s}$ (Starvation prevention maximum boundary)

### 3. Kinematic Speed Estimation:
$$v_{\text{inst}} = \left(\frac{\sqrt{(x_t - x_{t-1})^2 + (y_t - y_{t-1})^2}}{\Delta t}\right) \times C_{\text{speed}}$$
$$v_{\text{smooth}} = 0.82 \cdot v_{\text{prev}} + 0.18 \cdot v_{\text{inst}}$$

---

*Document Generated for AI-Based Smart Traffic Monitoring Major Project Submission.*
