import streamlit as st
import openai
from typing import Dict, List
import pyperclip

# Dictionary met beschikbare modellen en hun eigenschappen
AVAILABLE_MODELS: Dict[str, Dict] = {
    "GPT-4": {
        "model_name": "gpt-4-turbo-preview",
        "max_tokens": 4096,
        "temperature": 0.7
    },
    "GPT-3.5 Turbo": {
        "model_name": "gpt-3.5-turbo",
        "max_tokens": 4096,
        "temperature": 0.7
    },
    "Claude 3 Opus": {
        "model_name": "claude-3-opus-20240229",
        "max_tokens": 4096,
        "temperature": 0.7
    },
    "Claude 3 Sonnet": {
        "model_name": "claude-3-sonnet-20240229",
        "max_tokens": 4096,
        "temperature": 0.7
    }
}

def initialize_session_state():
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = list(AVAILABLE_MODELS.keys())[0]
    if 'prompt_type' not in st.session_state:
        st.session_state.prompt_type = "Cursor"
    if 'generated_response' not in st.session_state:
        st.session_state.generated_response = None
    if 'copied_to_clipboard' not in st.session_state:
        st.session_state.copied_to_clipboard = False

def copy_to_clipboard():
    if st.session_state.generated_response:
        pyperclip.copy(st.session_state.generated_response)
        st.session_state.copied_to_clipboard = True

