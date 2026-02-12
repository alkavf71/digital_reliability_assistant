import streamlit as st
import pandas as pd
from modules.analyzers import VibrationAnalyzer, BearingAnalyzer, StructuralAnalyzer, ThermalAnalyzer, HydraulicAnalyzer, SpectrumAnalyzer
from modules.decision_engine import generate_full_diagnosis

def render_mechanical_page():
    st.header("🔍 Inspection Input Form")
    st.caption("Standard: ISO 10816-3 (Velocity), API 610 (Hydraulic), & Bearing Health")
    st.markdown("---")

    # ==========================================
    # 1. EQUIPMENT SPECIFICATION (Tetap di atas)
    # ==========================================
    with st.expander("📋 1. Equipment Specification (Klik untuk Edit)", expanded=False):
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
            h_val = st.number_input("Design Head (m)", value=50.0)
            c5, c6 = st.columns([0.7, 0.3])
            q_val = c5.number_input("Design Flow", value=100.0)
            q_unit = c6.selectbox("Unit Q", ["m3/h", "GPM"])
            d_flow = q_val * 0.2271 if q_unit == "GPM" else q_val

    st.markdown("---")

    # ==========================================
    # 2. FIELD DATA ENTRY (LAYOUT 4 KOTAK)
    # ==========================================
    st.subheader("📝 2. Field Data Entry")
    
    # Kita gunakan Tabs agar halaman tidak terlalu panjang ke bawah
    tab_driver, tab_driven = st.tabs(["⚡ DRIVER SIDE (MOTOR)", "💧 DRIVEN SIDE (PUMP)"])

    # --- FUNGSI PEMBUAT KOTAK INPUT (Reusable) ---
    def render_quadrant_input(prefix_label):
        # Baris 1: Kotak A & B
        c_row1_a, c_row1_b = st.columns(2)
        
        # --- KOTAK A: VIBRATION ISO (Velocity) ---
        with c_row1_a:
            with st.container(border=True):
                st.markdown("### 🅰️ Vibration ISO (mm/s)")
                st.caption("Velocity RMS - H/V/A")
                
                c_de, c_nde = st.columns(2)
                with c_de:
                    st.markdown("**DE Point**")
                    vh_de = st.number_input("H", key=f"{prefix_label}_vh_de", step=0.01)
                    vv_de = st.number_input("V", key=f"{prefix_label}_vv_de", step=0.01)
                    va_de = st.number_input("A", key=f"{prefix_label}_va_de", step=0.01)
                with c_nde:
                    st.markdown("**NDE Point**")
                    vh_nde = st.number_input("H", key=f"{prefix_label}_vh_nde", step=0.01)
                    vv_nde = st.number_input("V", key=f"{prefix_label}_vv_nde", step=0.01)
                    va_nde = st.number_input("A", key=f"{prefix_label}_va_nde", step=0.01)

        # --- KOTAK B: CONDITION MONITORING (Accel & Disp) ---
        with c_row1_b:
            with st.container(border=True):
                st.markdown("### 🅱️ Condition (Bearing/Struktur)")
                st.caption("Accel (g) & Disp (μm)")
                
                c_de, c_nde = st.columns(2)
                with c_de:
                    st.markdown("**DE Point**")
                    acc_de = st.number_input("Acc (g)", key=f"{prefix_label}_acc_de", step=0.01)
                    disp_de = st.number_input("Disp (μm)", key=f"{prefix_label}_disp_de", step=1.0)
                with c_nde:
                    st.markdown("**NDE Point**")
                    acc_nde = st.number_input("Acc (g)", key=f"{prefix_label}_acc_nde", step=0.01)
                    disp_nde = st.number_input("Disp (μm)", key=f"{prefix_label}_disp_nde", step=1.0)

        # Baris 2: Kotak C & D
        c_row2_c, c_row2_d = st.columns(2)

        # --- KOTAK C: THERMAL & SPEED ---
        with c_row2_c:
            with st.container(border=True):
                st.markdown("### ©️ Thermal & Speed")
                st.caption("Temperature (°C)")
                
                c_t1, c_t2 = st.columns(2)
                t_de = c_t1.number_input("Temp DE (°C)", key=f"{prefix_label}_t_de", value=40.0)
                t_nde = c_t2.number_input("Temp NDE (°C)", key=f"{prefix_label}_t_nde", value=40.0)
                
                # Input RPM Aktual (Untuk memastikan motor tidak slip)
                act_rpm = st.number_input("Actual RPM (Strobo)", key=f"{prefix_label}_act_rpm", value=int(m_rpm))

        # --- KOTAK D: PEAK PICKING (SPECTRUM) ---
        with c_row2_d:
            with st.container(border=True):
                st.markdown("### ⓓ Peak Picking (Spectrum)")
                st.caption("Dominant Frequency (Untuk Diagnosa)")
                
                peaks = []
                # Hanya input 3 puncak tertinggi
                for i in range(1, 4):
                    cc1, cc2 = st.columns([0.6, 0.4])
                    f = cc1.number_input(f"Freq {i} (Hz)", key=f"{prefix_label}_f{i}", step=1.0)
                    a = cc2.number_input(f"Amp {i}", key=f"{prefix_label}_a{i}", step=0.1)
                    if f > 0: peaks.append({'freq': f, 'amp': a})
        
        # Return semua data dalam dictionary rapi
        return {
            "vh_de": vh_de, "vv_de": vv_de, "va_de": va_de,
            "vh_nde": vh_nde, "vv_nde": vv_nde, "va_nde": va_nde,
            "acc_de": acc_de, "acc_nde": acc_nde,
            "disp_de": disp_de, "disp_nde": disp_nde,
            "t_de": t_de, "t_nde": t_nde,
            "rpm": act_rpm, "peaks": peaks
        }

    # --- RENDER TAB DRIVER ---
    with tab_driver:
        st.info("Input Data Sisi Motor (Driver)")
        # Panggil fungsi 4 kotak
        data_motor = render_quadrant_input("m")

    # --- RENDER TAB DRIVEN ---
    with tab_driven:
        st.success("Input Data Sisi Pompa (Driven)")
        # Panggil fungsi 4 kotak
        data_pump = render_quadrant_input("p")
        
        # Tambahan Khusus Pompa: Hydraulic Data
        with st.expander("🌊 Tambahan: Process Data (Hydraulic)", expanded=True):
            cp1, cp2, cp3 = st.columns(3)
            suc = cp1.number_input("Suction (BarG)", value=0.5)
            dis = cp2.number_input("Discharge (BarG)", value=4.0)
            flow_in = cp3.number_input("Act. Flow", value=95.0)
            act_flow = flow_in * 0.2271 if q_unit == "GPM" else flow_in

    st.markdown("---")

    # ==========================================
    # 3. REPORT GENERATION
    # ==========================================
    if st.button("🚀 GENERATE REPORT", type="primary", use_container_width=True):
        st.divider()
        st.title(f"📊 Reliability Report: {p_tag}")

        # --- A. PEMROSESAN DATA (MAPPING) ---
        # Helper untuk format tabel (Safe Formatter)
        def safe_fmt(x): return "{:.2f}".format(x) if isinstance(x, (int, float)) else str(x)
        
        # Helper Kalkulasi Baris Tabel
        def make_row(comp, point, dir_label, val_de, val_nde):
            avr = (val_de + val_nde) / 2
            remark = VibrationAnalyzer.check_severity(avr, limit_iso)
            return [comp, dir_label, val_de, val_nde, avr, limit_iso, remark]

        # 1. Menyiapkan Data Tabel Laporan
        table_rows = []
        
        # Motor Rows
        table_rows.append(make_row("Driver", "H", "H", data_motor['vh_de'], data_motor['vh_nde']))
        table_rows.append(make_row("Driver", "V", "V", data_motor['vv_de'], data_motor['vv_nde']))
        table_rows.append(make_row("Driver", "A", "A", data_motor['va_de'], data_motor['va_nde']))
        # Motor Temp
        avg_tm = (data_motor['t_de'] + data_motor['t_nde']) / 2
        table_rows.append(["Driver", "Temp", "T (°C)", data_motor['t_de'], data_motor['t_nde'], avg_tm, "-", "-"])

        # Pump Rows
        table_rows.append(make_row("Driven", "H", "H", data_pump['vh_de'], data_pump['vh_nde']))
        table_rows.append(make_row("Driven", "V", "V", data_pump['vv_de'], data_pump['vv_nde']))
        table_rows.append(make_row("Driven", "A", "A", data_pump['va_de'], data_pump['va_nde']))
        # Pump Temp
        avg_tp = (data_pump['t_de'] + data_pump['t_nde']) / 2
        table_rows.append(["Driven", "Temp", "T (°C)", data_pump['t_de'], data_pump['t_nde'], avg_tp, "-", "-"])

        # --- B. TAMPILKAN TABEL ---
        st.subheader("📋 Vibration Data Sheet")
        df_rep = pd.DataFrame(table_rows, columns=["Comp", "Type", "Dir", "DE", "NDE", "Avr", "Limit", "Remark"])
        
        # Tampilkan kolom yang relevan saja agar rapi
        st.dataframe(
            df_rep[["Comp", "Dir", "DE", "NDE", "Avr", "Limit", "Remark"]].style.format({
                "DE": safe_fmt, "NDE": safe_fmt, "Avr": safe_fmt, "Limit": safe_fmt
            }),
            use_container_width=True
        )

        # --- C. ANALISA OTOMATIS (THE BRAIN) ---
        # 1. Cari Max Velocity (untuk ISO Status)
        vels = [r[4] for r in table_rows if r[2] in ["H", "V", "A"]] # Ambil kolom Avr
        max_vel = max(vels) if vels else 0.0
        
        # 2. Cari Max Parameter Lain
        max_acc = max(data_motor['acc_de'], data_motor['acc_nde'], data_pump['acc_de'], data_pump['acc_nde'])
        max_disp = max(data_motor['disp_de'], data_motor['disp_nde'], data_pump['disp_de'], data_pump['disp_nde'])
        max_temp = max(data_motor['t_de'], data_motor['t_nde'], data_pump['t_de'], data_pump['t_nde'])

        # 3. Panggil Modules
        res_iso_long = VibrationAnalyzer.check_severity(max_vel, limit_iso)
        # Mapping ke short status
        iso_short = "DANGER" if "damage" in res_iso_long else ("WARNING" if "Short-term" in res_iso_long else "GOOD")

        res_bearing = BearingAnalyzer.analyze(max_acc)
        res_struct = StructuralAnalyzer.analyze(max_disp, max_vel, limit_iso)
        res_therm = ThermalAnalyzer.analyze(max_temp)
        
        # Hydraulic (Hanya ada di Pump)
        # Asumsi Design Head ada di variabel h_val (user input di atas)
        res_hyd = HydraulicAnalyzer.analyze(suc, dis, h_val, act_flow, d_flow)
        
        # Spectrum (Gabungkan peak motor dan pompa)
        all_peaks = data_motor['peaks'] + data_pump['peaks']
        res_spec = SpectrumAnalyzer.analyze(m_rpm, all_peaks)

        # --- D. REKOMENDASI ---
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
        
        # Tampilkan status cepat dengan badge
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("ISO Status", iso_short, f"Max {max_vel:.2f} mm/s")
        c2.metric("Bearing", res_bearing, f"Max {max_acc:.2f} g")
        c3.metric("Hydraulic", "ISSUE" if res_hyd else "OK")
        c4.metric("Structure", res_struct)
        
        st.write("") # Spacer
        for rec in final_recs:
            if "SEHAT" in rec: st.success(rec)
            else: st.warning(rec)
