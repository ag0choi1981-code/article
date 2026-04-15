import streamlit as st
import pandas as pd
import google.generativeai as genai
import re
import os
from datetime import datetime
from urllib.parse import urlparse

# 커스텀 모듈 임포트
from universal_crawler import UniversalNewsCrawler
from enhanced_sentiment_analyzer import EnhancedSentimentAnalyzer

# API 키 저장 파일 경로
API_KEY_FILE = "gemini_api_key.txt"

def load_api_key():
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE, "r") as f:
            return f.read().strip()
    return ""

def save_api_key(api_key):
    with open(API_KEY_FILE, "w") as f:
        f.write(api_key)

# 페이지 설정
st.set_page_config(
    page_title="📊 네이버 뉴스 댓글 여론 분석 시스템 (Gemini)",
    page_icon="📊",
    layout="wide"
)

# 커스텀 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .report-box {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #e1e4e8;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 2rem;
        font-family: 'Malgun Gothic', sans-serif;
    }
    .comment-list {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# API 키 설정 (사이드바)
st.sidebar.header("🔑 API 설정")
saved_key = load_api_key()
GOOGLE_API_KEY = st.sidebar.text_input("Gemini API Key", value=saved_key, type="password")

if GOOGLE_API_KEY:
    if GOOGLE_API_KEY != saved_key:
        save_api_key(GOOGLE_API_KEY)
else:
    st.warning("⚠️ 사이드바에 Gemini API 키를 입력해주세요!")
    st.stop()

# Gemini 설정
genai.configure(api_key=GOOGLE_API_KEY)

def get_best_model():
    """사용 가능한 최적의 Gemini 모델 자동 선택 및 할당량 고려"""
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 429 에러 방지를 위해 할당량이 넉넉한 Flash 모델만 사용 (Pro는 무료 티어에서 사실상 사용 불가)
        preferences = [
            'models/gemini-1.5-flash',
            'models/gemini-1.5-flash-latest',
            'models/gemini-2.0-flash-exp', # 최신 Flash 모델 추가
            'models/gemini-1.5-flash-8b'    # 가벼운 모델 추가
        ]
        
        for pref in preferences:
            if pref in models:
                return genai.GenerativeModel(pref)
            short_pref = pref.replace('models/', '')
            for m in models:
                if short_pref in m:
                    return genai.GenerativeModel(m)
        
        # Flash 모델을 찾지 못한 경우에만 가용한 첫 번째 모델 선택
        if models:
            # Pro 모델이 포함되어 있을 수 있으므로 필터링 시도
            flash_models = [m for m in models if 'flash' in m.lower()]
            if flash_models:
                return genai.GenerativeModel(flash_models[0])
            return genai.GenerativeModel(models[0])
    except Exception as e:
        st.error(f"모델 목록 조회 실패: {e}")
    return genai.GenerativeModel('gemini-1.5-flash')

# 전역 변수로 model 정의 및 Streamlit UI 요소 배치
model = get_best_model()

st.markdown('<div class="main-header">📊 네이버 뉴스 댓글 여론 분석 시스템</div>', unsafe_allow_html=True)

# URL 입력창
urls_input = st.text_area("분석할 뉴스 기사 링크를 입력하세요 (한 줄에 하나씩, 최대 5개)", height=100)
max_comments = st.sidebar.slider("💬 기사당 최대 댓글 수", 10, 100, 50)

analyze_btn = st.button("📈 여론 분석 시작", type="primary")

def analyze_with_gemini_integrated(articles_data):
    """여러 기사의 댓글을 통합하여 하나의 여론 분석 보고서 생성"""
    import time
    global model
    
    # 모든 기사의 댓글 통합
    all_comments = []
    seen_contents = set() # 중복 내용 체크용 세트
    
    total_view_count = 0
    total_comment_count = 0
    article_titles_formatted = []
    
    for i, data in enumerate(articles_data, 1):
        info = data['info']
        df = data['df']
        
        # 기사별 데이터 합산 및 포맷팅
        site = info.get('site_display', '정보없음')
        title = info.get('title', '제목없음')
        v_count = info.get('view_count', '0')
        c_count = info.get('comment_count', '0')
        
        # 기사 제목에 번호 붙여서 포맷팅
        article_titles_formatted.append(f"{i}. ({site}) {title} [조회수 {v_count}, 댓글수 {c_count}]")
        
        # 중복 제거 로직 적용하며 댓글 추가
        for _, row in df.iterrows():
            content = str(row['content']).strip()
            # 공백 제거 및 소문자 변환하여 엄격하게 중복 체크
            content_key = re.sub(r'\s+', '', content).lower()
            
            if content_key not in seen_contents:
                seen_contents.add(content_key)
                all_comments.append(row.to_dict())
        
        # 숫자 추출 및 합산
        try:
            v_num = int(re.sub(r'[^0-9]', '', str(v_count))) if re.sub(r'[^0-9]', '', str(v_count)) else 0
            c_num = int(re.sub(r'[^0-9]', '', str(c_count))) if re.sub(r'[^0-9]', '', str(c_count)) else 0
            total_view_count += v_num
            total_comment_count += c_num
        except:
            pass
            
    # 통합 댓글 중복 제거 및 샘플링 로직 개선
    integrated_df = pd.DataFrame(all_comments)
    if not integrated_df.empty:
        # 1. 공감순 상위 70개 (베스트 의견)
        top_liked = integrated_df.sort_values('like_count', ascending=False).head(70)
        
        # 2. 최신순/다양한 의견 30개 (공감수는 적지만 새로운 시각 반영)
        # 상위 70개에 포함되지 않은 나머지 댓글 중 랜덤 샘플링
        remaining = integrated_df[~integrated_df.index.isin(top_liked.index)]
        if not remaining.empty:
            diverse_opinions = remaining.sample(n=min(30, len(remaining)), random_state=42)
            final_sample_df = pd.concat([top_liked, diverse_opinions])
        else:
            final_sample_df = top_liked
            
        final_sample_df = final_sample_df.reset_index(drop=True)
    else:
        final_sample_df = pd.DataFrame()
    
    comments_text = ""
    for _, row in final_sample_df.iterrows():
        clean_content = str(row['content'])[:200]
        comments_text += f"- {clean_content} (공감: {row['like_count']})\n"

    titles_block = "\n".join(article_titles_formatted)
    
    prompt = f"""실제 뉴스 댓글 데이터를 통합 분석하여 보고서를 작성하세요. 
유사한 주제의 여러 기사 댓글을 합산하여 전체적인 민심의 흐름을 파악해야 합니다.

[분석 대상 기사]
{titles_block}

[데이터 요약]
통합 분석 댓글 수: {len(final_sample_df)}개 (공감순 및 다양성 기반 샘플링)
전체 기사 본문 기반 핵심 주제를 파악하여 분석하세요.

[댓글 데이터 정보]
{comments_text}

[작성 지침]
1. 보고서 최상단에 반드시 다음 형식을 기재하세요: [반응 많은 뉴스]
2. 그 바로 아래에 분석 대상 기사 목록을 모두 나열하세요.
3. 종합 요약: 통합된 전체 여론의 핵심 줄기를 한 줄로 요약.
4. 세부 여론 동향: 입장별 비율 산정 및 핵심 내용을 △ 기호와 함께 명사형으로 나열. 구체적 우려/지지 사항 포함.
5. 실제 댓글 리스트: **비판**, **옹호**, **기타** 각 반응별로 가장 대표적인 댓글을 **최대 10개씩** 선정하여 리스트업하세요. 각 섹션 아래에 (비판반응), (옹호반응), (기타반응)과 같이 구분 제목을 달고, 그 아래부터는 [비판], [옹호], [기타] 접두사 없이 내용만 작성하세요.

[양식]
[반응 많은 뉴스]
{titles_block}

□ (종합 요약) 내용
□ (세부 여론 동향)
- (비판, %%) △내용1, △내용2, △내용3
- (옹호/기타, %%) △내용1, △내용2
**[실제 댓글 리스트]**
(비판반응)
1. 내용
...
(옹호반응)
1. 내용
...
(기타반응)
1. 내용
..."""

    max_retries = 3
    for attempt in range(max_retries + 1):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg and attempt < max_retries:
                wait_time = 60
                retry_match = re.search(r'(\d+)\s*(초|seconds|s)', error_msg)
                if retry_match:
                    wait_time = int(retry_match.group(1)) + 5
                time.sleep(wait_time)
                continue
            return f"Gemini 분석 중 에러가 발생했습니다: {error_msg}"

def analyze_with_gemini(title, content, comments_df, site_display="정보없음", view_count="정보없음", comment_count="정보없음"):
    """Gemini를 사용하여 여론 분석 보고서 생성 (재시도 로직 포함)"""
    import time
    
    # 함수 내에서 전역 변수 model 사용 선언
    global model
    
    # 토큰 절약을 위해 댓글 텍스트 최적화 (중요도가 낮은 댓글은 생략)
    # 공감순으로 정렬 후 상위 30개만 분석에 사용
    top_comments = comments_df.sort_values('like_count', ascending=False).head(30)
    
    comments_text = ""
    for _, row in top_comments.iterrows():
        # 댓글 길이 제한 (200자)
        clean_content = str(row['content'])[:200]
        comments_text += f"- {clean_content} (공감: {row['like_count']})\n"

    # 프롬프트 경량화 및 정확도 향상
    prompt = f"""실제 뉴스 댓글 데이터를 분석하여 보고서를 작성하세요. 
모든 핵심 여론(비판, 옹호, 우려, 제안 등)을 빠짐없이 반영해야 합니다.

[데이터]
뉴스정보: ({site_display}) {title} [조회수 {view_count}, 댓글수 {comment_count}]
기사요약: {content[:400]}
댓글리스트(공감순):
{comments_text}

[작성 지침]
1. 보고서 최상단에 반드시 다음 형식을 기재하세요: ({site_display}) {title} [조회수 {view_count}, 댓글수 {comment_count}]
2. 종합 요약: 전체 여론의 핵심 줄기를 한 줄로 요약.
3. 세부 여론 동향: 입장별 비율 산정 및 핵심 내용을 △ 기호와 함께 명사형으로 나열. 구체적 우려 사항 포함.
4. 실제 댓글 리스트: **비판**, **옹호**, **기타** 각 반응별로 가장 대표적인 댓글을 **최대 10개씩** 선정하여 리스트업하세요.

[양식]
({site_display}) {title} [조회수 {view_count}, 댓글수 {comment_count}]

□ (종합 요약) 내용
□ (세부 여론 동향)
- (비판, %%) △내용1, △내용2, △내용3
- (옹호/기타, %%) △내용1, △내용2
**[실제 댓글 리스트]**
(비판 반응)
1. "[비판] 내용"
...
(옹호 반응)
1. "[옹호] 내용"
...
(기타/제안)
1. "[기타] 내용"
..."""

    # 할당량 초과(429) 발생 시 재시도 로직
    max_retries = 3 # 재시도 횟수 증가
    for attempt in range(max_retries + 1):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg and attempt < max_retries:
                # 에러 메시지에서 대기 시간 추출 시도 (기본 60초)
                wait_time = 60
                retry_match = re.search(r'(\d+)\s*(초|seconds|s)', error_msg)
                if retry_match:
                    wait_time = int(retry_match.group(1)) + 5 # 안전하게 5초 추가
                
                st.warning(f"⚠️ API 할당량 초과로 {wait_time}초 후 다시 시도합니다... (시도 {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            return f"Gemini 분석 중 에러가 발생했습니다: {error_msg}"

# 분석 시작
if analyze_btn:
    urls = [url.strip() for url in urls_input.split('\n') if url.strip()]
    
    if not urls:
        st.warning("분석할 뉴스 링크를 입력해주세요.")
    elif len(urls) > 5:
        st.error("최대 5개의 링크까지만 분석 가능합니다.")
    else:
        crawler = UniversalNewsCrawler()
        sentiment_analyzer = EnhancedSentimentAnalyzer()
        
        all_articles_data = []
        
        with st.spinner("기사 정보를 수집 중입니다..."):
            for url in urls:
                info = crawler.get_news_info(url)
                # 댓글 100개까지 수집
                comments = crawler.get_comments(url, 100) 
                
                if info and comments:
                    results = sentiment_analyzer.analyze_comments(comments)
                    df = pd.DataFrame(results)
                    all_articles_data.append({'info': info, 'df': df, 'url': url})
                else:
                    st.error(f"'{url}' 데이터를 가져오지 못했습니다.")

        if all_articles_data:
            with st.spinner("통합 여론 분석 중입니다..."):
                # 통합 분석 수행
                report = analyze_with_gemini_integrated(all_articles_data)
                
                st.markdown("### 📊 통합 여론 분석 결과")
                st.markdown(f'<div class="report-box">{report}</div>', unsafe_allow_html=True)
                
                # 통합 보고서 다운로드
                file_name = f"통합분석보고서_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                st.download_button(
                    label="📥 통합 보고서 다운로드 (.txt)",
                    data=report,
                    file_name=file_name,
                    mime="text/plain"
                )
                
                # 뒤로 가기 버튼
                if st.button("🔙 뒤로 가기 (새 기사 분석)"):
                    st.rerun()
                
                # 개별 기사 원문 댓글 확인 탭
                st.markdown("---")
                st.markdown("### 💬 기사별 원문 댓글")
                tabs = st.tabs([f"기사 {i+1}" for i in range(len(all_articles_data))])
                for i, data in enumerate(all_articles_data):
                    with tabs[i]:
                        info = data['info']
                        df = data['df']
                        st.write(f"**({info.get('site_display')}) {info.get('title')}**")
                        st.write(f"수집된 댓글: {len(df)}개")
                        for _, row in df.iterrows():
                            st.markdown(f"""
                            <div class="comment-list">
                                <strong>{row['author']}</strong> (👍 {row['like_count']})<br>
                                {row['content']}
                            </div>
                            """, unsafe_allow_html=True)

st.caption("본 시스템은 실제 뉴스 데이터를 크롤링하고 Google Gemini AI를 통해 심층 분석한 결과입니다.")
