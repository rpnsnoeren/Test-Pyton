import streamlit as st
import pyperclip
import openai
import json
from pathlib import Path

# OpenAI configuratie
if 'OPENAI_API_KEY' not in st.secrets:
    st.error('Je moet eerst je OpenAI API key configureren!')
    st.stop()

openai.api_key = st.secrets['OPENAI_API_KEY']

def genereer_prompt(doel, context, stijl):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Je bent een expert in het schrijven van effectieve prompts."
                },
                {
                    "role": "user",
                    "content": f"Genereer een prompt voor het volgende doel: {doel}. \
                               Context: {context}. \
                               Gewenste stijl: {stijl}"
                }
            ]
        )
        return response.choices[0].message['content']
    except Exception as e:
        return f"Er is een fout opgetreden: {str(e)}"

def save_prompt(prompt):
    downloads_path = str(Path.home() / "Downloads" / "gegenereerde_prompt.md")
    with open(downloads_path, "w", encoding="utf-8") as f:
        f.write(f"# Gegenereerde Prompt\n\n{prompt}")
    return downloads_path

# Streamlit interface
st.title("🎯 Prompt Generator")

# Dropdown voor type prompt
prompt_type = st.selectbox("Kies het type prompt", ["Cursor", "Overige"])

# Input velden op basis van keuze
if prompt_type == "Cursor":
    st.subheader("Cursor Prompt Generator")
    
    # Project Overzicht
    st.markdown("### 1. Project Overzicht")
    project_naam = st.text_input("Project naam")
    project_doel = st.text_area("Project beschrijving", 
                               help="Beschrijf kort wat het doel is van je project en waarom je Cursor AI wilt gebruiken")
    
    # Technische Details
    st.markdown("### 2. Technische Details")
    col1, col2 = st.columns(2)
    with col1:
        programming_languages = st.multiselect(
            "Programmeertalen",
            ["Python", "JavaScript", "TypeScript", "Java", "C#", "PHP", "Ruby", "Go", "Rust", "Andere"],
            help="Selecteer alle programmeertalen die in je project worden gebruikt"
        )
        databases = st.multiselect(
            "Databases",
            ["MySQL", "PostgreSQL", "MongoDB", "SQLite", "Redis", "Geen", "Andere"],
            help="Selecteer de databases die je project gebruikt"
        )
    with col2:
        frameworks = st.multiselect(
            "Frameworks & Libraries",
            ["React", "Vue.js", "Angular", "Django", "Flask", "Express", "Spring", "Laravel", "Andere"],
            help="Selecteer de belangrijkste frameworks en libraries"
        )
        apis = st.text_area("API's & Externe Diensten",
                           help="Lijst van API's en externe diensten die je project gebruikt")
    
    # Bestandsstructuur
    st.markdown("### 3. Project Structuur")
    file_structure = st.text_area("Bestandsstructuur", 
                                 help="Beschrijf de belangrijkste mappen en bestanden in je project. Gebruik bijvoorbeeld een boomstructuur.",
                                 height=150)
    
    # Code Richtlijnen
    st.markdown("### 4. Code Richtlijnen")
    naming_conventions = st.text_area("Naamgevingsconventies",
                                    help="Beschrijf je voorkeuren voor het benoemen van variabelen, functies, klassen, etc.")
    code_style = st.text_area("Code Stijl",
                             help="Beschrijf je voorkeuren voor indentatie, commentaar, en andere stijlrichtlijnen")
    
    # Specifieke Instructies
    st.markdown("### 5. Specifieke Instructies")
    specific_tasks = st.text_area("Specifieke Taken",
                                 help="Beschrijf de specifieke taken of problemen waar je hulp bij nodig hebt van Cursor AI")
    
    # Best Practices
    st.markdown("### 6. Best Practices & Voorbeelden")
    examples = st.text_area("Code Voorbeelden",
                           help="Voeg relevante code voorbeelden toe die je stijl en voorkeuren illustreren")
    documentation = st.text_area("Documentatie Links",
                               help="Voeg links toe naar relevante documentatie of resources")

    # Aangepaste prompt generatie voor Cursor
    def genereer_cursor_prompt(project_info):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Je bent een expert in het schrijven van effectieve Cursor AI prompts."
                    },
                    {
                        "role": "user",
                        "content": f"""Genereer een gestructureerde Cursor AI prompt op basis van de volgende projectinformatie:
                        
                        Project Naam: {project_info['project_naam']}
                        Project Doel: {project_info['project_doel']}
                        
                        Technische Stack:
                        - Programmeertalen: {', '.join(project_info['programming_languages'])}
                        - Frameworks: {', '.join(project_info['frameworks'])}
                        - Databases: {', '.join(project_info['databases'])}
                        - API's: {project_info['apis']}
                        
                        Projectstructuur:
                        {project_info['file_structure']}
                        
                        Code Richtlijnen:
                        - Naamgeving: {project_info['naming_conventions']}
                        - Stijl: {project_info['code_style']}
                        
                        Specifieke Taken:
                        {project_info['specific_tasks']}
                        
                        Voorbeelden en Documentatie:
                        {project_info['examples']}
                        {project_info['documentation']}
                        
                        Genereer een duidelijke, gestructureerde prompt die Cursor AI kan gebruiken om effectief te helpen bij dit project."""
                    }
                ]
            )
            return response.choices[0].message['content']
        except Exception as e:
            return f"Er is een fout opgetreden: {str(e)}"

