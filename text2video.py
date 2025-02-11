import streamlit as st
import torch
from diffusers import AnimateDiffPipeline, MotionAdapter, EulerDiscreteScheduler
from diffusers.utils import export_to_gif
from huggingface_hub import hf_hub_download
from safetensors.torch import load_file
import base64
from pathlib import Path
import time

# Thiết lập theme và style
st.set_page_config(
    page_title="Anime Text2Video Generator",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS cho giao diện anime
st.markdown("""
<style>
    .stApp {
        background-image: url("https://i.imgur.com/YourAnimeBackground.jpg");
        background-size: cover;
    }
    .stButton>button {
        background-color: #FF69B4;
        color: white;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        background-color: #FF1493;
    }
    .stTextInput>div>div>input {
        border-radius: 15px;
        border: 2px solid #FF69B4;
    }
    .css-1d391kg {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 2rem;
        border-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)

def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32
    
    with st.spinner("🌟 Đang tải model... Vui lòng đợi một chút!"):
        step = 4
        repo = "ByteDance/AnimateDiff-Lightning"
        ckpt = f"animatediff_lightning_{step}step_diffusers.safetensors"
        base = "emilianJR/epiCRealism"

        adapter = MotionAdapter().to(device, dtype)
        adapter.load_state_dict(load_file(hf_hub_download(repo, ckpt), device=device))
        pipe = AnimateDiffPipeline.from_pretrained(
            base, 
            motion_adapter=adapter, 
            torch_dtype=dtype
        ).to(device)
        pipe.scheduler = EulerDiscreteScheduler.from_config(
            pipe.scheduler.config, 
            timestep_spacing="trailing", 
            beta_schedule="linear"
        )
        return pipe

def generate_video(pipe, prompt, num_steps=4, guidance_scale=1.0):
    with st.spinner("✨ Đang tạo video anime của bạn..."):
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.1)
            progress_bar.progress(i + 1)
            
        output = pipe(
            prompt=prompt,
            guidance_scale=guidance_scale,
            num_inference_steps=num_steps
        )
        
        # Lưu và hiển thị kết quả
        export_to_gif(output.frames[0], "animation.gif")
        return "animation.gif"

def main():
    st.title("🌸 Anime Text-to-Video Generator 🌸")
    
    # Sidebar cho cài đặt
    with st.sidebar:
        st.header("⚙️ Cài đặt")
        theme = st.selectbox(
            "Chọn theme",
            ["Light", "Dark"],
            key="theme"
        )
        
        guidance_scale = st.slider(
            "Guidance Scale",
            0.1, 2.0, 1.0,
            step=0.1
        )
        
        num_steps = st.slider(
            "Số bước sinh",
            1, 8, 4,
            step=1
        )

    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        prompt = st.text_area(
            "✍️ Nhập mô tả cho video anime của bạn",
            height=100,
            placeholder="Ví dụ: An anime girl with long flowing hair standing in a cherry blossom garden..."
        )
        
        if st.button("🎨 Tạo Video", key="generate"):
            if not prompt:
                st.error("Vui lòng nhập mô tả!")
                return
                
            pipe = load_model()
            video_path = generate_video(
                pipe,
                prompt,
                num_steps,
                guidance_scale
            )
            
            # Hiển thị video kết quả
            with col2:
                st.success("✅ Video đã được tạo thành công!")
                st.image(video_path)
                
                # Tạo nút download
                with open(video_path, "rb") as file:
                    btn = st.download_button(
                        label="📥 Tải video",
                        data=file,
                        file_name="anime_video.gif",
                        mime="image/gif"
                    )

if __name__ == "__main__":
    main()
