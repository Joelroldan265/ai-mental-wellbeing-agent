import streamlit as st
from autogen import (SwarmAgent, SwarmResult, initiate_swarm_chat, OpenAIWrapper, AFTER_WORK, UPDATE_SYSTEM_MESSAGE)
import os

os.environ["AUTOGEN_USE_DOCKER"] = "0"

# ─── API KEY ────────────────────────────────────────────────────────────────
OPENAI_API_KEY = "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"
# ─────────────────────────────────────────────────────────────────────────────

if 'output' not in st.session_state:
    st.session_state.output = {'assessment': '', 'action': '', 'followup': ''}

if 'lang' not in st.session_state:
    st.session_state.lang = 'es'

# ─── TEXTOS BILINGÜES ────────────────────────────────────────────────────────
T = {
    'es': {
        'title': '🧠 Agente de Bienestar Mental',
        'lang_btn': '🌐 Switch to English',
        'warning_title': '⚠️ Aviso Importante',
        'warning_body': (
            "Esta aplicación es una herramienta de apoyo y **no reemplaza** la atención "
            "profesional de salud mental. Si estás en crisis:\n\n"
            "- 📞 Línea de crisis: 800-290-0024 (México)\n"
            "- 🚨 Emergencias: 911\n"
            "- Busca ayuda profesional de inmediato"
        ),
        'team_info': (
            "**Conoce a tu Equipo de Bienestar Mental:**\n\n"
            "🧠 **Agente de Evaluación** — Analiza tu situación y necesidades emocionales\n\n"
            "🎯 **Agente de Acción** — Crea un plan de acción inmediato y te conecta con recursos\n\n"
            "🔄 **Agente de Seguimiento** — Diseña tu estrategia de apoyo a largo plazo"
        ),
        'personal_info': '📋 Información Personal',
        'feeling': '¿Cómo te has sentido últimamente?',
        'feeling_placeholder': 'Describe tu estado emocional, pensamientos o preocupaciones...',
        'sleep': 'Patrón de Sueño (horas por noche)',
        'stress': 'Nivel de Estrés Actual (1-10)',
        'support': 'Sistema de Apoyo Actual',
        'support_opts': ['Familia', 'Amigos', 'Terapeuta', 'Grupos de Apoyo', 'Ninguno'],
        'changes': '¿Cambios o eventos significativos recientes?',
        'changes_placeholder': 'Cambios de trabajo, relaciones, pérdidas, etc...',
        'symptoms': 'Síntomas Actuales',
        'symptoms_opts': ['Ansiedad', 'Depresión', 'Insomnio', 'Fatiga', 'Pérdida de Interés',
                          'Dificultad para Concentrarse', 'Cambios en el Apetito',
                          'Aislamiento Social', 'Cambios de Humor', 'Malestar Físico'],
        'btn': '🔍 Obtener Plan de Apoyo',
        'spinner': '🤔 Los Agentes IA están analizando tu situación...',
        'assessment_exp': '📊 Evaluación de la Situación',
        'action_exp': '🎯 Plan de Acción y Recursos',
        'followup_exp': '🔄 Estrategia de Apoyo a Largo Plazo',
        'success': '✅ ¡Plan de bienestar mental generado exitosamente!',
        'error': 'Ocurrió un error: ',
        'assessment_label': 'Evaluación: ',
        'action_label': 'Plan de Acción: ',
        'followup_label': 'Seguimiento: ',
    },
    'en': {
        'title': '🧠 Mental Wellbeing Agent',
        'lang_btn': '🌐 Cambiar a Español',
        'warning_title': '⚠️ Important Notice',
        'warning_body': (
            "This application is a supportive tool and does **not replace** professional mental health care. "
            "If you're in crisis:\n\n"
            "- 📞 Crisis Hotline: 988 (USA)\n"
            "- 🚨 Emergency Services: 911\n"
            "- Seek immediate professional help"
        ),
        'team_info': (
            "**Meet Your Mental Wellbeing Agent Team:**\n\n"
            "🧠 **Assessment Agent** — Analyzes your situation and emotional needs\n\n"
            "🎯 **Action Agent** — Creates immediate action plan and connects you with resources\n\n"
            "🔄 **Follow-up Agent** — Designs your long-term support strategy"
        ),
        'personal_info': '📋 Personal Information',
        'feeling': 'How have you been feeling recently?',
        'feeling_placeholder': 'Describe your emotional state, thoughts, or concerns...',
        'sleep': 'Sleep Pattern (hours per night)',
        'stress': 'Current Stress Level (1-10)',
        'support': 'Current Support System',
        'support_opts': ['Family', 'Friends', 'Therapist', 'Support Groups', 'None'],
        'changes': 'Any significant life changes or events recently?',
        'changes_placeholder': 'Job changes, relationships, losses, etc...',
        'symptoms': 'Current Symptoms',
        'symptoms_opts': ['Anxiety', 'Depression', 'Insomnia', 'Fatigue', 'Loss of Interest',
                          'Difficulty Concentrating', 'Changes in Appetite', 'Social Withdrawal',
                          'Mood Swings', 'Physical Discomfort'],
        'btn': '🔍 Get Support Plan',
        'spinner': '🤔 AI Agents are analyzing your situation...',
        'assessment_exp': '📊 Situation Assessment',
        'action_exp': '🎯 Action Plan & Resources',
        'followup_exp': '🔄 Long-term Support Strategy',
        'success': '✅ Mental health support plan generated successfully!',
        'error': 'An error occurred: ',
        'assessment_label': 'Assessment: ',
        'action_label': 'Action Plan: ',
        'followup_label': 'Follow-up: ',
    }
}

