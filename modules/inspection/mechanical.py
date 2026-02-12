import streamlit as st
import pandas as pd
from modules.analyzers import VibrationAnalyzer, BearingAnalyzer, StructuralAnalyzer, ThermalAnalyzer, HydraulicAnalyzer, SpectrumAnalyzer
from modules.decision_engine import generate_full_diagnosis

def render_mechanical_page():
    st.header("🔍 Inspection Input Form")
    st.caption("Standard: ISO 10816-3 (Average Logic)")
    st.markdown("---")

    # ==========================================
    # 1. EQUIPMENT SPECIFICATION
    # ==========================================
    st.subheader("📋 1. Equipment Specification")
    c_spec1, c_spec2 = st.columns(2)
    
    with c_spec1:
        st.info("🔌 Motor Spec")
        c1, c2 = st.columns([0.7, 0.3])
        p_val = c1.number_input("Power", value=30.0)
        p_unit = c2.selectbox("Unit", ["kW", "HP"])
        m_kw = p_val * 0.7457 if p_unit == "HP" else p_val
        
        m_rpm = st.number_input("Speed (RPM)", value=2950)
        is_flex = st.checkbox("Flexible Foundation?")
        
        limit_iso = VibrationAnalyzer.get_iso_limit(m_kw, is_flex)
        st.write(f"🛡️ **ISO Trip Limit:** `{limit_iso} mm/s`")

    with c_spec2:
        st.success("💧 Pump Spec")
        p_tag = st.text_input("Tag No", "P-101A")
        
        c3, c4 = st.columns([0.7, 0.3])
        h_val = c3.number_input("Design Head", value=50.0)
        h_unit = c4.selectbox("Unit H", ["m", "ft"])
        d_head = h_val * 0.3048 if h_unit == "ft" else h_val
        
        c5, c6 = st.columns([0.7, 0.3])
        q_val = c5.number_input("Design Flow", value=100.0)
        q_unit = c6.selectbox("Unit Q", ["m3/h", "GPM"])
        d_flow = q_val * 0.2271 if q_unit == "GPM" else q_val

    st.markdown("---")

    # ==========================================
    # 2. FIELD DATA ENTRY
    # ==========================================
    st.subheader("📝 2. Field Data Entry")

    def input_vibration_point(label, prefix):
        with st.expander(f"📍 {label}", expanded=True):
            col_vel, col_cond = st.columns([0.6, 0.4])
            with col_vel:
                st.markdown("**Velocity (mm/s)**")
                c_h, c_v, c_a = st.columns(3)
                vh = c_h.number_input(f"Horiz", key=f"{prefix}_vh", step=0.01)
                vv = c_v.number_input(f"Vert", key=f"{prefix}_vv", step=0.01)
                va = c_a.number_input(f"Axial", key=f"{prefix}_va", step=0.01)
            with col_cond:
                st.markdown("**Condition**")
                acc = st.number_input(f"Acc (g)", key=f"{prefix}_acc", step=0.01)
                temp = st.number_input(f"Temp (°C)", key=f"{prefix}_temp", value=40.0)
                disp = st.number_input(f"Disp (μm)", key=f"{prefix}_disp", value=0.0)
        return {"h": vh, "v": vv, "a": va, "acc": acc, "temp": temp, "disp": disp}

    col_motor, col_pump = st.columns(2)
    with col_motor:
        st.caption("DRIVER SIDE")
        data_m_de = input_vibration_point("Motor DE", "m_de")
        data_m_nde = input_vibration_point("Motor NDE", "m_nde")
    with col_pump:
        st.caption("DRIVEN SIDE")
        data_p_de = input_vibration_point("Pump DE", "p_de")
        data_p_nde = input_vibration_point("Pump NDE", "p_nde")

    st.markdown("---")

    # ==========================================
    # 3. PROCESS & SPECTRUM
    # ==========================================
    col_proc, col_spec = st.columns(2)
    with col_proc:
        st.subheader("🚰 Process Data")
        suc = st.number_input("Suction (BarG)", value=0.5)
        dis = st.number_input("Discharge (BarG)", value=4.0)
        flow_in = st.number_input("Actual Flow Reading", value=95.0)
        act_flow = flow_in * 0.2271 if q_unit == "GPM" else flow_in

    with col_spec:
        st.subheader("📈 Spectrum Peaks")
        peaks = []
        for i in range(1, 4):
            c1, c2 = st.columns(2)
            f = c1.number_input(f"Freq {i}", key=f"f{i}")
            a = c2.number_input(f"Amp {i}", key=f"a{i}")
            if f > 0: peaks.append({'freq': f, 'amp': a})

    # ==========================================
    # 4. REPORT GENERATION
    # ==========================================
    if st.button("🚀 GENERATE REPORT", type="primary", use_container_width=True):
        st.divider()
        st.title(f"📊 Reliability Report: {p_tag}")

        # --- A. LOGIKA RATA-RATA (AVERAGE CALCULATION) ---
        def make_row(component, direction, val_de, val_nde):
            avr = (val_de + val_nde) / 2
            remark = VibrationAnalyzer.check_severity(avr, limit_iso)
            return [component, direction, val_de, val_nde, avr, limit_iso, remark]

        table_rows = []
        
        # 1. Driver Rows (H, V, A)
        table_rows.append(make_row("Driver", "H", data_m_de['h'], data_m_nde['h']))
        table_rows.append(make_row("Driver", "V", data_m_de['v'], data_m_nde['v']))
        table_rows.append(make_row("Driver", "A", data_m_de['a'], data_m_nde['a']))
        
        # Row Temperature (Gunakan "-" untuk Limit agar sesuai visual, tapi nanti kita handle formatter-nya)
        avg_temp_m = (data_m_de['temp'] + data_m_nde['temp']) / 2
        table_rows.append(["Driver", "T (°C)", data_m_de['temp'], data_m_nde['temp'], avg_temp_m, "-", "-"])

        # 2. Driven Rows (H, V, A)
        table_rows.append(make_row("Driven", "H", data_p_de['h'], data_p_nde['h']))
        table_rows.append(make_row("Driven", "V", data_p_de['v'], data_p_nde['v']))
        table_rows.append(make_row("Driven", "A", data_p_de['a'], data_p_nde['a']))
        
        # Row Temperature
        avg_temp_p = (data_p_de['temp'] + data_p_nde['temp']) / 2
        table_rows.append(["Driven", "T (°C)", data_p_de['temp'], data_p_nde['temp'], avg_temp_p, "-", "-"])

        # --- B. TAMPILKAN TABEL (DENGAN SAFE FORMATTER) ---
        st.subheader("📋 Vibration Data Sheet")
        df_report = pd.DataFrame(table_rows, columns=["Titik", "Dir", "DE", "NDE", "Avr", "Limit", "Remark"])
        
        # [SOLUSI ERROR] Fungsi formatter yang aman:
        # Jika angka --> Format 2 desimal
        # Jika string ("-") --> Biarkan apa adanya
        def safe_fmt(x):
            return "{:.2f}".format(x) if isinstance(x, (int, float)) else str(x)

        # Terapkan styling dengan formatter aman
        st.dataframe(
            df_report.style.format({
                "DE": safe_fmt, 
                "NDE": safe_fmt, 
                "Avr": safe_fmt, 
                "Limit": safe_fmt
            }), 
            use_container_width=True
        )

        # --- C. DATA UNTUK ALGORITMA DIAGNOSA ---
        # Filter hanya baris H/V/A untuk mencari max vibration (abaikan row T)
        vel_values = [r[4] for r in table_rows if r[1] in ["H", "V", "A"]]
        max_avr_vel = max(vel_values) if vel_values else 0.0
        
        max_acc = max(data_m_de['acc'], data_m_nde['acc'], data_p_de['acc'], data_p_nde['acc'])
        max_disp = max(data_m_de['disp'], data_m_nde['disp'], data_p_de['disp'], data_p_nde['disp'])
        max_temp = max(data_m_de['temp'], data_m_nde['temp'], data_p_de['temp'], data_p_nde['temp'])

        res_iso = VibrationAnalyzer.check_severity(max_avr_vel, limit_iso)
        
        # Mapping ulang status text panjang ke status pendek untuk decision engine
        if "damage" in res_iso: iso_short = "DANGER"
        elif "Short-term" in res_iso: iso_short = "WARNING"
        else: iso_short = "GOOD"

        res_bearing = BearingAnalyzer.analyze(max_acc)
        res_struct = StructuralAnalyzer.analyze(max_disp, max_avr_vel, limit_iso)
        res_therm = ThermalAnalyzer.analyze(max_temp)
        res_hyd = HydraulicAnalyzer.analyze(suc, dis, d_head, act_flow, d_flow)
        res_spec = SpectrumAnalyzer.analyze(m_rpm, peaks)

        # --- D. REKOMENDASI AI ---
        context = {
            'iso_status': iso_short,
            'bearing_status': res_bearing,
            'struct_status': res_struct,
            'therm_status': res_therm,
            'hyd_issues': res_hyd,
            'spec_faults': res_spec
        }
        
        final_recs = generate_full_diagnosis(context)
        
        st.subheader("💡 Expert Diagnosis & Recommendations")
        for rec in final_recs:
            if "SEHAT" in rec: st.success(rec)
            else: st.warning(rec)
