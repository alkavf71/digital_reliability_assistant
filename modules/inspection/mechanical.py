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
    # 2. FIELD DATA ENTRY (QUADRANT LAYOUT)
    # ==========================================
    st.subheader("📝 2. Field Data Entry")

    # Kita bagi layar jadi 2 kolom besar (Kiri & Kanan)
    col_left, col_right = st.columns(2)

    # --- KOTAK A: VELOCITY ISO (DI KIRI ATAS) ---
    with col_left:
        with st.container(border=True):
            st.markdown("### 🅰️ Velocity ISO (mm/s)")
            st.caption("Input Horizontal (H), Vertical (V), Axial (A)")
            
            # --- MOTOR SECTION ---
            st.markdown("##### ⚡ Driver (Motor)")
            cm1, cm2 = st.columns(2)
            with cm1:
                st.caption("Motor DE")
                m_de_h = st.number_input("H", key="m_de_h", step=0.01)
                m_de_v = st.number_input("V", key="m_de_v", step=0.01)
                m_de_a = st.number_input("A", key="m_de_a", step=0.01)
            with cm2:
                st.caption("Motor NDE")
                m_nde_h = st.number_input("H", key="m_nde_h", step=0.01)
                m_nde_v = st.number_input("V", key="m_nde_v", step=0.01)
                m_nde_a = st.number_input("A", key="m_nde_a", step=0.01)
            
            st.markdown("---")
            
            # --- PUMP SECTION ---
            st.markdown("##### 💧 Driven (Pump)")
            cp1, cp2 = st.columns(2)
            with cp1:
                st.caption("Pump DE")
                p_de_h = st.number_input("H", key="p_de_h", step=0.01)
                p_de_v = st.number_input("V", key="p_de_v", step=0.01)
                p_de_a = st.number_input("A", key="p_de_a", step=0.01)
            with cp2:
                st.caption("Pump NDE")
                p_nde_h = st.number_input("H", key="p_nde_h", step=0.01)
                p_nde_v = st.number_input("V", key="p_nde_v", step=0.01)
                p_nde_a = st.number_input("A", key="p_nde_a", step=0.01)

    # --- KOTAK B: BEARING & STRUCTURE (DI KANAN ATAS) ---
    with col_right:
        with st.container(border=True):
            st.markdown("### 🅱️ Condition Data")
            st.caption("Bearing (Accel g) & Structure (Disp μm)")
            
            # Grid Layout untuk Accel & Disp
            c_b1, c_b2 = st.columns(2)
            
            with c_b1:
                st.markdown("**Accel (g)**")
                m_de_acc = st.number_input("M-DE", key="m_de_acc", step=0.01)
                m_nde_acc = st.number_input("M-NDE", key="m_nde_acc", step=0.01)
                p_de_acc = st.number_input("P-DE", key="p_de_acc", step=0.01)
                p_nde_acc = st.number_input("P-NDE", key="p_nde_acc", step=0.01)
                
            with c_b2:
                st.markdown("**Disp (μm)**")
                m_de_disp = st.number_input("M-DE", key="m_de_disp", step=1.0)
                m_nde_disp = st.number_input("M-NDE", key="m_nde_disp", step=1.0)
                p_de_disp = st.number_input("P-DE", key="p_de_disp", step=1.0)
                p_nde_disp = st.number_input("P-NDE", key="p_nde_disp", step=1.0)

    # --- KOTAK C: THERMAL & SPEED (DI KIRI BAWAH) ---
    with col_left:
        with st.container(border=True):
            st.markdown("### ©️ Thermal & Speed")
            
            c_t1, c_t2 = st.columns(2)
            with c_t1:
                st.markdown("**Temp (°C)**")
                m_de_temp = st.number_input("M-DE", key="m_de_temp", value=40.0)
                m_nde_temp = st.number_input("M-NDE", key="m_nde_temp", value=40.0)
                p_de_temp = st.number_input("P-DE", key="p_de_temp", value=40.0)
                p_nde_temp = st.number_input("P-NDE", key="p_nde_temp", value=40.0)
            
            with c_t2:
                st.markdown("**Actual RPM**")
                act_rpm = st.number_input("Strobo Reading", value=int(m_rpm), help="Input RPM aktual lapangan untuk diagnosa spektrum")

    # --- KOTAK D: PEAK PICKING (DI KANAN BAWAH) ---
    with col_right:
        with st.container(border=True):
            st.markdown("### ⓓ Peak Picking (Spectrum)")
            st.caption("Input 3 Puncak Dominan Tertinggi")
            
            peaks = []
            for i in range(1, 4):
                cpk1, cpk2 = st.columns([0.6, 0.4])
                f = cpk1.number_input(f"Freq {i} (Hz)", key=f"f{i}")
                a = cpk2.number_input(f"Amp {i}", key=f"a{i}")
                if f > 0: peaks.append({'freq': f, 'amp': a})

    # --- RE-MAPPING VARIABLE (PENTING AGAR TIDAK MERUBAH LOGIKA LAPORAN) ---
    # Kita menyatukan variabel yang terpencar di kotak-kotak tadi menjadi dictionary
    # agar kode di Section 4 (Report) bisa tetap membaca data_m_de['h'], dst.
    
    data_m_de = {"h": m_de_h, "v": m_de_v, "a": m_de_a, "acc": m_de_acc, "disp": m_de_disp, "temp": m_de_temp}
    data_m_nde = {"h": m_nde_h, "v": m_nde_v, "a": m_nde_a, "acc": m_nde_acc, "disp": m_nde_disp, "temp": m_nde_temp}
    data_p_de = {"h": p_de_h, "v": p_de_v, "a": p_de_a, "acc": p_de_acc, "disp": p_de_disp, "temp": p_de_temp}
    data_p_nde = {"h": p_nde_h, "v": p_nde_v, "a": p_nde_a, "acc": p_nde_acc, "disp": p_nde_disp, "temp": p_nde_temp}

    st.markdown("---")

    # ==========================================
    # 3. PROCESS DATA (HYDRAULIC)
    # ==========================================
    # Bagian ini tetap terpisah karena khusus pompa
    with st.expander("🚰 Tambahan: Process Data (Hydraulic)", expanded=True):
        col_proc1, col_proc2, col_proc3 = st.columns(3)
        suc = col_proc1.number_input("Suction (BarG)", value=0.5)
        dis = col_proc2.number_input("Discharge (BarG)", value=4.0)
        flow_in = col_proc3.number_input("Actual Flow Reading", value=95.0)
        act_flow = flow_in * 0.2271 if q_unit == "GPM" else flow_in

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
        
        # Row Temperature (Gunakan "-" untuk Limit agar sesuai visual)
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
        
        # [SOLUSI ERROR] Fungsi formatter yang aman
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
