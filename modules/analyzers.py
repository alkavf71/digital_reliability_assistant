# modules/analyzers.py

class VibrationAnalyzer:
    @staticmethod
    def get_iso_limit(kw, is_flexible=False):
        """Menentukan Limit ISO 10816-3"""
        if kw < 15: return 4.50
        if 15 <= kw <= 300: return 7.10 if is_flexible else 4.50
        else: return 11.0 if is_flexible else 7.10

    @staticmethod
    def check_severity(value, limit):
        """Output: Status Severity (Good/Warning/Danger)"""
        if value > limit: return "DANGER"
        elif value > (limit * 0.60): return "WARNING"
        return "GOOD"

class BearingAnalyzer:
    @staticmethod
    def analyze(accel_g):
        """Cek Kondisi Bearing berdasarkan Percepatan (g)"""
        if accel_g > 2.0: return "DAMAGED"
        elif accel_g > 1.0: return "WARNING"
        return "GOOD"

class StructuralAnalyzer:
    @staticmethod
    def analyze(disp_micron, vel_mm_s, limit_vel):
        """Cek Integritas Struktur (Looseness)"""
        # Jika Displacement tinggi (>100) tapi Velocity Masih Aman -> Murni Looseness
        if disp_micron > 100:
            if vel_mm_s < limit_vel: return "LOOSENESS_ONLY"
            else: return "STRUCTURAL_DAMAGE" # Velocity ikut tinggi
        return "RIGID"

class ThermalAnalyzer:
    @staticmethod
    def analyze(temp_c):
        """Cek Temperatur"""
        if temp_c > 80: return "OVERHEAT"
        elif temp_c > 60: return "WARM"
        return "NORMAL"

class HydraulicAnalyzer:
    @staticmethod
    def analyze(suc, dis, design_head, act_flow, design_flow):
        """Cek Performa Pompa (API 610)"""
        res = []
        # Head Check
        diff_bar = dis - suc
        act_head = (diff_bar * 10.2) / 0.85
        if design_head > 0:
            ratio = (act_head / design_head) * 100
            if ratio < 75: res.append("LOW_HEAD")
            elif ratio > 110: res.append("HIGH_HEAD")
        
        # Flow Check
        if design_flow > 0 and act_flow > 0:
            ratio = (act_flow / design_flow) * 100
            if ratio < 60: res.append("LOW_FLOW")
            elif ratio > 120: res.append("HIGH_FLOW")
            
        return res

class SpectrumAnalyzer:
    @staticmethod
    def analyze(rpm, peaks):
        """Root Cause Analysis (1x, 2x, 3x RPM)"""
        if rpm == 0 or not peaks: return []
        run_hz = rpm / 60
        faults = []
        for p in peaks:
            order = p['freq'] / run_hz
            if 0.8 <= order <= 1.2: faults.append("UNBALANCE")
            elif 1.8 <= order <= 2.2: faults.append("MISALIGNMENT")
            elif 2.8 <= order <= 3.2: faults.append("LOOSENESS")
            elif order > 3.5: faults.append("BEARING_FREQ")
        return list(set(faults))