else:
    st.subheader("Algemene Prompt Generator")
    doel = st.text_input("Wat is het doel van je prompt?")
    context = st.text_area("Geef wat context voor je prompt")
    stijl = st.selectbox("Kies een stijl", ["Formeel", "Informeel", "Technisch", "Creatief", "Zakelijk"])

# Initialiseer session states
if 'gegenereerde_prompt' not in st.session_state:
    st.session_state.gegenereerde_prompt = None
if 'kopie_status' not in st.session_state:
    st.session_state.kopie_status = False
if 'download_status' not in st.session_state:
    st.session_state.download_status = False

# Reset functie
def reset_states():
    st.session_state.gegenereerde_prompt = None
    st.session_state.kopie_status = False
    st.session_state.download_status = False

# Aangepaste genereer knop logica
if st.button("Genereer Prompt"):
    if prompt_type == "Cursor":
        project_info = {
            'project_naam': project_naam,
            'project_doel': project_doel,
            'programming_languages': programming_languages,
            'frameworks': frameworks,
            'databases': databases,
            'apis': apis,
            'file_structure': file_structure,
            'naming_conventions': naming_conventions,
            'code_style': code_style,
            'specific_tasks': specific_tasks,
            'examples': examples,
            'documentation': documentation
        }
        
        if all(project_info.values()):  # Controleer of alle velden zijn ingevuld
            st.session_state.gegenereerde_prompt = genereer_cursor_prompt(project_info)
            st.session_state.kopie_status = False
            st.session_state.download_status = False
        else:
            st.warning("Vul alstublieft alle velden in")
    else:
        if doel and context and stijl:
            st.session_state.gegenereerde_prompt = genereer_prompt(doel, context, stijl)
            st.session_state.kopie_status = False
            st.session_state.download_status = False
        else:
            st.warning("Vul alstublieft alle velden in")

# Toon de prompt en knoppen als er een prompt is gegenereerd
if st.session_state.gegenereerde_prompt:
    # Markdown weergave
    st.markdown("### Gegenereerde Prompt")
    st.markdown(f"```\n{st.session_state.gegenereerde_prompt}\n```")
    
    # Knoppen in kolommen
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Kopieer naar Klembord"):
            pyperclip.copy(st.session_state.gegenereerde_prompt)
            st.session_state.kopie_status = True
    
    with col2:
        if st.button("Download Prompt"):
            bestandspad = save_prompt(st.session_state.gegenereerde_prompt)
            st.session_state.download_status = True
    
    with col3:
        if st.button("Reset"):
            reset_states()
            st.rerun()

    # Status berichten onder de knoppen
    if st.session_state.kopie_status:
        st.success("Prompt gekopieerd naar klembord!")
    if st.session_state.download_status:
        st.success(f"Prompt gedownload naar: {str(Path.home() / 'Downloads' / 'gegenereerde_prompt.md')}")