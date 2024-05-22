##### 기본 정보 입력 #####
import streamlit as st
# audiorecorder 패키지 추가
from audiorecorder import audiorecorder
# OpenAI 패키기 추가
import openai
# 파일 삭제를 위한 패키지 추가
import os
# 시간 정보를 위핸 패키지 추가
from datetime import datetime
# TTS 패키기 추가
from gtts import gTTS
# 음원파일 재생을 위한 패키지 추가
import base64
### 구글 translator api import ####
from googletrans import Translator
tlangs = ('en', 'es', 'fr', 'de', 'zh', 'ja', 'ru', 'ar', 'pt', 'hi', 'bn', 'pa', 'id', 'ms', 'sw', 'ta', 'te', 'vi', 'ko', 'it', 'nl', 'pl', 'uk', 'tr', 'fa', 'ur', 'he', 'el', 'sv', 'fi', 'no', 'da', 'hu', 'cs', 'ro', 'sk', 'bg', 'hr', 'sr', 'th')


##### 기능 구현 함수 #####
def google_trans(messages,targetLang):
    google = Translator()
    result = google.translate(messages, dest=targetLang, timeout=10)
    return result.text
def STT(audio):
    # 파일 저장
    filename='input.mp3'
    audio.export(filename, format="mp3")
    # 음원 파일 열기
    audio_file = open(filename, "rb")
    #Whisper 모델을 활용해 텍스트 얻기
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    audio_file.close()
    # 파일 삭제
    os.remove(filename)
    return transcript["text"]


def TTS(response,targetLang):
    # gTTS 를 활용하여 음성 파일 생성
    filename = "output.mp3"
    tts = gTTS(text=response,lang=targetLang)
    tts.save(filename)

    # 음원 파일 자동 재성
    with open(filename, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="True">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md,unsafe_allow_html=True,)
    # 파일 삭제
    os.remove(filename)

##### 메인 함수 #####
def main():
    # 기본 설정
    st.set_page_config(
        page_title="음성 자동인식 번역",
        layout="wide")

    # session state 초기화
    if "chat" not in st.session_state:
        st.session_state["chat"] = []

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}]

    if "check_reset" not in st.session_state:
        st.session_state["check_reset"] = False

    # 제목 
    st.header("번역 프로그램")
    # 구분선
    st.markdown("---")

    # 기본 설명
    with st.expander("translator", expanded=True):
        st.write(
        """     
        -원하는 번역결과를 얻으세요 .
        """
        )

        st.markdown("")



    # Open AI API 키 
    openai.api_key = st.secrets["OPENAI_API_KEY"]

        

    # GPT 모델
    model = "gpt-3.5-turbo"


    
            
    # 기능 구현 공간
    col1, col2 =  st.columns(2)
    with col1:
        # 왼쪽 영역 작성
        st.subheader("질문하기")
        targetLang=st.selectbox('Select target language', tlangs)
        # 음성 녹음 아이콘 추가
        audio = audiorecorder("클릭하여 녹음하기", "녹음중...")
        if (audio.duration_seconds > 0) and (st.session_state["check_reset"]==False):
            # 음성 재생 
            st.audio(audio.export().read())
            # 음원 파일에서 텍스트 추출
            question = STT(audio)
                                                                
            # 채팅을 시각화하기 위해 질문 내용 저장
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"]+ [("user",now, question)]
            

    with col2:
        # 오른쪽 영역 작성
        st.subheader("질문/답변")
        if  (audio.duration_seconds > 0)  and (st.session_state["check_reset"]==False):
            #구글번역
            
            response = google_trans(question,targetLang)

           

            # 채팅 시각화를 위한 답변 내용 저장
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"]+ [("bot",now, response)]

            # 채팅 형식으로 시각화 하기
            for sender, time, message in st.session_state["chat"]:
                if sender == "user":
                    st.write(f'<div style="display:flex;align-items:center;"><div style="background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', unsafe_allow_html=True)
                    st.write("")
                else:
                    st.write(f'<div style="display:flex;align-items:center;justify-content:flex-end;"><div style="background-color:lightgray;border-radius:12px;padding:8px 12px;margin-left:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', unsafe_allow_html=True)
                    st.write("")
            
            # gTTS 를 활용하여 음성 파일 생성 및 재생
            TTS(response,targetLang)
        else:
            st.session_state["check_reset"] = False

if __name__=="__main__":
    main()