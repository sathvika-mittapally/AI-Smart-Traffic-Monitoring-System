"""
Smart Traffic System - Incident & Traffic Violation Auditor
Module: core/incident_detector.py

Monitors speeding (>60 km/h), red-light running (>48 km/h during red),
and wrong-way driving on standard 960x540 intersection.
"""

import cv2
import time
import os
import csv
from datetime import datetime

class IncidentDetector:
    def __init__(self, speed_limit_kmh=60.0, output_dir="data/violations"):
        self.speed_limit_kmh = speed_limit_kmh
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.violations_log = []
        self.reported_incident_keys = set()
        
        self.csv_path = os.path.join(self.output_dir, "violations_log.csv")
        self._init_csv()

    def _init_csv(self):
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Incident_ID", "Timestamp", "Vehicle_ID", "Vehicle_Type",
                    "Speed_KMH", "Speed_Limit", "Violation_Type", "Lane", "Snapshot_File"
                ])

    def check_violations(self, active_vehicles, signal_state, current_frame=None):
        new_incidents = []
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for v in active_vehicles:
            vid = v["id"]
            speed = v["speed_kmh"]
            vtype = v["class_name"]
            lane = v["lane_id"]
            is_emergency = v.get("is_emergency", False)
            traj = v.get("trajectory", [])
            cx, cy = v["centroid"]
            
            # 1. Over-speeding (> 60 km/h)
            if speed > self.speed_limit_kmh and not is_emergency:
                incident_key = f"SPEED_{vid}"
                if incident_key not in self.reported_incident_keys:
                    self.reported_incident_keys.add(incident_key)
                    v["violation"] = "OVERSPEEDING"
                    
                    snapshot_filename = f"speed_viol_{vid}_{int(time.time())}.jpg"
                    self._save_snapshot(current_frame, v["bbox"], snapshot_filename)
                    
                    incident = {
                        "incident_id": f"INC-{len(self.violations_log) + 1:04d}",
                        "timestamp": now_str,
                        "vehicle_id": vid,
                        "vehicle_type": vtype,
                        "speed_kmh": speed,
                        "speed_limit": self.speed_limit_kmh,
                        "violation_type": f"Over-speeding ({speed} km/h > {self.speed_limit_kmh} km/h)",
                        "lane": lane,
                        "snapshot": snapshot_filename,
                        "severity": "HIGH" if speed > self.speed_limit_kmh + 12 else "MEDIUM"
                    }
                    self.violations_log.insert(0, incident)
                    new_incidents.append(incident)
                    self._write_to_csv(incident)

            # 2. Aggressive Red-Light Running
            lane_dir = lane.split()[0]
            lane_signal = signal_state.get(lane_dir, "GREEN")
            in_center = (390 <= cx <= 570 and 180 <= cy <= 360)
            
            if lane_signal == "RED" and in_center and not is_emergency and speed > 48.0:
                incident_key = f"REDLIGHT_{vid}"
                if incident_key not in self.reported_incident_keys:
                    self.reported_incident_keys.add(incident_key)
                    v["violation"] = "RED_LIGHT_VIOLATION"
                    
                    snapshot_filename = f"redlight_viol_{vid}_{int(time.time())}.jpg"
                    self._save_snapshot(current_frame, v["bbox"], snapshot_filename)
                    
                    incident = {
                        "incident_id": f"INC-{len(self.violations_log) + 1:04d}",
                        "timestamp": now_str,
                        "vehicle_id": vid,
                        "vehicle_type": vtype,
                        "speed_kmh": speed,
                        "speed_limit": self.speed_limit_kmh,
                        "violation_type": "Red Light Signal Violation",
                        "lane": lane,
                        "snapshot": snapshot_filename,
                        "severity": "CRITICAL"
                    }
                    self.violations_log.insert(0, incident)
                    new_incidents.append(incident)
                    self._write_to_csv(incident)

            # 3. Wrong-Way Movement
            if len(traj) >= 12 and not is_emergency:
                dx = traj[-1][0] - traj[0][0]
                dy = traj[-1][1] - traj[0][1]
                mag = (dx**2 + dy**2)**0.5
                
                if mag > 70:
                    unit_v = (dx / mag, dy / mag)
                    exp_v = v.get("expected_vector", (0, 1))
                    dot = unit_v[0] * exp_v[0] + unit_v[1] * exp_v[1]
                    
                    if dot < -0.85:
                        incident_key = f"WRONGWAY_{vid}"
                        if incident_key not in self.reported_incident_keys:
                            self.reported_incident_keys.add(incident_key)
                            v["violation"] = "WRONG_WAY"
                            
                            snapshot_filename = f"wrongway_viol_{vid}_{int(time.time())}.jpg"
                            self._save_snapshot(current_frame, v["bbox"], snapshot_filename)
                            
                            incident = {
                                "incident_id": f"INC-{len(self.violations_log) + 1:04d}",
                                "timestamp": now_str,
                                "vehicle_id": vid,
                                "vehicle_type": vtype,
                                "speed_kmh": speed,
                                "speed_limit": self.speed_limit_kmh,
                                "violation_type": "Wrong-Way Movement",
                                "lane": lane,
                                "snapshot": snapshot_filename,
                                "severity": "CRITICAL"
                            }
                            self.violations_log.insert(0, incident)
                            new_incidents.append(incident)
                            self._write_to_csv(incident)

        return new_incidents

    def _save_snapshot(self, frame, bbox, filename):
        if frame is None:
            return
        x, y, w, h = bbox
        fh, fw = frame.shape[:2]
        pad_x = int(w * 0.25)
        pad_y = int(h * 0.25)
        x1 = max(0, x - pad_x)
        y1 = max(0, y - pad_y)
        x2 = min(fw, x + w + pad_x)
        y2 = min(fh, y + h + pad_y)
        
        crop = frame[y1:y2, x1:x2]
        if crop.size > 0:
            target_path = os.path.join(self.output_dir, filename)
            cv2.imwrite(target_path, crop)

    def _write_to_csv(self, inc):
        try:
            with open(self.csv_path, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    inc["incident_id"], inc["timestamp"], inc["vehicle_id"],
                    inc["vehicle_type"], inc["speed_kmh"], inc["speed_limit"],
                    inc["violation_type"], inc["lane"], inc["snapshot"]
                ])
        except Exception as e:
            print(f"Error logging to CSV: {e}")

    def get_recent_violations(self, limit=12):
        return self.violations_log[:limit]