def get_model_response(prompt: str, model_config: Dict) -> str:
    try:
        if "claude" in model_config["model_name"].lower():
            # Anthropic API aanroep
            response = anthropic.messages.create(
                model=model_config["model_name"],
                max_tokens=model_config["max_tokens"],
                temperature=model_config["temperature"],
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content
        else:
            # OpenAI API aanroep
            response = openai.ChatCompletion.create(
                model=model_config["model_name"],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=model_config["max_tokens"],
                temperature=model_config["temperature"]
            )
            return response.choices[0].message.content
    except Exception as e:
        st.error(f"Fout bij het genereren van respons: {str(e)}")
        return ""

def main():
    st.set_page_config(
        page_title="Prompt Generator",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Custom CSS voor mobiele optimalisatie
    st.markdown("""
        <style>
        .stButton button {
            width: 100%;
            margin: 5px 0;
        }
        .stTextArea textarea {
            font-size: 16px;
        }
        .stSelectbox select {
            font-size: 16px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("📱 Prompt Generator")
    initialize_session_state()

    # Model selectie
    selected_model = st.selectbox(
        "AI Model",
        options=list(AVAILABLE_MODELS.keys()),
        key="model_selector"
    )
    
    # Uitgebreide prompt types
    prompt_type = st.selectbox(
        "Type Prompt",
        options=["Cursor", "Code Review", "Bug Fix", "Documentatie", "API", "Database Query", "Test Cases", "UI/UX", "Overige"],
        key="prompt_type"
    )

    # Geavanceerde instellingen
    with st.expander("⚙️ Instellingen"):
        temperature = st.slider("Temperature", 0.0, 1.0, AVAILABLE_MODELS[selected_model]["temperature"])
        max_tokens = st.number_input("Max Tokens", 1, 4096, AVAILABLE_MODELS[selected_model]["max_tokens"])

    # Prompt input gebaseerd op type
    if prompt_type == "Cursor":
        with st.expander("📋 Project Details", expanded=True):
            project_naam = st.text_input("Project naam")
            project_doel = st.text_area("Project beschrijving", height=100)
            
            programming_languages = st.multiselect(
                "Programmeertalen",
                ["Python", "JavaScript", "TypeScript", "Java", "C#", "PHP", "Ruby", "Go", "Rust", "Andere"]
            )
            
            frameworks = st.multiselect(
                "Frameworks & Libraries",
                ["React", "Vue.js", "Angular", "Django", "Flask", "Express", "Spring", "Laravel", "Andere"]
            )
            
            databases = st.multiselect(
                "Databases",
                ["MySQL", "PostgreSQL", "MongoDB", "SQLite", "Redis", "Geen", "Andere"]
            )
            
            apis = st.text_input("API's & Externe Diensten")
            
            with st.expander("🔧 Extra Details"):
                file_structure = st.text_area("Projectstructuur", height=100)
                naming_conventions = st.text_input("Naamgevingsconventies")
                code_style = st.text_input("Code Stijl")
        
        if st.button("✨ Genereer Prompt", use_container_width=True):
            if all([project_naam, project_doel, programming_languages, frameworks]):
                prompt = f"""
                Project: {project_naam}
                Doel: {project_doel}
                
                Stack:
                - Talen: {', '.join(programming_languages)}
                - Frameworks: {', '.join(frameworks)}
                - Databases: {', '.join(databases) if databases else 'Geen'}
                - API's: {apis}
                
                Details:
                - Structuur: {file_structure}
                - Naamgeving: {naming_conventions}
                - Stijl: {code_style}
                """
                
                model_config = AVAILABLE_MODELS[selected_model].copy()
                model_config.update({
                    "temperature": temperature,
                    "max_tokens": max_tokens
                })
                
                with st.spinner("⚡ Genereren..."):
                    st.session_state.generated_response = get_model_response(prompt, model_config)
                    st.session_state.copied_to_clipboard = False
            else:
                st.warning("❗ Vul de belangrijkste velden in")
    
    elif prompt_type == "Code Review":
        with st.expander("📋 Code Review Details", expanded=True):
            code = st.text_area("Code om te reviewen", height=200)
            programming_language = st.selectbox(
                "Programmeertaal",
                ["Python", "JavaScript", "Java", "C#", "PHP", "Ruby", "Go", "Rust", "Andere"]
            )
            review_focus = st.multiselect(
                "Review Focus",
                ["Performance", "Security", "Clean Code", "Best Practices", "Documentation", "Error Handling"]
            )
            complexity_level = st.select_slider(
                "Code Complexiteit",
                options=["Beginner", "Intermediate", "Advanced", "Expert"]
            )

    elif prompt_type == "Bug Fix":
        with st.expander("🐛 Bug Details", expanded=True):
            error_message = st.text_area("Error Message/Bug Beschrijving")
            code_context = st.text_area("Relevante Code", height=150)
            expected_behavior = st.text_area("Verwacht Gedrag")
            steps_to_reproduce = st.text_area("Stappen om te Reproduceren")

    elif prompt_type == "Documentatie":
        with st.expander("📚 Documentatie Details", expanded=True):
            doc_type = st.selectbox(
                "Type Documentatie",
                ["README", "API Docs", "Code Comments", "Tutorial", "Technical Spec"]
            )
            target_audience = st.multiselect(
                "Doelgroep",
                ["Developers", "End Users", "System Admins", "Project Managers", "Technical Writers"]
            )
            content_scope = st.text_area("Scope van de Documentatie")
            code_examples = st.text_area("Code Voorbeelden (indien van toepassing)")

    elif prompt_type == "API":
        with st.expander("🔌 API Details", expanded=True):
            api_type = st.selectbox("API Type", ["REST", "GraphQL", "SOAP", "gRPC"])
            endpoint_description = st.text_area("Endpoint Beschrijving")
            request_method = st.selectbox("Request Method", ["GET", "POST", "PUT", "DELETE", "PATCH"])
            parameters = st.text_area("Parameters/Payload")
            authentication = st.selectbox(
                "Authenticatie",
                ["None", "API Key", "OAuth", "JWT", "Basic Auth"]
            )

    elif prompt_type == "Database Query":
        with st.expander("🗄️ Query Details", expanded=True):
            db_type = st.selectbox(
                "Database Type",
                ["MySQL", "PostgreSQL", "MongoDB", "SQLite", "Oracle", "SQL Server"]
            )
            query_type = st.selectbox(
                "Query Type",
                ["SELECT", "INSERT", "UPDATE", "DELETE", "JOIN", "Aggregation", "Index", "Optimization"]
            )
            table_structure = st.text_area("Tabel Structuur")
            query_goal = st.text_area("Doel van de Query")

    elif prompt_type == "Test Cases":
        with st.expander("🧪 Test Details", expanded=True):
            test_type = st.multiselect(
                "Type Tests",
                ["Unit Tests", "Integration Tests", "E2E Tests", "Performance Tests", "Security Tests"]
            )
            feature_description = st.text_area("Feature Beschrijving")
            test_scenarios = st.text_area("Test Scenarios")
            edge_cases = st.text_area("Edge Cases")

    elif prompt_type == "UI/UX":
        with st.expander("🎨 UI/UX Details", expanded=True):
            design_type = st.selectbox(
                "Type Design",
                ["Web App", "Mobile App", "Desktop App", "Component", "Landing Page"]
            )
            target_platform = st.multiselect(
                "Platform",
                ["iOS", "Android", "Web", "Desktop", "Cross-platform"]
            )
            design_requirements = st.text_area("Design Requirements")
            user_interaction = st.text_area("Gebruikers Interactie")
            accessibility = st.multiselect(
                "Accessibility Requirements",
                ["WCAG 2.1", "Screen Readers", "Keyboard Navigation", "Color Contrast", "None"]
            )

    else:  # Overige
        user_prompt = st.text_area("Prompt:", height=150)

    # Genereer knop en logica voor elk type
    if st.button("✨ Genereer Prompt", use_container_width=True):
        prompt = ""
        if prompt_type == "Cursor":
            # ... (bestaande Cursor logica)
            pass
        elif prompt_type == "Code Review":
            prompt = f"""
            Code Review Request:
            Language: {programming_language}
            Focus Areas: {', '.join(review_focus)}
            Complexity: {complexity_level}

            Code to Review:
            ```
            {code}
            ```
            """
        # ... (voeg hier vergelijkbare prompt constructie toe voor andere types)

        if prompt:
            model_config = AVAILABLE_MODELS[selected_model].copy()
            model_config.update({
                "temperature": temperature,
                "max_tokens": max_tokens
            })
            
            with st.spinner("⚡ Genereren..."):
                st.session_state.generated_response = get_model_response(prompt, model_config)
                st.session_state.copied_to_clipboard = False

    # Toon response en kopieer knop (blijft hetzelfde)
    if st.session_state.generated_response:
        st.markdown("### 📝 Gegenereerde Prompt")
        st.markdown(f"```\n{st.session_state.generated_response}\n```")
        
        if st.button("📋 Kopieer naar Klembord", use_container_width=True):
            copy_to_clipboard()
            st.success("✅ Gekopieerd naar klembord!")

if __name__ == "__main__":
    main()