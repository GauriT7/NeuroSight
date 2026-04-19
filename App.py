import streamlit as st

st.set_page_config(page_title="NeuroSight", page_icon="🧠", layout="centered")

st.markdown("""
<div style='background:#1a3a5c;padding:1.2rem 1.5rem;border-radius:12px;color:white;margin-bottom:1.5rem'>
<h2 style='margin:0;font-size:22px'>🧠 NeuroSight</h2>
<p style='margin:4px 0 0;opacity:0.75;font-size:13px'>Portable neuro-ocular dementia risk screening</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["Patient Info", "Oculomotor Tasks", "Retinal Input", "Results"])

with tab1:
    st.subheader("Patient Information")
    age = st.slider("Age", 40, 90, 62)
    eye_condition = st.selectbox("Known eye conditions?",
        ["None", "Glaucoma (+5)", "Macular degeneration (+3)", "Diabetic retinopathy (+2)"])
    eye_penalty = {"None":0,"Glaucoma (+5)":5,"Macular degeneration (+3)":3,"Diabetic retinopathy (+2)":2}[eye_condition]

with tab2:
    st.subheader("Oculomotor Task Parameters")
    st.caption("These values are captured from the IR eye-tracking camera during the 3–5 min protocol")
    saccade_latency = st.slider("Saccade latency (ms)", 150, 400, 220)
    st.caption("Normal: 150–200ms | Higher = slower frontal response")
    anti_saccade_err = st.slider("Anti-saccade error rate (%)", 0, 60, 18)
    st.caption("Normal: <15% | Higher = impaired inhibitory control")
    fixation_instability = st.slider("Fixation instability (°)", 0.5, 5.0, 1.8)
    st.caption("Normal: <1.5° | Higher = unstable fixation")
    pursuit_gain = st.slider("Smooth pursuit gain", 0.40, 1.00, 0.82)
    st.caption("Normal: >0.85 | Lower = degraded tracking ability")

with tab3:
    st.subheader("Retinal Assessment (optional)")
    st.caption("Integrated when retinal imaging is available as part of routine eye care")
    vascular_score = st.slider("Vascular caliber anomaly score", 0, 10, 3)
    texture_score = st.slider("Texture anomaly index", 0, 10, 2)
    has_retinal = st.checkbox("Retinal image available", value=True)

with tab4:
    st.subheader("Composite NeuroOcular Risk Score")

    age_factor = 1.15 if age > 70 else 1.07 if age > 60 else 1.0

    sl_score  = min(100, max(0, ((saccade_latency - 150) / 250) * 100))
    as_score  = min(100, (anti_saccade_err / 60) * 100)
    fi_score  = min(100, max(0, ((fixation_instability - 0.5) / 4.5) * 100))
    sp_score  = min(100, max(0, ((1.0 - pursuit_gain) / 0.6) * 100))
    ret_score = ((vascular_score + texture_score) / 20) * 100

    ocular_composite = (sl_score * 0.35) + (as_score * 0.30) + (fi_score * 0.20) + (sp_score * 0.15)
    final_score = (ocular_composite * 0.75 + ret_score * 0.25) if has_retinal else ocular_composite
    final_score = min(100, round(final_score * age_factor + eye_penalty))

    if final_score < 34:
        category, color = "Low Risk", "green"
    elif final_score < 67:
        category, color = "Intermediate Risk", "orange"
    else:
        category, color = "High Risk", "red"

    st.metric("Risk Score", f"{final_score}/100", delta=category)
    st.progress(final_score / 100)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Saccade latency", f"{round(sl_score)}/100")
    col2.metric("Anti-saccade", f"{round(as_score)}/100")
    col3.metric("Fixation", f"{round(fi_score)}/100")
    col4.metric("Pursuit gain", f"{round(sp_score)}/100")

    st.divider()

    if final_score >= 67:
        st.error("High risk detected — neurological referral recommended within 4 weeks")
        st.subheader("Brief Cognitive Questionnaire")
        q1 = st.radio("Do you frequently forget recent conversations?", ["No","Sometimes","Yes"])
        q2 = st.radio("Do you have difficulty finding words while speaking?", ["No","Sometimes","Yes"])
        q3 = st.radio("Have you noticed changes in your ability to plan or organise?", ["No","Sometimes","Yes"])
        cog_score = sum([["No","Sometimes","Yes"].index(q) for q in [q1,q2,q3]])
        if cog_score >= 3:
            st.error(f"Cognitive questionnaire score: {cog_score}/6 — supports referral urgency")
        else:
            st.warning(f"Cognitive questionnaire score: {cog_score}/6")
    elif final_score >= 34:
        st.warning("Intermediate risk — follow-up screening in 6 months recommended")
    else:
        st.success("Low risk — routine screening in 12 months")

    st.caption("NeuroSight is a screening and triage tool only. Not a diagnostic device.")
