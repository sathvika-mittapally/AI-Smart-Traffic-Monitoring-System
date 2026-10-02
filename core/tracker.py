"""
Smart Traffic System - Multi-Object Vehicle Tracker
Module: core/tracker.py

Tracks vehicles, assigns persistent IDs, calculates speed (km/h),
and maintains directional trajectories on standard 960x540 intersection.
"""

import math
import time
from collections import deque
import numpy as np

class VehicleTracker:
    def __init__(self, max_disappeared=15, max_distance=65, speed_calibration_factor=0.20):
        self.next_object_id = 1
        self.objects = {}
        self.disappeared = {}
        self.trajectories = {}
        self.timestamps = {}
        self.vehicle_meta = {}
        
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance
        self.speed_calibration_factor = speed_calibration_factor
        
        self.total_counted = 0
        self.class_counts = {
            "Car": 0,
            "Bus": 0,
            "Truck": 0,
            "Motorcycle": 0,
            "Ambulance": 0,
            "Pedestrian": 0
        }

    def _determine_lane_and_direction(self, centroid, trajectory):
        cx, cy = centroid
        
        # Center is at (480, 270)
        if len(trajectory) >= 3:
            dx = trajectory[-1][0] - trajectory[0][0]
            dy = trajectory[-1][1] - trajectory[0][1]
            if abs(dx) > abs(dy):
                return ("East Approach" if dx < 0 else "West Approach"), (1 if dx > 0 else -1, 0)
            else:
                return ("North Approach" if dy > 0 else "South Approach"), (0, 1 if dy > 0 else -1)
                
        if cy < 270 and abs(cx - 480) < 100:
            return "North Approach", (0, 1)
        elif cy >= 270 and abs(cx - 480) < 100:
            return "South Approach", (0, -1)
        elif cx < 480:
            return "West Approach", (1, 0)
        else:
            return "East Approach", (-1, 0)

    def register(self, centroid, det_info):
        obj_id = self.next_object_id
        self.objects[obj_id] = centroid
        self.disappeared[obj_id] = 0
        self.trajectories[obj_id] = deque(maxlen=25)
        self.trajectories[obj_id].append(centroid)
        self.timestamps[obj_id] = deque(maxlen=25)
        self.timestamps[obj_id].append(time.time())
        
        lane_name, exp_vec = self._determine_lane_and_direction(centroid, self.trajectories[obj_id])
        
        base_speed = 38.0 + np.random.uniform(-4.0, 7.0)
        if det_info.get("is_emergency", False):
            base_speed = 52.0 + np.random.uniform(2.0, 8.0)
            
        c_name = det_info["class_name"]
        
        self.vehicle_meta[obj_id] = {
            "class_name": c_name,
            "bbox": det_info["bbox"],
            "confidence": det_info["confidence"],
            "color": det_info["color"],
            "speed_kmh": round(base_speed, 1),
            "is_emergency": det_info.get("is_emergency", False),
            "entry_time": time.strftime("%H:%M:%S"),
            "lane_id": lane_name,
            "expected_vector": exp_vec,
            "violation": None
        }
        
        self.total_counted += 1
        if c_name in self.class_counts:
            self.class_counts[c_name] += 1
        else:
            self.class_counts[c_name] = 1
            
        self.next_object_id += 1
        return obj_id

    def deregister(self, obj_id):
        for collection in [self.objects, self.disappeared, self.trajectories, self.timestamps, self.vehicle_meta]:
            if obj_id in collection:
                del collection[obj_id]

    def _calculate_instant_speed(self, obj_id, new_centroid):
        if obj_id not in self.trajectories or len(self.trajectories[obj_id]) < 2:
            return self.vehicle_meta[obj_id]["speed_kmh"]
            
        prev_cx, prev_cy = self.trajectories[obj_id][-1]
        prev_time = self.timestamps[obj_id][-1]
        now = time.time()
        
        dt = max(1e-4, now - prev_time)
        pixel_distance = math.hypot(new_centroid[0] - prev_cx, new_centroid[1] - prev_cy)
        speed_raw = (pixel_distance / dt) * self.speed_calibration_factor
        
        current_speed = self.vehicle_meta[obj_id]["speed_kmh"]
        smooth_speed = 0.82 * current_speed + 0.18 * speed_raw
        
        if self.vehicle_meta[obj_id]["is_emergency"]:
            smooth_speed = max(40.0, min(smooth_speed, 75.0))
        else:
            smooth_speed = max(20.0, min(smooth_speed, 65.0))
            
        return round(smooth_speed, 1)

    def update(self, detections):
        if len(detections) == 0:
            for obj_id in list(self.disappeared.keys()):
                self.disappeared[obj_id] += 1
                if self.disappeared[obj_id] > self.max_disappeared:
                    self.deregister(obj_id)
            return self.get_active_vehicles()

        input_centroids = [d["center"] for d in detections]
        
        if len(self.objects) == 0:
            for i, centroid in enumerate(input_centroids):
                self.register(centroid, detections[i])
            return self.get_active_vehicles()

        object_ids = list(self.objects.keys())
        object_centroids = list(self.objects.values())

        D = np.zeros((len(object_centroids), len(input_centroids)), dtype=np.float32)
        for r, oc in enumerate(object_centroids):
            for c, ic in enumerate(input_centroids):
                D[r, c] = math.hypot(oc[0] - ic[0], oc[1] - ic[1])

        rows = D.min(axis=1).argsort()
        cols = D.argmin(axis=1)[rows]

        used_rows = set()
        used_cols = set()

        for (row, col) in zip(rows, cols):
            if row in used_rows or col in used_cols:
                continue

            if D[row, col] > self.max_distance:
                continue

            obj_id = object_ids[row]
            new_centroid = input_centroids[col]
            det_info = detections[col]

            speed = self._calculate_instant_speed(obj_id, new_centroid)

            self.objects[obj_id] = new_centroid
            self.disappeared[obj_id] = 0
            self.trajectories[obj_id].append(new_centroid)
            self.timestamps[obj_id].append(time.time())
            
            lane_name, exp_vec = self._determine_lane_and_direction(new_centroid, self.trajectories[obj_id])
            
            self.vehicle_meta[obj_id]["bbox"] = det_info["bbox"]
            self.vehicle_meta[obj_id]["confidence"] = det_info["confidence"]
            self.vehicle_meta[obj_id]["speed_kmh"] = speed
            self.vehicle_meta[obj_id]["lane_id"] = lane_name
            self.vehicle_meta[obj_id]["expected_vector"] = exp_vec

            used_rows.add(row)
            used_cols.add(col)

        unused_rows = set(range(0, D.shape[0])).difference(used_rows)
        for row in unused_rows:
            obj_id = object_ids[row]
            self.disappeared[obj_id] += 1
            if self.disappeared[obj_id] > self.max_disappeared:
                self.deregister(obj_id)

        unused_cols = set(range(0, D.shape[1])).difference(used_cols)
        for col in unused_cols:
            self.register(input_centroids[col], detections[col])

        return self.get_active_vehicles()

    def get_active_vehicles(self):
        active = []
        for obj_id, centroid in self.objects.items():
            if obj_id in self.vehicle_meta:
                meta = self.vehicle_meta[obj_id]
                active.append({
                    "id": obj_id,
                    "centroid": centroid,
                    "bbox": meta["bbox"],
                    "class_name": meta["class_name"],
                    "confidence": meta["confidence"],
                    "color": meta["color"],
                    "speed_kmh": meta["speed_kmh"],
                    "is_emergency": meta["is_emergency"],
                    "lane_id": meta["lane_id"],
                    "expected_vector": meta.get("expected_vector", (0, 1)),
                    "trajectory": list(self.trajectories[obj_id]),
                    "violation": meta.get("violation", None)
                })
        return active
