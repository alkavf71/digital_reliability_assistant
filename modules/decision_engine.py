# modules/decision_engine.py

def generate_full_diagnosis(data_context):
    """
    Algoritma Pengambil Keputusan (The Brain).
    Menerima dictionary hasil analisa, mengeluarkan list kalimat rekomendasi.
    """
    recs = []
    
    # Ambil Data Konteks
    iso_status = data_context.get('iso_status')
    bearing_status = data_context.get('bearing_status')
    struct_status = data_context.get('struct_status')
    therm_status = data_context.get('therm_status')
    hyd_issues = data_context.get('hyd_issues', [])
    spec_faults = data_context.get('spec_faults', [])
    
    # --- LOGIKA SILANG (CROSS-REFERENCE) ---

    # 1. Logic Bearing & Thermal
    if bearing_status == "DAMAGED":
        recs.append("⚙️ **BEARING CRITICAL:** Accel > 2.0g. Kerusakan fisik bearing terdeteksi. Stop & Ganti Bearing.")
    elif therm_status == "OVERHEAT" and bearing_status == "GOOD":
        recs.append("🛢️ **LUBRICATION:** Suhu Tinggi (>60°C) tapi Vibrasi Rendah. Indikasi Grease Kering. Lakukan Regreasing.")
    
    # 2. Logic Structural
    if struct_status == "LOOSENESS_ONLY":
        recs.append("🏗️ **FOUNDATION ISSUE:** Vibrasi Displacement tinggi tapi Velocity normal. Cek kekencangan Baut Angkur/Frame.")
    elif struct_status == "STRUCTURAL_DAMAGE":
        recs.append("⚠️ **STRUCTURAL DANGER:** Getaran mesin sudah mengguncang struktur pondasi. Segera perbaiki sumber getaran.")

    # 3. Logic Root Cause (Spectrum)
    if "UNBALANCE" in spec_faults:
        recs.append("⚖️ **UNBALANCE:** Dominan 1x RPM. Lakukan Cleaning Impeller & In-situ Balancing.")
    if "MISALIGNMENT" in spec_faults:
        recs.append("📏 **MISALIGNMENT:** Dominan 2x RPM. Cek Softfoot & Lakukan Laser Alignment poros.")
        
    # 4. Logic Hydraulic (Process)
    for issue in hyd_issues:
        if issue == "LOW_FLOW":
            recs.append("🌊 **LOW FLOW:** Operasi di bawah 60% BEP. Buka valve discharge perlahan (Cegah Recirculation).")
        if issue == "HIGH_FLOW":
            recs.append("🛑 **HIGH FLOW:** Operasi run-out (>120% BEP). Throttling valve discharge (Cegah Kavitasi).")
        if issue == "LOW_HEAD":
            recs.append("🔧 **PUMP WEAR:** Head aktual turun drastis. Cek clearance Wear Ring & Impeller.")

    # 5. General Safety Logic
    if iso_status == "DANGER" and not recs:
        recs.append("🔴 **HIGH VIBRATION:** Vibrasi melebihi batas Trip ISO. Periksa kondisi baut & alignment secara menyeluruh.")

    if not recs:
        return ["✅ Unit dalam kondisi SEHAT (Normal Operation)."]
    
    return recs
