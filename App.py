import streamlit as st
from moviepy.editor import VideoFileClip
import speech_recognition as sr
import os

st.set_page_config(page_title="Clipper + Auto Subtitle", page_icon="🎬")
st.title("🎬 Web Clipper + Auto Subtitle Gratis")
st.write("Potong video dan dapatkan teks subtitlenya otomatis menggunakan AI.")

# 1. Upload Video
uploaded_file = st.file_uploader("Upload video Anda (MP4, MKV, AVI)", type=["mp4", "mkv", "avi"])

if uploaded_file is not None:
    with open("temp_video.mp4", "wb") as f:
        f.write(uploaded_file.read())
    
    clip = VideoFileClip("temp_video.mp4")
    durasi_total = int(clip.duration)
    st.info(f"Durasi video asli: {durasi_total} detik")
    
    # 2. Slider Waktu
    waktu_potong = st.slider("Tentukan detik mulai dan selesai:", 0, durasi_total, (0, min(10, durasi_total)))
    detik_mulai, detik_selesai = waktu_potong
    
    # 3. Tombol Eksekusi
    if st.button("🚀 Potong & Buat Subtitle"):
        with st.spinner("1. Sedang memotong video..."):
            try:
                # Proses Potong
                video_terpotong = clip.subclip(detik_mulai, detik_selesai)
                output_video = "hasil_potongan.mp4"
                output_audio = "temp_audio.wav"
                
                # Simpan video hasil potongan
                video_terpotong.write_videofile(output_video, codec="libx264", audio_codec="aac", preset="ultrafast")
                
                # Ekstrak audio dari video terpotong untuk bahan subtitle
                st.spinner("2. Sedang mengekstrak suara dan membaca teks...")
                video_terpotong.audio.write_audiofile(output_audio, codec="pcm_s16le")
                
                # Close clip agar file tidak terkunci
                clip.close()
                video_terpotong.close()
                
                # Proses Auto Subtitle (Speech to Text)
                recognizer = sr.Recognizer()
                with sr.AudioFile(output_audio) as source:
                    audio_data = recognizer.record(source)
                    try:
                        # Menggunakan Google Speech Recognition (Bahasa Indonesia)
                        text_subtitle = recognizer.recognize_google(audio_data, language="id-ID")
                    except sr.UnknownValueError:
                        text_subtitle = "[Suara kurang jelas atau tidak ada percakapan terdeteksi]"
                    except sr.RequestError:
                        text_subtitle = "[Gagal terhubung ke server pengenal suara]"

                st.success("✅ Proses Selesai!")
                
                # 4. Tampilkan Hasil Subtitle di Layar Web
                st.subheader("📝 Hasil Teks / Subtitle Otomatis:")
                st.success(f'"{text_subtitle}"')
                
                # 5. Tombol Unduh Video
                with open(output_video, "rb") as file_hasil:
                    st.download_button(
                        label="⬇️ UNDUH VIDEO HASIL POTONGAN",
                        data=file_hasil,
                        file_name="video_terpotong.mp4",
                        mime="video/mp4"
                    )
                
                # Pembersihan file sampah di server
                if os.path.exists("temp_video.mp4"): os.remove("temp_video.mp4")
                if os.path.exists(output_video): os.remove(output_video)
                if os.path.exists(output_audio): os.remove(output_audio)
                
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
