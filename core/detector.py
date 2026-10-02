"""
Smart Traffic System - Vehicle Perception Engine
Module: core/detector.py

Classifies Cars, Buses, Trucks, Motorcycles, and Ambulances using geometry,
area thresholds, and emergency beacon signatures.
"""

import cv2
import numpy as np

class VehicleDetector:
    def __init__(self, confidence_threshold=0.45, min_area=300):
        self.conf_thresh = confidence_threshold
        self.min_area = min_area
        
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=300, varThreshold=35, detectShadows=True
        )

    def detect_emergency_features(self, vehicle_roi):
        if vehicle_roi is None or vehicle_roi.size == 0:
            return False, 0.0
            
        b = vehicle_roi[:, :, 0]
        g = vehicle_roi[:, :, 1]
        r = vehicle_roi[:, :, 2]
        
        blue_px = np.sum((b > 180) & (r < 80))
        red_px = np.sum((r > 180) & (b < 80))
        white_px = np.sum((r > 200) & (g > 200) & (b > 200))
        
        if red_px >= 30 and blue_px >= 6 and white_px >= 180:
            return True, 0.98
            
        return False, 0.0

    def classify_vehicle_type(self, w, h, area, aspect_ratio, roi):
        is_emergency, em_conf = self.detect_emergency_features(roi)
        if is_emergency:
            return "Ambulance", em_conf, (239, 68, 68) # Red
            
        if area > 2800:
            if aspect_ratio > 1.3 or aspect_ratio < 0.7:
                return "Bus", 0.93, (249, 115, 22) # Orange
            else:
                return "Truck", 0.89, (168, 85, 247) # Slate Purple
        elif area > 750:
            return "Car", 0.95, (59, 130, 246) # Blue
        else:
            return "Motorcycle", 0.88, (245, 158, 11) # Amber

    def detect(self, frame):
        h, w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        fg_mask = self.bg_subtractor.apply(blurred)
        
        _, thresh = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        dilated = cv2.dilate(thresh, kernel, iterations=2)
        closing = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        contours, _ = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detections = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < self.min_area:
                continue
                
            x, y, bw, bh = cv2.boundingRect(cnt)
            
            if bw > w * 0.7 or bh > h * 0.7:
                continue
                
            aspect_ratio = float(bw) / float(bh) if bh > 0 else 1.0
            vehicle_roi = frame[max(0, y):min(h, y + bh), max(0, x):min(w, x + bw)]
            
            class_name, conf, color = self.classify_vehicle_type(bw, bh, area, aspect_ratio, vehicle_roi)
            
            cx = int(x + bw / 2)
            cy = int(y + bh / 2)
            
            detections.append({
                "bbox": [x, y, bw, bh],
                "center": (cx, cy),
                "class_name": class_name,
                "confidence": conf,
                "color": color,
                "area": area,
                "is_emergency": (class_name == "Ambulance")
            })
            
        return detections, closing
