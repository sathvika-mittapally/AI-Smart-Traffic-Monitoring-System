import cv2
import numpy as np
import os
import random
import math

class TrafficVideoSimulator:
    def __init__(self, width=960, height=540, fps=30):
        self.width = width
        self.height = height
        self.fps = fps
        
    def _draw_road_background(self, frame):
        w, h = self.width, self.height
        cx, cy = w // 2, h // 2
        road_w = 180 # Clean standard road width
        
        # 1. Natural muted roadside terrain
        frame[:] = (50, 60, 54) # Muted slate green
        
        # 2. Sidewalk borders (Clean light gray curb)
        curb_col = (140, 145, 150)
        cv2.rectangle(frame, (cx - road_w//2 - 12, 0), (cx + road_w//2 + 12, h), curb_col, -1)
        cv2.rectangle(frame, (0, cy - road_w//2 - 12), (w, cy + road_w//2 + 12), curb_col, -1)
        
        # 3. Clean Asphalt Road (Dark Charcoal)
        asphalt = (38, 40, 44)
        cv2.rectangle(frame, (cx - road_w//2, 0), (cx + road_w//2, h), asphalt, -1)
        cv2.rectangle(frame, (0, cy - road_w//2), (w, cy + road_w//2), asphalt, -1)
        
        # 4. Center Junction Box
        cv2.rectangle(frame, (cx - road_w//2, cy - road_w//2), (cx + road_w//2, cy + road_w//2), (42, 44, 48), -1)
        
        # 5. Yellow Solid Center Dividers
        yellow = (0, 210, 250)
        cv2.line(frame, (cx, 0), (cx, cy - road_w//2 - 20), yellow, 2)
        cv2.line(frame, (cx, cy + road_w//2 + 20), (cx, h), yellow, 2)
        cv2.line(frame, (0, cy), (cx - road_w//2 - 20, cy), yellow, 2)
        cv2.line(frame, (cx + road_w//2 + 20, cy), (w, cy), yellow, 2)
        
        # 6. White Dashed Lane Dividers
        white = (225, 230, 235)
        dash_len = 15
        gap_len = 15
        
        # North lanes
        for y in range(0, cy - road_w//2 - 22, dash_len + gap_len):
            cv2.line(frame, (cx - road_w//4, y), (cx - road_w//4, y + dash_len), white, 2)
            cv2.line(frame, (cx + road_w//4, y), (cx + road_w//4, y + dash_len), white, 2)
            
        # South lanes
        for y in range(cy + road_w//2 + 22, h, dash_len + gap_len):
            cv2.line(frame, (cx - road_w//4, y), (cx - road_w//4, y + dash_len), white, 2)
            cv2.line(frame, (cx + road_w//4, y), (cx + road_w//4, y + dash_len), white, 2)
            
        # West lanes
        for x in range(0, cx - road_w//2 - 22, dash_len + gap_len):
            cv2.line(frame, (x, cy - road_w//4), (x + dash_len, cy - road_w//4), white, 2)
            cv2.line(frame, (x, cy + road_w//4), (x + dash_len, cy + road_w//4), white, 2)
            
        # East lanes
        for x in range(cx + road_w//2 + 22, w, dash_len + gap_len):
            cv2.line(frame, (x, cy - road_w//4), (x + dash_len, cy - road_w//4), white, 2)
            cv2.line(frame, (x, cy + road_w//4), (x + dash_len, cy + road_w//4), white, 2)
            
        # 7. Zebra Crossings (Pedestrian Walkways)
        zw = 10
        for offset in range(-road_w//2 + 4, road_w//2 - 4, zw + 8):
            cv2.rectangle(frame, (cx + offset, cy - road_w//2 - 20), (cx + offset + zw, cy - road_w//2 - 4), white, -1)
            cv2.rectangle(frame, (cx + offset, cy + road_w//2 + 4), (cx + offset + zw, cy + road_w//2 + 20), white, -1)
            cv2.rectangle(frame, (cx - road_w//2 - 20, cy + offset), (cx - road_w//2 - 4, cy + offset + zw), white, -1)
            cv2.rectangle(frame, (cx + road_w//2 + 4, cy + offset), (cx + road_w//2 + 20, cy + offset + zw), white, -1)
            
        # 8. Solid White Stop Bars
        cv2.line(frame, (cx - road_w//2, cy - road_w//2 - 21), (cx + road_w//2, cy - road_w//2 - 21), white, 3)
        cv2.line(frame, (cx - road_w//2, cy + road_w//2 + 21), (cx + road_w//2, cy + road_w//2 + 21), white, 3)
        cv2.line(frame, (cx - road_w//2 - 21, cy - road_w//2), (cx - road_w//2 - 21, cy + road_w//2), white, 3)
        cv2.line(frame, (cx + road_w//2 + 21, cy - road_w//2), (cx + road_w//2 + 21, cy + road_w//2), white, 3)

    def _draw_traffic_light_posts(self, frame, signals):
        """
        Draws realistic physical 3-lens traffic light heads at the 4 approach corners.
        """
        w, h = self.width, self.height
        cx, cy = w // 2, h // 2
        road_w = 180

        # Post positions and orientations: (px, py, orientation, lane_key)
        # Orientation: 'V' for vertical box, 'H' for horizontal box
        posts = [
            # North Approach Stop Light (Top-Left corner of intersection)
            (cx - road_w//2 - 22, cy - road_w//2 - 38, 'V', 'North'),
            # South Approach Stop Light (Bottom-Right corner of intersection)
            (cx + road_w//2 + 10, cy + road_w//2 + 12, 'V', 'South'),
            # West Approach Stop Light (Bottom-Left corner of intersection)
            (cx - road_w//2 - 38, cy + road_w//2 + 10, 'H', 'West'),
            # East Approach Stop Light (Top-Right corner of intersection)
            (cx + road_w//2 + 12, cy - road_w//2 - 22, 'H', 'East')
        ]

        for px, py, orient, lane in posts:
            sig = signals.get(lane, 'RED')
            
            # Colors: Active vs Inactive (Dim)
            red_c = (0, 0, 245) if sig == 'RED' else (25, 25, 65)
            yel_c = (0, 215, 245) if sig == 'YELLOW' else (25, 60, 65)
            grn_c = (40, 230, 90) if sig == 'GREEN' else (20, 55, 30)

            if orient == 'V':
                box_w, box_h = 14, 34
                cv2.rectangle(frame, (px, py), (px + box_w, py + box_h), (20, 22, 26), -1)
                cv2.rectangle(frame, (px, py), (px + box_w, py + box_h), (80, 85, 95), 1)
                
                # 3 Circles: Red, Yellow, Green
                cv2.circle(frame, (px + 7, py + 6), 4, red_c, -1)
                cv2.circle(frame, (px + 7, py + 17), 4, yel_c, -1)
                cv2.circle(frame, (px + 7, py + 28), 4, grn_c, -1)
                
                # Active glow border
                if sig == 'RED':
                    cv2.circle(frame, (px + 7, py + 6), 5, (50, 50, 255), 1)
                elif sig == 'YELLOW':
                    cv2.circle(frame, (px + 7, py + 17), 5, (50, 230, 255), 1)
                elif sig == 'GREEN':
                    cv2.circle(frame, (px + 7, py + 28), 5, (80, 255, 120), 1)
            else:
                box_w, box_h = 34, 14
                cv2.rectangle(frame, (px, py), (px + box_w, py + box_h), (20, 22, 26), -1)
                cv2.rectangle(frame, (px, py), (px + box_w, py + box_h), (80, 85, 95), 1)
                
                # 3 Circles: Red, Yellow, Green
                cv2.circle(frame, (px + 6, py + 7), 4, red_c, -1)
                cv2.circle(frame, (px + 17, py + 7), 4, yel_c, -1)
                cv2.circle(frame, (px + 28, py + 7), 4, grn_c, -1)
                
                # Active glow border
                if sig == 'RED':
                    cv2.circle(frame, (px + 6, py + 7), 5, (50, 50, 255), 1)
                elif sig == 'YELLOW':
                    cv2.circle(frame, (px + 17, py + 7), 5, (50, 230, 255), 1)
                elif sig == 'GREEN':
                    cv2.circle(frame, (px + 28, py + 7), 5, (80, 255, 120), 1)

    def _draw_vehicle(self, frame, x, y, vtype, color, direction, frame_idx):
        is_vert = direction in ['N_to_S', 'S_to_N']
        
        if vtype == "Car":
            w_size, l_size = (32, 60) if is_vert else (60, 32)
        elif vtype == "Bus":
            w_size, l_size = (38, 105) if is_vert else (105, 38)
        elif vtype == "Truck":
            w_size, l_size = (40, 88) if is_vert else (88, 40)
        elif vtype == "Ambulance":
            w_size, l_size = (34, 70) if is_vert else (70, 34)
        elif vtype == "Motorcycle":
            w_size, l_size = (16, 36) if is_vert else (36, 16)
        else:
            w_size, l_size = (30, 56)
            
        x1 = int(x - w_size // 2)
        y1 = int(y - l_size // 2)
        x2 = int(x + w_size // 2)
        y2 = int(y + l_size // 2)
        
        # Drop shadow
        cv2.rectangle(frame, (x1 + 2, y1 + 2), (x2 + 3, y2 + 3), (20, 22, 25), -1)
        
        # Main Body
        if vtype == "Ambulance":
            cv2.rectangle(frame, (x1, y1), (x2, y2), (250, 250, 250), -1) # Clean white body
            # Red cross
            rc = (0, 0, 230)
            cx, cy = (x1 + x2)//2, (y1 + y2)//2
            cv2.rectangle(frame, (cx - 3, cy - 12), (cx + 3, cy + 12), rc, -1)
            cv2.rectangle(frame, (cx - 12, cy - 3), (cx + 12, cy + 3), rc, -1)
            
            # Flashing Strobe (Red / Blue)
            flash = (frame_idx // 4) % 2
            s1 = (0, 0, 240) if flash == 0 else (220, 0, 0)
            s2 = (220, 0, 0) if flash == 0 else (0, 0, 240)
            if is_vert:
                cv2.circle(frame, (cx - 8, y1 + 8), 4, s1, -1)
                cv2.circle(frame, (cx + 8, y1 + 8), 4, s2, -1)
            else:
                cv2.circle(frame, (x1 + 8, cy - 8), 4, s1, -1)
                cv2.circle(frame, (x1 + 8, cy + 8), 4, s2, -1)
        else:
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, -1)
            
        # Subtle dark border
        cv2.rectangle(frame, (x1, y1), (x2, y2), (25, 27, 30), 1)
        
        # Windshields & Windows
        glass = (185, 205, 220)
        if vtype in ["Car", "Bus", "Truck", "Ambulance"]:
            if is_vert:
                wy1 = y1 + 10 if direction == 'N_to_S' else y2 - 18
                cv2.rectangle(frame, (x1 + 4, wy1), (x2 - 4, wy1 + 7), glass, -1)
                # Rear window
                ry1 = y2 - 14 if direction == 'N_to_S' else y1 + 7
                cv2.rectangle(frame, (x1 + 4, ry1), (x2 - 4, ry1 + 5), (60, 65, 75), -1)
            else:
                wx1 = x1 + 10 if direction == 'W_to_E' else x2 - 18
                cv2.rectangle(frame, (wx1, y1 + 4), (wx1 + 7, y2 - 4), glass, -1)
                # Rear window
                rx1 = x2 - 14 if direction == 'W_to_E' else x1 + 7
                cv2.rectangle(frame, (rx1, y1 + 4), (rx1 + 5, y2 - 4), (60, 65, 75), -1)

    def _get_signal_for_frame(self, f_idx, scenario):
        """
        Computes the active signal phase (NS vs EW) for any given simulation frame.
        """
        if scenario == "emergency_rush":
            # Emergency vehicle approaching on West lane -> EW Green wave!
            if f_idx > 45:
                return {
                    'North': 'RED', 'South': 'RED',
                    'East': 'GREEN', 'West': 'GREEN',
                    'phase': 'EW', 'state': 'GREEN'
                }

        # Standard repeating cycle (total cycle: 400 frames ~ 14-16s)
        cycle_len = 420
        phase_pos = f_idx % cycle_len

        if phase_pos < 170:
            # NS Green Phase (EW Red)
            return {'North': 'GREEN', 'South': 'GREEN', 'East': 'RED', 'West': 'RED', 'phase': 'NS', 'state': 'GREEN'}
        elif phase_pos < 210:
            # NS Yellow Phase
            return {'North': 'YELLOW', 'South': 'YELLOW', 'East': 'RED', 'West': 'RED', 'phase': 'NS', 'state': 'YELLOW'}
        elif phase_pos < 380:
            # EW Green Phase (NS Red)
            return {'North': 'RED', 'South': 'RED', 'East': 'GREEN', 'West': 'GREEN', 'phase': 'EW', 'state': 'GREEN'}
        else:
            # EW Yellow Phase
            return {'North': 'RED', 'South': 'RED', 'East': 'YELLOW', 'West': 'YELLOW', 'phase': 'EW', 'state': 'YELLOW'}

    def generate_video(self, output_path, scenario="normal", duration_sec=30):
        total_frames = self.fps * duration_sec
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, self.fps, (self.width, self.height))
        
        w, h = self.width, self.height
        cx, cy = w // 2, h // 2
        road_w = 180
        
        lane_coords = {
            'N_to_S': (cx - road_w//4, -60, 0, 1),
            'S_to_N': (cx + road_w//4, h + 60, 0, -1),
            'W_to_E': (-60, cy + road_w//4, 1, 0),
            'E_to_W': (w + 60, cy - road_w//4, -1, 0)
        }

        # Stop bar coordinates for each lane
        stop_bars = {
            'N_to_S': cy - road_w//2 - 21,  # 159
            'S_to_N': cy + road_w//2 + 21,  # 381
            'W_to_E': cx - road_w//2 - 21,  # 369
            'E_to_W': cx + road_w//2 + 21   # 591
        }
        
        # Automotive colors
        car_colors = [
            (205, 45, 45),   # Classic Red
            (45, 125, 215),  # Deep Blue
            (225, 230, 235), # Silver
            (35, 38, 42),    # Midnight Black
            (235, 175, 25),  # Amber Gold
            (40, 155, 75),   # Forest Green
            (130, 135, 140)  # Slate Gray
        ]
        
        # Pre-populate active vehicles distributed naturally across the junction
        active_vehicles = [
            {'x': cx - road_w//4, 'y': 80.0, 'dx': 0, 'dy': 1, 'speed': 3.6, 'max_speed': 3.8, 'vtype': 'Car', 'color': car_colors[0], 'direction': 'N_to_S', 'is_violator': False},
            {'x': cx - road_w//4, 'y': -10.0, 'dx': 0, 'dy': 1, 'speed': 3.9, 'max_speed': 4.1, 'vtype': 'Motorcycle', 'color': car_colors[4], 'direction': 'N_to_S', 'is_violator': False},
            {'x': cx + road_w//4, 'y': 460.0, 'dx': 0, 'dy': -1, 'speed': 3.2, 'max_speed': 3.4, 'vtype': 'Bus', 'color': (35, 130, 210), 'direction': 'S_to_N', 'is_violator': False},
            {'x': cx + road_w//4, 'y': 310.0, 'dx': 0, 'dy': -1, 'speed': 3.8, 'max_speed': 4.0, 'vtype': 'Car', 'color': car_colors[1], 'direction': 'S_to_N', 'is_violator': False},
            {'x': 110.0, 'y': cy + road_w//4, 'dx': 1, 'dy': 0, 'speed': 0.0, 'max_speed': 3.8, 'vtype': 'Car', 'color': car_colors[2], 'direction': 'W_to_E', 'is_violator': False},
            {'x': 250.0, 'y': cy + road_w//4, 'dx': 1, 'dy': 0, 'speed': 0.0, 'max_speed': 3.5, 'vtype': 'Truck', 'color': (115, 95, 80), 'direction': 'W_to_E', 'is_violator': False},
            {'x': 860.0, 'y': cy - road_w//4, 'dx': -1, 'dy': 0, 'speed': 0.0, 'max_speed': 3.7, 'vtype': 'Car', 'color': car_colors[5], 'direction': 'E_to_W', 'is_violator': False},
            {'x': 710.0, 'y': cy - road_w//4, 'dx': -1, 'dy': 0, 'speed': 0.0, 'max_speed': 4.2, 'vtype': 'Motorcycle', 'color': car_colors[4], 'direction': 'E_to_W', 'is_violator': False}
        ]
        
        spawn_rate = 0.12 if scenario == "normal" else (0.22 if scenario == "heavy_traffic" else 0.14)
        ambulance_spawned = False
        
        base_bg = np.zeros((h, w, 3), dtype=np.uint8)
        self._draw_road_background(base_bg)
        
        print(f"[*] Generating signal-following traffic simulation '{scenario}' -> {output_path} ({total_frames} frames)...")

        for f_idx in range(total_frames):
            frame = base_bg.copy()
            current_signals = self._get_signal_for_frame(f_idx, scenario)
            
            # Draw physical 3-lens traffic signal posts with live glowing lenses
            self._draw_traffic_light_posts(frame, current_signals)

            # Spawn incoming vehicles
            if random.random() < spawn_rate:
                dir_key = random.choice(list(lane_coords.keys()))
                lx, ly, dx, dy = lane_coords[dir_key]
                
                # Only spawn ambulance in the dedicated emergency scenario
                if scenario == "emergency_rush" and not ambulance_spawned and f_idx > 30:
                    vtype = "Ambulance"
                    ambulance_spawned = True
                    color = (250, 250, 250)
                    max_speed = 5.2
                    dir_key = 'W_to_E'
                    lx, ly, dx, dy = lane_coords[dir_key]
                    is_viol = False
                else:
                    roll = random.random()
                    is_viol = (random.random() < 0.04) # 4% rare aggressive driver
                    if roll < 0.65:
                        vtype = "Car"
                        max_speed = random.uniform(3.4, 4.4)
                        color = random.choice(car_colors)
                    elif roll < 0.82:
                        vtype = "Motorcycle"
                        max_speed = random.uniform(3.8, 4.8)
                        color = (235, 175, 25)
                    elif roll < 0.93:
                        vtype = "Bus"
                        max_speed = random.uniform(2.8, 3.4)
                        color = (35, 130, 210)
                    else:
                        vtype = "Truck"
                        max_speed = random.uniform(2.6, 3.2)
                        color = (115, 95, 80)
                        
                can_spawn = True
                for v in active_vehicles:
                    if v['direction'] == dir_key:
                        dist = math.hypot(v['x'] - lx, v['y'] - ly)
                        if dist < 120:
                            can_spawn = False
                            break
                            
                if can_spawn:
                    active_vehicles.append({
                        'x': float(lx),
                        'y': float(ly),
                        'dx': dx,
                        'dy': dy,
                        'speed': max_speed * 0.8,
                        'max_speed': max_speed,
                        'vtype': vtype,
                        'color': color,
                        'direction': dir_key,
                        'is_violator': is_viol
                    })

            # Vehicle Kinematics & Signal Compliance Logic:
            # Group vehicles by lane and sort them by position along their lane direction (lead vehicles first)
            lanes_dict = {'N_to_S': [], 'S_to_N': [], 'W_to_E': [], 'E_to_W': []}
            for v in active_vehicles:
                lanes_dict[v['direction']].append(v)
                
            # Sort:
            lanes_dict['N_to_S'].sort(key=lambda item: item['y'], reverse=True) # Highest y is further down
            lanes_dict['S_to_N'].sort(key=lambda item: item['y'])               # Lowest y is further up
            lanes_dict['W_to_E'].sort(key=lambda item: item['x'], reverse=True) # Highest x is further right
            lanes_dict['E_to_W'].sort(key=lambda item: item['x'])               # Lowest x is further left

            # Update speeds with intelligent stopping, queueing, and smooth acceleration
            for dir_key, v_list in lanes_dict.items():
                lane_name = 'North' if dir_key == 'N_to_S' else ('South' if dir_key == 'S_to_N' else ('West' if dir_key == 'W_to_E' else 'East'))
                signal_state = current_signals.get(lane_name, 'RED')
                stop_coord = stop_bars[dir_key]
                
                for idx, v in enumerate(v_list):
                    is_ambulance = (v['vtype'] == 'Ambulance')
                    is_viol = v.get('is_violator', False)
                    target_speed = v['max_speed']
                    
                    # 1. Check distance to stop line if signal is RED or YELLOW
                    if signal_state in ['RED', 'YELLOW'] and not is_ambulance and not is_viol:
                        if dir_key == 'N_to_S':
                            # Moving downwards toward stop_coord (159)
                            if v['y'] < stop_coord - 20: # Behind stop bar
                                dist_to_stop = (stop_coord - 28) - v['y']
                                if dist_to_stop < 140:
                                    target_speed = max(0.0, (dist_to_stop / 140.0) * v['max_speed'])
                                    if dist_to_stop <= 6:
                                        target_speed = 0.0
                        elif dir_key == 'S_to_N':
                            # Moving upwards toward stop_coord (381)
                            if v['y'] > stop_coord + 20: # Behind stop bar
                                dist_to_stop = v['y'] - (stop_coord + 28)
                                if dist_to_stop < 140:
                                    target_speed = max(0.0, (dist_to_stop / 140.0) * v['max_speed'])
                                    if dist_to_stop <= 6:
                                        target_speed = 0.0
                        elif dir_key == 'W_to_E':
                            # Moving rightwards toward stop_coord (369)
                            if v['x'] < stop_coord - 20: # Behind stop bar
                                dist_to_stop = (stop_coord - 28) - v['x']
                                if dist_to_stop < 140:
                                    target_speed = max(0.0, (dist_to_stop / 140.0) * v['max_speed'])
                                    if dist_to_stop <= 6:
                                        target_speed = 0.0
                        elif dir_key == 'E_to_W':
                            # Moving leftwards toward stop_coord (591)
                            if v['x'] > stop_coord + 20: # Behind stop bar
                                dist_to_stop = v['x'] - (stop_coord + 28)
                                if dist_to_stop < 140:
                                    target_speed = max(0.0, (dist_to_stop / 140.0) * v['max_speed'])
                                    if dist_to_stop <= 6:
                                        target_speed = 0.0

                    # 2. Check distance to vehicle immediately ahead in the same lane (Car-following / Queueing)
                    if idx > 0:
                        v_ahead = v_list[idx - 1]
                        dist_ahead = math.hypot(v_ahead['x'] - v['x'], v_ahead['y'] - v['y'])
                        safe_gap = 62.0 if v['vtype'] != 'Bus' else 80.0
                        
                        if dist_ahead < safe_gap + 70:
                            following_speed = max(0.0, ((dist_ahead - safe_gap) / 70.0) * v_ahead['speed'])
                            if dist_ahead <= safe_gap:
                                following_speed = 0.0
                            target_speed = min(target_speed, following_speed)

                    # Smooth acceleration / deceleration filter
                    if target_speed < v['speed']:
                        v['speed'] = max(target_speed, v['speed'] - 0.22) # Smooth braking
                    else:
                        v['speed'] = min(target_speed, v['speed'] + 0.14) # Smooth acceleration

            # Move and render vehicles
            remaining_vehicles = []
            for v in active_vehicles:
                v['x'] += v['dx'] * v['speed']
                v['y'] += v['dy'] * v['speed']
                
                if -120 <= v['x'] <= w + 120 and -120 <= v['y'] <= h + 120:
                    self._draw_vehicle(frame, v['x'], v['y'], v['vtype'], v['color'], v['direction'], f_idx)
                    remaining_vehicles.append(v)
                    
            active_vehicles = remaining_vehicles
            
            # Minimal camera watermark
            cv2.putText(frame, "CAM 01 - JUNCTION A4", (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.50, (220, 225, 230), 1, cv2.LINE_AA)
            
            out.write(frame)
            
        out.release()
        print(f"[+] Video successfully created: {output_path}")

def generate_all_sample_videos(data_dir="data/sample_videos"):
    os.makedirs(data_dir, exist_ok=True)
    sim = TrafficVideoSimulator(width=960, height=540, fps=25)
    
    videos = [
        ("junction_normal.mp4", "normal", 30),
        ("junction_heavy.mp4", "heavy_traffic", 30),
        ("junction_ambulance_emergency.mp4", "emergency_rush", 30)
    ]
    
    for filename, scenario, duration in videos:
        filepath = os.path.join(data_dir, filename)
        sim.generate_video(filepath, scenario=scenario, duration_sec=duration)

if __name__ == "__main__":
    generate_all_sample_videos()

