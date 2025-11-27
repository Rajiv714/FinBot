"""
FinBot Frontend - Streamlit Application
Calls backend API for all operations
"""
import os
import sys
import streamlit as st
import httpx
from pathlib import Path
from typing import Dict, Any, List
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
from langdetect import detect

# Load environment variables
load_dotenv()

# Backend API configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Supported languages - Focus on Indian languages
LANGUAGES = {
    "English": "en",
    "Hindi (हिंदी)": "hi",
    "Bengali (বাংলা)": "bn",
    "Telugu (తెలుగు)": "te",
    "Marathi (मराठी)": "mr",
    "Tamil (தமிழ்)": "ta",
    "Gujarati (ગુજરાતી)": "gu",
    "Kannada (ಕನ್ನಡ)": "kn",
    "Malayalam (മലയാളം)": "ml",
    "Punjabi (ਪੰਜਾਬੀ)": "pa",
    "Odia (ଓଡ଼ିଆ)": "or",
    "Urdu (اردو)": "ur",
    "Assamese (অসমীয়া)": "as",
    "Konkani (कोंकणी)": "gom",
    "Sanskrit (संस्कृत)": "sa"
}

# Configure Streamlit page
st.set_page_config(
    page_title="FinBot - Financial Literacy Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #2E7D32, #4CAF50);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }

    .stButton > button,
    .stDownloadButton > button {
        width: 100%;
        min-height: 40px;
        padding: 0.5rem 0.9rem !important;
        background: #1E88E5 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        transition: background 0.15s ease !important;
    }
    
    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background: #1565C0 !important;
    }

    [data-testid="stCaptionContainer"] p {
        text-align: center;
        color: #6b7280;
        margin-top: 0.35rem;
        font-size: 0.9rem;
    }
    
    .language-selector {
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 999;
        background: white;
        padding: 0.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# Translation Functions
# ============================================================================

def translate_text(text: str, target_language: str) -> str:
    """Translate text to target language"""
    try:
        if target_language == "en" or not text:
            return text
        
        # Split long text into chunks (Google Translate has character limits)
        max_length = 4000
        if len(text) > max_length:
            # Split by paragraphs
            paragraphs = text.split('\n\n')
            translated_paragraphs = []
            
            for para in paragraphs:
                if para.strip():
                    if len(para) > max_length:
                        # Split long paragraphs by sentences
                        sentences = para.split('. ')
                        translated_sentences = []
                        for sentence in sentences:
                            if sentence.strip():
                                translated = GoogleTranslator(source='auto', target=target_language).translate(sentence)
                                translated_sentences.append(translated)
                        translated_paragraphs.append('. '.join(translated_sentences))
                    else:
                        translated = GoogleTranslator(source='auto', target=target_language).translate(para)
                        translated_paragraphs.append(translated)
            
            return '\n\n'.join(translated_paragraphs)
        else:
            # Translate directly for shorter text
            translated = GoogleTranslator(source='auto', target=target_language).translate(text)
            return translated
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original if translation fails


def get_ui_text(key: str, language: str) -> str:
    """Get UI text in selected language"""
    ui_texts = {
        "title": {
            "en": "FinBot - Financial Literacy Assistant",
            "hi": "फिनबॉट - वित्तीय साक्षरता सहायक",
            "bn": "ফিনবট - আর্থিক সাক্ষরতা সহায়ক",
            "te": "FinBot - ఆర్థిక అక్షరాస్యత సహాయకుడు",
            "mr": "फिनबॉट - आर्थिक साक्षरता सहाय्यक",
            "ta": "FinBot - நிதி எழுத்தறிவு உதவியாளர்",
            "gu": "FinBot - નાણાકીય સાક્ષરતા સહાયક",
            "kn": "FinBot - ಆರ್ಥಿಕ ಸಾಕ್ಷರತೆ ಸಹಾಯಕ",
            "ml": "FinBot - സാമ്പത്തിക സാക്ഷരത സഹായി",
            "pa": "FinBot - ਵਿੱਤੀ ਸਾਖਰਤਾ ਸਹਾਇਕ",
            "or": "FinBot - ଆର୍ଥିକ ସାକ୍ଷରତା ସହାୟକ",
            "ur": "فن بوٹ - مالیاتی خواندگی اسسٹنٹ",
        },
        "subtitle": {
            "en": "Your comprehensive financial education companion powered by AI",
            "hi": "AI द्वारा संचालित आपका व्यापक वित्तीय शिक्षा साथी",
            "bn": "AI দ্বারা চালিত আপনার বিস্তৃত আর্থিক শিক্ষা সঙ্গী",
            "te": "AI ద్వారా శక్తివంతం చేయబడిన మీ సమగ్ర ఆర్థిక విద్య సహచరుడు",
            "mr": "AI द्वारे समर्थित तुमचा सर्वसमावेशक आर्थिक शिक्षण सहकारी",
            "ta": "AI மூலம் இயக்கப்படும் உங்கள் விரிவான நிதிக் கல்வி துணை",
            "gu": "AI દ્વારા સંચાલિત તમારો વ્યાપક નાણાકીય શિક્ષણ સાથી",
            "kn": "AI ನಿಂದ ಚಾಲಿತವಾದ ನಿಮ್ಮ ಸಮಗ್ರ ಆರ್ಥಿಕ ಶಿಕ್ಷಣ ಸಹಚರ",
            "ml": "AI ഉപയോഗിച്ച് പ്രവർത്തിക്കുന്ന നിങ്ങളുടെ സമഗ്ര സാമ്പത്തിക വിദ്യാഭ്യാസ കൂട്ടാളി",
            "pa": "AI ਦੁਆਰਾ ਸੰਚਾਲਿਤ ਤੁਹਾਡਾ ਵਿਆਪਕ ਵਿੱਤੀ ਸਿੱਖਿਆ ਸਾਥੀ",
            "or": "AI ଦ୍ୱାରା ଚାଳିତ ଆପଣଙ୍କର ବ୍ୟାପକ ଆର୍ଥିକ ଶିକ୍ଷା ସାଥୀ",
            "ur": "AI سے چلنے والا آپ کا جامع مالیاتی تعلیم کا ساتھی",
        },
        "choose_feature": {
            "en": "Choose Your Financial Assistant Feature",
            "hi": "अपना वित्तीय सहायक सुविधा चुनें",
            "bn": "আপনার আর্থিক সহায়ক বৈশিষ্ট্য চয়ন করুন",
            "te": "మీ ఆర్థిక సహాయక లక్షణాన్ని ఎంచుకోండి",
            "mr": "तुमची आर्थिक सहाय्यक वैशिष्ट्य निवडा",
            "ta": "உங்கள் நிதி உதவியாளர் அம்சத்தைத் தேர்ந்தெடுக்கவும்",
            "gu": "તમારી નાણાકીય સહાયક સુવિધા પસંદ કરો",
            "kn": "ನಿಮ್ಮ ಆರ್ಥಿಕ ಸಹಾಯಕ ವೈಶಿಷ್ಟ್ಯವನ್ನು ಆರಿಸಿ",
            "ml": "നിങ്ങളുടെ സാമ്പത്തിക സഹായി സവിശേഷത തിരഞ്ഞെടുക്കുക",
            "pa": "ਆਪਣੀ ਵਿੱਤੀ ਸਹਾਇਕ ਵਿਸ਼ੇਸ਼ਤਾ ਚੁਣੋ",
            "or": "ଆପଣଙ୍କର ଆର୍ଥିକ ସହାୟକ ବୈଶିଷ୍ଟ୍ୟ ବାଛନ୍ତୁ",
            "ur": "اپنی مالیاتی معاون خصوصیت منتخب کریں",
        },
        "chatbot": {
            "en": "💬 Financial Chatbot",
            "hi": "💬 वित्तीय चैटबॉट",
            "bn": "💬 আর্থিক চ্যাটবট",
            "te": "💬 ఆర్థిక చాట్‌బాట్",
            "mr": "💬 आर्थिक चॅटबॉट",
            "ta": "💬 நிதி சாட்பாட்",
            "gu": "💬 નાણાકીય ચેટબોટ",
            "kn": "💬 ಆರ್ಥಿಕ ಚಾಟ್‌ಬಾಟ್",
            "ml": "💬 സാമ്പത്തിക ചാറ്റ്ബോട്ട്",
            "pa": "💬 ਵਿੱਤੀ ਚੈਟਬੋਟ",
            "or": "💬 ଆର୍ଥିକ ଚାଟବଟ୍",
            "ur": "💬 مالیاتی چیٹ بوٹ",
        },
        "learning_module": {
            "en": "📚 Learning Module Creator",
            "hi": "📚 शिक्षण मॉड्यूल निर्माता",
            "bn": "📚 শিক্ষা মডিউল নির্মাতা",
            "te": "📚 అభ్యాస మాడ్యూల్ సృష్టికర్త",
            "mr": "📚 शिक्षण मॉड्यूल निर्माता",
            "ta": "📚 கற்றல் தொகுதி உருவாக்குநர்",
            "gu": "📚 શિક્ષણ મોડ્યુલ નિર્માતા",
            "kn": "📚 ಕಲಿಕಾ ಮಾಡ್ಯೂಲ್ ಸೃಷ್ಟಿಕರ್ತ",
            "ml": "📚 പഠന മൊഡ്യൂൾ സ്രഷ്ടാവ്",
            "pa": "📚 ਸਿੱਖਿਆ ਮੋਡਿਊਲ ਨਿਰਮਾਤਾ",
            "or": "📚 ଶିକ୍ଷା ମଡ୍ୟୁଲ୍ ନିର୍ମାତା",
            "ur": "📚 سیکھنے والا ماڈیول بنانے والا",
        },
        "back_home": {
            "en": "← Back to Home",
            "hi": "← होम पर वापस जाएं",
            "bn": "← হোমে ফিরে যান",
            "te": "← హోమ్‌కు తిరిగి వెళ్లండి",
            "mr": "← मुख्यपृष्ठावर परत या",
            "ta": "← முகப்புக்குத் திரும்பு",
            "gu": "← હોમ પર પાછા જાઓ",
            "kn": "← ಮುಖಪುಟಕ್ಕೆ ಹಿಂತಿರುಗಿ",
            "ml": "← ഹോമിലേക്ക് മടങ്ങുക",
            "pa": "← ਘਰ ਵਾਪਸ ਜਾਓ",
            "or": "← ହୋମକୁ ଫେରନ୍ତୁ",
            "ur": "← ہوم پر واپس جائیں",
        }
    }
    
    return ui_texts.get(key, {}).get(language, ui_texts.get(key, {}).get("en", ""))


# ============================================================================
# API Client Functions
# ============================================================================

async def api_chat(query: str, include_context: bool = True) -> Dict[str, Any]:
    """Call chat API"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{BACKEND_URL}/api/chat",
            json={
                "query": query,
                "include_context": include_context
            }
        )
        return response.json()


async def api_create_handout(
    topic: str,
    target_length: int = 1200,
    include_google_search: bool = True
) -> Dict[str, Any]:
    """Call handout creation API"""
    async with httpx.AsyncClient(timeout=300.0) as client:  # 5 min timeout
        response = await client.post(
            f"{BACKEND_URL}/api/handouts",
            json={
                "topic": topic,
                "target_length": target_length,
                "include_google_search": include_google_search,
                "search_depth": "standard"
            }
        )
        return response.json()


async def api_get_status() -> Dict[str, Any]:
    """Get system status"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{BACKEND_URL}/api/status")
        return response.json()


