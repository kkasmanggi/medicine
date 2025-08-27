import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# KONFIGURASI APLIKASI STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="Pemeriksa Penyakit",
    page_icon="⚕️",
    layout="centered"
)

# Judul dan deskripsi aplikasi
st.title("⚕️ DokterAI - Pemeriksa Penyakit")
st.markdown("Halo! Saya adalah DokterAI. Saya dapat membantu Anda mendiagnosis penyakit. Tuliskan gejala-gejala yang Anda rasakan untuk saya analisis.")
st.divider()

# ==============================================================================
# PENGATURAN API KEY DAN MODEL
# ==============================================================================
# Mengambil API Key dari Streamlit Secrets atau environment variable
API_KEY = st.secrets["AIzaSyBWzMBC6hVzvooktYrFkO5fvrDuJKVxqio"]
MODEL_NAME = 'gemini-1.5-flash'

# ==============================================================================
# FUNGSI UNTUK MENGHUBUNGI GEMINI API
# ==============================================================================
@st.cache_resource
def get_gemini_model():
    """Menginisialisasi dan mengkonfigurasi model Gemini. Menggunakan cache untuk efisiensi."""
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(
            MODEL_NAME,
            generation_config=genai.types.GenerationConfig(
                temperature=0.4,
                max_output_tokens=500
            )
        )
        st.success(f"Model '{MODEL_NAME}' berhasil diinisialisasi!", icon="✅")
        return model
    except Exception as e:
        st.error(f"⚠️ Kesalahan saat mengkonfigurasi atau menginisialisasi model Gemini: {e}")
        st.warning("Pastikan API Key Anda benar dan sudah terdaftar di Streamlit Secrets.")
        st.stop()

# ==============================================================================
# KONTEKS AWAL CHATBOT
# ==============================================================================
# Inisialisasi riwayat chat jika belum ada di session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "user",
            "parts": ["Saya seorang tenaga medis. Tuliskan penyakit yang perlu di diagnosis. Jawaban singkat dan jelas. Tolak pertanyaan selain tentang penyakit."]
        },
        {
            "role": "model",
            "parts": ["Baik! Tuliskan gejala-gejala atau penyakit yang perlu di diagnosis."]
        }
    ]

# Tampilkan pesan dari riwayat chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["parts"][0])

# ==============================================================================
# INTERAKSI PENGGUNA
# ==============================================================================
# Ambil input pengguna
if prompt := st.chat_input("Tuliskan gejala yang Anda rasakan..."):
    # Tambahkan input pengguna ke riwayat chat
    st.session_state.messages.append({"role": "user", "parts": [prompt]})
    
    # Tampilkan input pengguna di UI
    with st.chat_message("user"):
        st.markdown(prompt)

    # Dapatkan respons dari model
    with st.spinner("DokterAI sedang berpikir..."):
        try:
            model = get_gemini_model()
            # Gunakan riwayat chat dari session state untuk konteks
            chat_session = model.start_chat(history=st.session_state.messages)
            response = chat_session.send_message(prompt, request_options={"timeout": 60})
            gemini_response = response.text
            
            # Tambahkan respons model ke riwayat chat
            st.session_state.messages.append({"role": "model", "parts": [gemini_response]})
            
            # Tampilkan respons model di UI
            with st.chat_message("model"):
                st.markdown(gemini_response)

        except Exception as e:
            st.error(f"❌ Maaf, terjadi kesalahan saat berkomunikasi dengan DokterAI: {e}")
            st.warning("Silakan coba lagi. Pastikan API Key Anda valid.")

