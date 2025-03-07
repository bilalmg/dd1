import streamlit as st
from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem import Descriptors
import openai

# Use Streamlit Secrets to access the API key
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def get_openai_response(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error with OpenAI API: {e}"

st.set_page_config(page_title="Medcinx: Molecular Design", page_icon="🔬", layout="wide")

# Custom CSS (as before) ...

st.markdown(
    """
    <style>
        .title {
            animation: fadeIn 2s;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="display: flex; justify-content: left; align-items: left;">
        <h1 class="title" style="display: flex; align-items: center;">
            <span style="margin-right: 10px;">🧬</span> Medcinx
        </h1>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns([1, 2])

with col1:
    smiles = st.text_area("Enter SMILES:", "C1CCCCC1")

    mw_range = st.slider("Molecular Weight (Da)", 100, 600, (200, 400))
    logp_range = st.slider("LogP", -2.0, 5.0, (0.0, 3.0))
    hbd_range = st.slider("Hydrogen Bond Donors", 0, 5, (0, 3))
    hba_range = st.slider("Hydrogen Bond Acceptors", 0, 10, (0, 5))

    if st.button("Analyze Molecule"):
        mol = Chem.MolFromSmiles(smiles)

        if mol:
            mw = Descriptors.MolWt(mol)
            logp = Descriptors.MolLogP(mol)
            hbd = Descriptors.NumHDonors(mol)
            hba = Descriptors.NumHAcceptors(mol)

            st.write(f"**Molecular Weight:** {mw} ({'Within range' if mw_range[0] <= mw <= mw_range[1] else 'Out of range'})")
            st.write(f"**LogP:** {logp} ({'Within range' if logp_range[0] <= logp <= logp_range[1] else 'Out of range'})")
            st.write(f"**Hydrogen Bond Donors:** {hbd} ({'Within range' if hbd_range[0] <= hbd <= hbd_range[1] else 'Out of range'})")
            st.write(f"**Hydrogen Bond Acceptors:** {hba} ({'Within range' if hba_range[0] <= hba <= hba_range[1] else 'Out of range'})")

            violations = 0
            if mw > 500: violations += 1
            if logp > 5: violations += 1
            if hbd > 5: violations += 1
            if hba > 10: violations += 1
            st.write(f"**Lipinski Violations:** {violations}")

            st.session_state.violations = violations  # Store violations in session state
            st.session_state.mol = mol #Store mol in session state
            st.session_state.smiles = smiles #Store smiles in session state.

        else:
            st.error("Invalid SMILES.")

    if st.button("Show Violations") and 'violations' in st.session_state:
        violations = st.session_state.violations
        if violations > 0 and 'mol' in st.session_state:
            mol = st.session_state.mol
            mw = Descriptors.MolWt(mol)
            logp = Descriptors.MolLogP(mol)
            hbd = Descriptors.NumHDonors(mol)
            hba = Descriptors.NumHAcceptors(mol)

            violation_explanations = []
            if mw > 500:
                violation_explanations.append(f"Molecular Weight: {mw} Da (Limit: 500 Da)")
            if logp > 5:
                violation_explanations.append(f"LogP: {logp} (Limit: 5)")
            if hbd > 5:
                violation_explanations.append(f"Hydrogen Bond Donors: {hbd} (Limit: 5)")
            if hba > 10:
                violation_explanations.append(f"Hydrogen Bond Acceptors: {hba} (Limit: 10)")

            for explanation in violation_explanations:
                prompt = f"Explain why violating the Lipinski rule: '{explanation}' is bad for a drug."
                response = get_openai_response(prompt)
                st.write(f"**{explanation} Explanation:**\n{response}")
        else:
            st.write("No Lipinski violations to show.")

    if st.button("Suggestions") and 'smiles' in st.session_state:
        smiles = st.session_state.smiles
        prompt = f"How can I modify {smiles} to improve drug-likeness?"
        response = get_openai_response(prompt)
        st.write(f"**Suggestions:**\n{response}")

with col2:
    if 'smiles' in st.session_state and st.session_state.smiles:
        mol = Chem.MolFromSmiles(st.session_state.smiles)
        if mol:
            st.markdown(
                """
                <div style="display: flex; flex-direction: column; align-items: center;">
                    <h3 style="color: red; display: flex; align-items: center;">
                         Interactive Molecular Design
                    </h3>
                </div>
                """,
                unsafe_allow_html=True,
            )
            # Create a nested column for right-center alignment
            col2a, col2b, col2c = st.columns([1, 2, 1])  # Adjust ratios as needed

            with col2b: #place image in the center column
                img = Draw.MolToImage(mol, size=(400, 400))
                st.image(img)