# ============================================================================
# Main Application
# ============================================================================

def main():
    """Main Streamlit application"""
    
    # Initialize session state
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"
    if "selected_language" not in st.session_state:
        st.session_state.selected_language = "English"
    
    # Language selector in top right corner
    col_empty, col_lang = st.columns([6, 1])
    with col_lang:
        selected_language = st.selectbox(
            "🌐",
            options=list(LANGUAGES.keys()),
            index=list(LANGUAGES.keys()).index(st.session_state.selected_language),
            key="language_selector",
            label_visibility="collapsed"
        )
        if selected_language != st.session_state.selected_language:
            st.session_state.selected_language = selected_language
            st.rerun()
    
    lang_code = LANGUAGES[st.session_state.selected_language]
    
    # Header with translated text
    st.markdown(
        f"""
        <div class="main-header">
            <h1>💰 {get_ui_text('title', lang_code)}</h1>
            <p>{get_ui_text('subtitle', lang_code)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Navigation
    if st.session_state.current_page == "home":
        show_home_page(lang_code)
    elif st.session_state.current_page == "chatbot":
        show_chatbot_page(lang_code)
    elif st.session_state.current_page == "learning_module":
        show_learning_module_page(lang_code)


def show_home_page(lang_code: str):
    """Display home page with feature cards"""
    
    st.markdown(f"## {get_ui_text('choose_feature', lang_code)}")
    
    # Feature cards - only 2 now
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(get_ui_text('chatbot', lang_code), key="chatbot_card", use_container_width=True):
            st.session_state.current_page = "chatbot"
            st.rerun()
        caption_text = translate_text("Ask questions about financial concepts and get expert guidance", lang_code)
        st.caption(caption_text)
    
    with col2:
        if st.button(get_ui_text('learning_module', lang_code), key="learning_card", use_container_width=True):
            st.session_state.current_page = "learning_module"
            st.rerun()
        caption_text = translate_text("Generate 1000-1200 word educational handouts on financial topics", lang_code)
        st.caption(caption_text)


def show_chatbot_page(lang_code: str):
    """Display chatbot interface"""
    
    # Back button
    if st.button(get_ui_text('back_home', lang_code)):
        st.session_state.current_page = "home"
        st.rerun()
    
    chatbot_title = translate_text("Financial Chatbot", lang_code)
    chatbot_desc = translate_text("Ask me anything about finance, investments, or personal money management!", lang_code)
    
    st.markdown(f"## {chatbot_title}")
    st.markdown(chatbot_desc)
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for question, answer in st.session_state.chat_history:
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            st.markdown(answer)
    
    # Chat input
    input_placeholder = translate_text("Ask your financial question...", lang_code)
    if prompt := st.chat_input(input_placeholder):
        # Add user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            spinner_text = translate_text("Searching knowledge base...", lang_code)
            with st.spinner(spinner_text):
                import asyncio
                try:
                    # Translate question to English for API
                    english_prompt = translate_text(prompt, "en") if lang_code != "en" else prompt
                    
                    response = asyncio.run(api_chat(english_prompt))
                    answer = response.get("answer", "No response")
                    
                    # Translate answer back to selected language
                    translated_answer = translate_text(answer, lang_code)
                    
                    st.markdown(translated_answer)
                    st.session_state.chat_history.append((prompt, translated_answer))
                    
                    # Show sources
                    if response.get("sources"):
                        sources_label = translate_text("View Sources", lang_code)
                        with st.expander(sources_label):
                            for i, source in enumerate(response["sources"][:3], 1):
                                st.markdown(f"**{translate_text('Source', lang_code)} {i}** ({translate_text('Score', lang_code)}: {source['score']:.3f})")
                                st.markdown(f"📄 {source.get('metadata', {}).get('filename', 'Unknown')}")
                                st.markdown(f"{source['text'][:200]}...")
                                st.markdown("---")
                    
                except Exception as e:
                    error_msg = translate_text(f"Error: {str(e)}", lang_code)
                    st.error(error_msg)
                    st.session_state.chat_history.append((prompt, error_msg))
    
    # Clear chat
    clear_button_text = translate_text("Clear Chat History", lang_code)
    if st.button(clear_button_text):
        st.session_state.chat_history = []
        st.rerun()


def show_learning_module_page(lang_code: str):
    """Display learning module creation interface"""
    
    # Back button
    if st.button(get_ui_text('back_home', lang_code)):
        st.session_state.current_page = "home"
        st.rerun()
    
    module_title = translate_text("Create Learning Module", lang_code)
    module_desc = translate_text("Get a comprehensive handout on any financial topic in seconds.", lang_code)
    
    st.markdown(f"## {module_title}")
    st.markdown(module_desc)
    
    # Topic input
    topic_label = translate_text("Enter the financial topic:", lang_code)
    topic_placeholder = translate_text("e.g., Mutual Funds, Personal Finance Basics, Investment Strategies", lang_code)
    topic = st.text_input(topic_label, placeholder=topic_placeholder)
    
    # Suggested topics
    st.markdown(f"**{translate_text('Suggested Topics:', lang_code)}**")
    suggested_topics = [
        "Mutual Funds", "Personal Finance Basics", "Investment Strategies",
        "Retirement Planning", "Tax Planning", "Insurance Planning", "Credit Management"
    ]
    
    cols = st.columns(4)
    for i, suggested_topic in enumerate(suggested_topics):
        with cols[i % 4]:
            translated_topic = translate_text(suggested_topic, lang_code)
            if st.button(translated_topic, key=f"topic_{i}"):
                topic = suggested_topic
                st.rerun()
    
    # Options
    col1, col2 = st.columns(2)
    with col1:
        target_label = translate_text("Target Word Count:", lang_code)
        target_length = st.selectbox(target_label, [1000, 1100, 1200], index=2)
    
    with col2:
        news_label = translate_text("Include Latest News (Google Search)", lang_code)
        news_help = translate_text("Uses SERPAPI to fetch latest information", lang_code)
        include_google = st.checkbox(news_label, value=True, help=news_help)
    
    # Generate button
    generate_btn_text = translate_text("Generate Learning Module", lang_code)
    if st.button(generate_btn_text, type="primary", disabled=not topic):
        if topic:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            import asyncio
            try:
                creating_msg = translate_text("Creating your learning module...", lang_code)
                status_text.text(creating_msg)
                progress_bar.progress(50)
                
                # Translate topic to English for API
                english_topic = translate_text(topic, "en") if lang_code != "en" else topic
                
                result = asyncio.run(api_create_handout(
                    topic=english_topic,
                    target_length=target_length,
                    include_google_search=include_google
                ))
                
                progress_bar.progress(100)
                
                # Check if actually successful (has content)
                handout_content = result.get('handout_content', '')
                
                # If there's an API error in the content, show error
                if "exceeded your current quota" in handout_content or "technical difficulties" in handout_content:
                    error_msg = translate_text("Failed to generate handout", lang_code)
                    st.error(f"❌ {error_msg}")
                    st.warning(handout_content)
                    status_text.text("")
                    progress_bar.empty()
                    return
                
                # Check if content is too short (probably an error)
                if len(handout_content.split()) < 100:
                    error_msg = translate_text("Failed to generate handout - received incomplete response", lang_code)
                    st.error(f"❌ {error_msg}")
                    if handout_content:
                        st.warning(handout_content)
                    status_text.text("")
                    progress_bar.empty()
                    return
                
                # Translate handout content to selected language
                if lang_code != "en":
                    translating_msg = translate_text("Translating to your language...", lang_code)
                    status_text.text(translating_msg)
                    handout_content = translate_text(handout_content, lang_code)
                
                # Success!
                status_text.text("")
                progress_bar.empty()
                
                if result.get("success") and handout_content:
                    success_msg = translate_text("Learning module created successfully!", lang_code)
                    st.success(f"✅ {success_msg}")
                    
                    # Display content with download button
                    module_header = translate_text("Your Learning Module", lang_code)
                    st.markdown(f"### {module_header}")
                    
                    download_label = translate_text("📥 Download as Markdown", lang_code)
                    st.download_button(
                        label=download_label,
                        data=handout_content,
                        file_name=f"{topic.replace(' ', '_')}_handout.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                    
                    # Show the content
                    st.markdown("---")
                    st.markdown(handout_content)
                else:
                    error_text = translate_text(f"Error: {result.get('error', 'Failed to generate handout')}", lang_code)
                    st.error(f"❌ {error_text}")
                    
            except Exception as e:
                status_text.text("")
                progress_bar.empty()
                error_creating = translate_text(f"Error creating learning module: {str(e)}", lang_code)
                st.error(f"❌ {error_creating}")
                backend_info = translate_text(f"Make sure the backend server is running at {BACKEND_URL}", lang_code)
                st.info(f"💡 {backend_info}")


# ============================================================================
# Run Application
# ============================================================================

if __name__ == "__main__":
    main()