# ─── SELECTOR DE IDIOMA ───────────────────────────────────────────────────────
lang = st.session_state.lang
t = T[lang]

st.sidebar.title("🌐 Idioma / Language")
if st.sidebar.button(t['lang_btn']):
    st.session_state.lang = 'en' if lang == 'es' else 'es'
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.warning(f"**{t['warning_title']}**\n\n{t['warning_body']}")

# ─── INTERFAZ PRINCIPAL ───────────────────────────────────────────────────────
st.title(t['title'])
st.info(t['team_info'])

st.subheader(t['personal_info'])
col1, col2 = st.columns(2)

with col1:
    mental_state = st.text_area(t['feeling'], placeholder=t['feeling_placeholder'])
    sleep_pattern = st.select_slider(
        t['sleep'],
        options=[f"{i}" for i in range(0, 13)],
        value="7"
    )

with col2:
    stress_level = st.slider(t['stress'], 1, 10, 5)
    support_system = st.multiselect(t['support'], t['support_opts'])

recent_changes = st.text_area(t['changes'], placeholder=t['changes_placeholder'])
current_symptoms = st.multiselect(t['symptoms'], t['symptoms_opts'])

# ─── LÓGICA PRINCIPAL ─────────────────────────────────────────────────────────
if st.button(t['btn'], type="primary"):
    with st.spinner(t['spinner']):
        try:
            task = f"""
            Create a comprehensive mental health support plan based on:
            Emotional State: {mental_state}
            Sleep: {sleep_pattern} hours per night
            Stress Level: {stress_level}/10
            Support System: {', '.join(support_system) if support_system else 'None reported'}
            Recent Changes: {recent_changes}
            Current Symptoms: {', '.join(current_symptoms) if current_symptoms else 'None reported'}
            Respond in {'Spanish' if lang == 'es' else 'English'}.
            """

            system_messages = {
                "assessment_agent": "You are an experienced mental health professional. Analyze the user's emotional state with clinical precision and genuine empathy. Use 'you' and 'your' when addressing the user.",
                "action_agent": "You are a crisis intervention and resource specialist. Provide immediate evidence-based coping strategies and create a concrete daily wellness plan.",
                "followup_agent": "You are a mental health recovery planner. Design a personalized long-term support strategy with milestone markers and relapse prevention strategies."
            }

            llm_config = {
                "config_list": [{"model": "gpt-4o", "api_key": OPENAI_API_KEY}]
            }

            context_variables = {"assessment": None, "action": None, "followup": None}

            def update_assessment_overview(assessment_summary: str, context_variables: dict) -> SwarmResult:
                context_variables["assessment"] = assessment_summary
                st.sidebar.success(t['assessment_label'] + assessment_summary[:80] + "...")
                return SwarmResult(agent="action_agent", context_variables=context_variables)

            def update_action_overview(action_summary: str, context_variables: dict) -> SwarmResult:
                context_variables["action"] = action_summary
                st.sidebar.success(t['action_label'] + action_summary[:80] + "...")
                return SwarmResult(agent="followup_agent", context_variables=context_variables)

            def update_followup_overview(followup_summary: str, context_variables: dict) -> SwarmResult:
                context_variables["followup"] = followup_summary
                st.sidebar.success(t['followup_label'] + followup_summary[:80] + "...")
                return SwarmResult(agent="assessment_agent", context_variables=context_variables)

            def update_system_message_func(agent: SwarmAgent, messages) -> str:
                system_prompt = system_messages[agent.name]
                current_gen = agent.name.split("_")[0]

                if agent._context_variables.get(current_gen) is None:
                    system_prompt += f" Call the update function to provide a 2-3 sentence summary of your ideas on {current_gen.upper()}."
                    agent.llm_config['tool_choice'] = {"type": "function", "function": {"name": f"update_{current_gen}_overview"}}
                else:
                    agent.llm_config["tools"] = None
                    agent.llm_config['tool_choice'] = None
                    system_prompt += f"\n\nWrite the {current_gen} part of the report. Do not include other parts. Start with: '## {current_gen.capitalize()} Plan'."
                    k = list(agent._oai_messages.keys())[-1]
                    agent._oai_messages[k] = agent._oai_messages[k][:1]

                system_prompt += "\n\nContext:\n"
                for k, v in agent._context_variables.items():
                    if v is not None:
                        system_prompt += f"\n{k.capitalize()} Summary:\n{v}"

                agent.client = OpenAIWrapper(**agent.llm_config)
                return system_prompt

            state_update = UPDATE_SYSTEM_MESSAGE(update_system_message_func)

            assessment_agent = SwarmAgent("assessment_agent", llm_config=llm_config, functions=update_assessment_overview, update_agent_state_before_reply=[state_update])
            action_agent = SwarmAgent("action_agent", llm_config=llm_config, functions=update_action_overview, update_agent_state_before_reply=[state_update])
            followup_agent = SwarmAgent("followup_agent", llm_config=llm_config, functions=update_followup_overview, update_agent_state_before_reply=[state_update])

            assessment_agent.register_hand_off(AFTER_WORK(action_agent))
            action_agent.register_hand_off(AFTER_WORK(followup_agent))
            followup_agent.register_hand_off(AFTER_WORK(assessment_agent))

            result, _, _ = initiate_swarm_chat(
                initial_agent=assessment_agent,
                agents=[assessment_agent, action_agent, followup_agent],
                user_agent=None,
                messages=task,
                max_rounds=13,
            )

            st.session_state.output = {
                'assessment': result.chat_history[-3]['content'],
                'action': result.chat_history[-2]['content'],
                'followup': result.chat_history[-1]['content']
            }

            with st.expander(t['assessment_exp'], expanded=True):
                st.markdown(st.session_state.output['assessment'])
            with st.expander(t['action_exp'], expanded=True):
                st.markdown(st.session_state.output['action'])
            with st.expander(t['followup_exp'], expanded=True):
                st.markdown(st.session_state.output['followup'])

            st.success(t['success'])

        except Exception as e:
            st.error(t['error'] + str(e))