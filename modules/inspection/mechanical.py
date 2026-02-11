import streamlit as st
import pandas as pd
# Import modul menggunakan absolute path dari root
from modules.analyzers import VibrationAnalyzer, BearingAnalyzer, StructuralAnalyzer, ThermalAnalyzer, HydraulicAnalyzer, SpectrumAnalyzer
from modules.decision_engine import generate_full_diagnosis

def render_mechanical_page():
    # Isi fungsi tetap sama seperti sebelumnya
    st.header("🔍 Integrated Diagnostic Dashboard")
    # ... (lanjutkan sisa kode UI Anda)
    st.markdown("---")

    # --- 1. INPUT SPEC ---
    st.subheader("📋 1. Equipment Specification")
    c1, c2 = st.columns(2)
    with c1:
        p_kw = st.number_input("Motor Power (kW)", value=30.0)
        rpm = st.number_input("Speed (RPM)", value=2950)
        is_flex = st.checkbox("Flexible Foundation?")
        # [CALL MODULE] ISO Limit Calculator
        limit_iso = VibrationAnalyzer.get_iso_limit(p_kw, is_flex)
        st.caption(f"Calculated ISO Limit: {limit_iso} mm/s")
    
    with c2:
        d_head = st.number_input("Design Head (m)", value=50.0)
        d_flow = st.number_input("Design Flow (m3/h)", value=100.0)

    st.markdown("---")

    # --- 2. INPUT FIELD DATA ---
    st.subheader("📝 2. Field Measurement")
    # (Saya sederhanakan inputnya agar fokus ke logika modul)
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        st.info("Vibration Data")
        vel_max = st.number_input("Max Velocity (mm/s)", value=0.0)
        acc_max = st.number_input("Max Accel (g)", value=0.0)
        disp_max = st.number_input("Max Disp (μm)", value=0.0)
        temp_max = st.number_input("Max Temp (°C)", value=40.0)
    
    with col_in2:
        st.success("Process Data")
        suc = st.number_input("Suction (Bar)", value=0.5)
        dis = st.number_input("Discharge (Bar)", value=4.0)
        flow = st.number_input("Act Flow (m3/h)", value=95.0)
        
        st.caption("Spectrum Peaks")
        peaks = []
        if st.checkbox("Add Peak Data"):
            f = st.number_input("Freq (Hz)")
            if f > 0: peaks.append({'freq': f, 'amp': 1.0})

    # --- 3. EKSEKUSI DIAGNOSA ---
    if st.button("🚀 RUN DIAGNOSIS MODULES", type="primary"):
        st.divider()
        st.subheader("📊 Laporan Hasil Diagnosa (Pertamina Format)")

        # [STEP A] PANGGIL MODUL ANALYZER SATU PER SATU
        res_iso = VibrationAnalyzer.check_severity(vel_max, limit_iso)
        res_bearing = BearingAnalyzer.analyze(acc_max)
        res_struct = StructuralAnalyzer.analyze(disp_max, vel_max, limit_iso)
        res_therm = ThermalAnalyzer.analyze(temp_max)
        res_hyd = HydraulicAnalyzer.analyze(suc, dis, d_head, flow, d_flow)
        res_spec = SpectrumAnalyzer.analyze(rpm, peaks)

        # [STEP B] SIAPKAN KONTEKS DATA UNTUK "THE BRAIN"
        context = {
            'iso_status': res_iso,
            'bearing_status': res_bearing,
            'struct_status': res_struct,
            'therm_status': res_therm,
            'hyd_issues': res_hyd,
            'spec_faults': res_spec
        }

        # [STEP C] PANGGIL DECISION ENGINE (DATABASE REKOMENDASI)
        final_recommendations = generate_full_diagnosis(context)

        # [STEP D] TAMPILKAN OUTPUT
        
        # 1. Scorecard
        cc1, cc2, cc3, cc4 = st.columns(4)
        cc1.metric("ISO Severity", res_iso, "Limit: " + str(limit_iso))
        cc2.metric("Bearing Cond", res_bearing, f"{acc_max} g")
        cc3.metric("Structure", res_struct, f"{disp_max} μm")
        cc4.metric("Hydraulic", "ISSUE" if res_hyd else "OK")

        # 2. Tabel Rekomendasi
        st.subheader("💡 Rekomendasi & Tindak Lanjut")
        for rec in final_recommendations:
            if "SEHAT" in rec: st.success(rec)
            else: st.warning(rec)
