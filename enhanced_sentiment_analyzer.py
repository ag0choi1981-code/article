import re
from collections import Counter
from typing import List, Dict, Tuple

class EnhancedSentimentAnalyzer:
    """개선된 감성 분석기"""
    
    def __init__(self):
        # 긍정 단어 사전 (확장)
        self.positive_words = [
            # 기본 긍정 표현
            '좋다', '훌륭하다', '멋지다', '대단하다', '최고', '짱', '굿', '훌륭', '최상', '완벽',
            '기쁘다', '즐겁다', '행복하다', '반갑다', '환영하다', '만족', '만족스럽다', '감사', '고맙다',
            '성공', '승리', '희망', '긍정', '지지', '찬성', '추천', '칭찬', '인정', '인정하다',
            
            # 강한 긍정 표현
            '대박', '최고다', '킹', '갓', '엄지', '존경', '감탄', '환상적', '완벽하다', '탁월하다',
            '뛰어나다', '훌륭합니다', '최고입니다', '감사합니다', '멋집니다', '대단합니다',
            
            # 동의/옹호 표현
            '맞다', '맞습니다', '동의', '찬성합니다', '옳다', '옳습니다', '그렇다', '그렇습니다',
            '맞아요', '맞습니다', '옹호', '지지합니다', '밀어준다', '응원', '힘내다', '응원합니다',
            
            # 긍정적 평가
            '유용', '도움', '필요', '좋은', '훌륭한', '멋진', '대단한', '환상적인', '탁월한',
            '잘했다', '잘하다', '잘됐다', '잘되다', '성과', '성과있다', '효과적', '효과 있다',
            
            # 영어 긍정 표현
            'good', 'great', 'best', 'excellent', 'nice', 'perfect', 'awesome', 'amazing',
            'wonderful', 'fantastic', 'love', 'like', 'recommend', 'support', 'agree',
            
            # 기타 긍정 표현
            '기대', '희망', '낫다', '더 낫다', '좋아지다', '발전', '개선', '향상', '성장',
            '밝다', '희망적', '긍정적', '긍정적이다', '긍정입니다', '좋은 방향', '좋은 결과'
        ]
        
        # 부정 단어 사전 (확장)
        self.negative_words = [
            # 기본 부정 표현
            '나쁘다', '최악', '별로', '실망', '화나다', '속상하다', '슬프다', '불행하다', '안타깝다',
            '문제', '오류', '실패', '패배', '위기', '부정', '반대', '거절', '거부', '비판',
            '불만', '불평', '불만족', '후회', '미안', '죄송', '죄송합니다', '미안합니다',
            
            # 강한 부정 표현
            '최악이다', '최악입니다', '망했다', '망했습니다', '엉망', '엉망이다', '쓰레기', '바보',
            '미친', '미쳤다', '정신나가다', '정신나갔다', '어이없다', '어이없습니다', '한심하다',
            
            # 반대/비판 표현
            '아니다', '아닙니다', '틀리다', '틀렸다', '틀립니다', '틀렸습니다', '아니요', '아닙니다',
            '반대', '반대합니다', '반대다', '반대입니다', '틀렸어', '틀렸어요', '말도 안된다',
            '말도 안됩니다', '이상하다', '이상합니다', '이해 안된다', '이해 안됩니다',
            
            # 부정적 평가
            '나쁜', '최악의', '실망스러운', '안좋은', '문제의', '위험한', '해로운', '유해한',
            '손해', '피해', '손실', '감소', '축소', '퇴보', '후퇴', '악화', '나빠지다',
            
            # 영어 부정 표현
            'bad', 'worst', 'terrible', 'awful', 'horrible', 'disgusting', 'hate', 'dislike',
            'reject', 'refuse', 'oppose', 'disagree', 'wrong', 'fail', 'problem', 'error',
            
            # 불만/불평 표현
            '불편', '불편하다', '힘들다', '어렵다', '어렵습니다', '힘듭니다', '괴롭다', '괴롭습니다',
            '짜증', '짜증나다', '짜증납니다', '화', '화나다', '화납니다', '분노', '분노하다',
            '억울하다', '억울합니다', '억울', '부당하다', '부당합니다', '부당', '불공정',
            
            # 기타 부정 표현
            '위험', '위험하다', '위험합니다', '걱정', '걱정된다', '걱정됩니다', '두렵다', '두렵습니다',
            '무섭다', '무섭습니다', '무서워', '무서워요', '불안', '불안하다', '불안합니다'
        ]
        
        # 비판 관련 키워드
        self.criticism_keywords = [
            '비판', '문제', '실수', '오류', '잘못', '틀렸', '반대', '아니다', '아니', '아닙니다',
            '이상', '이해안', '말도안', '어이없', '한심', '최악', '별로', '불만', '불평',
            '화', '짜증', '속상', '실망', '걱정', '위험', '문제점', '단점', '약점', '결함',
            '틀렸다', '틀렸어', '틀렸습니다', '아니다', '아닌데', '아닌가', '아닌게',
            '반대한다', '반대입니다', '동의안', '찬성안', '틀렸어요', '아니요'
        ]
        
        # 옹호 관련 키워드
        self.support_keywords = [
            '옹호', '지지', '찬성', '동의', '맞다', '맞아', '맞습니다', '옳다', '옳아', '옳습니다',
            '좋다', '훌륭', '최고', '대단', '멋지다', '잘한다', '잘됐다', '성공', '추천',
            '칭찬', '인정', '긍정', '응원', '힘내', '밀어', '도와', '도움', '필요',
            '기대', '희망', '낫다', '좋아', '맞아요', '맞습니다', '옳아요', '옳습니다',
            '지지한다', '지지합니다', '동의한다', '동의합니다', '찬성한다', '찬성합니다'
        ]
    
    def preprocess_text(self, text: str) -> str:
        """텍스트 전처리"""
        # 특수문자 제거 (한글, 영어, 숫자, 공백만 남기기)
        text = re.sub(r'[^\w\s\uac00-\ud7af]', ' ', text)
        # 숫자 제거
        text = re.sub(r'\d+', '', text)
        # 여러 공백을 하나로
        text = re.sub(r'\s+', ' ', text)
        return text.strip().lower()
    
    def calculate_sentiment_score(self, text: str) -> Tuple[float, float]:
        """감성 점수 계산"""
        processed_text = self.preprocess_text(text)
        words = processed_text.split()
        
        positive_score = 0
        negative_score = 0
        
        for word in words:
            if word in self.positive_words:
                positive_score += 1
            elif word in self.negative_words:
                negative_score += 1
        
        return positive_score, negative_score
    
    def classify_reaction(self, text: str) -> str:
        """반응 분류 (비판/옹호/기타)"""
        processed_text = self.preprocess_text(text)
        
        # 비판 키워드 카운트
        criticism_count = sum(1 for keyword in self.criticism_keywords if keyword in processed_text)
        
        # 옹호 키워드 카운트
        support_count = sum(1 for keyword in self.support_keywords if keyword in processed_text)
        
        # 긍정/부정 단어 카운트
        positive_count = sum(1 for word in processed_text.split() if word in self.positive_words)
        negative_count = sum(1 for word in processed_text.split() if word in self.negative_words)
        
        # 총 점수 계산
        total_criticism = criticism_count + negative_count
        total_support = support_count + positive_count
        
        # 분류 결정
        if total_criticism > total_support and total_criticism > 0:
            return '비판'
        elif total_support > total_criticism and total_support > 0:
            return '옹호'
        else:
            return '기타'
    
    def predict_sentiment(self, text: str) -> Dict:
        """감성 예측"""
        positive_score, negative_score = self.calculate_sentiment_score(text)
        reaction_type = self.classify_reaction(text)
        
        # 신뢰도 계산
        total_score = positive_score + negative_score
        if total_score == 0:
            confidence = 0.1  # 아무 감성도 없을 때는 낮은 신뢰도
        else:
            confidence = max(positive_score, negative_score) / total_score
        
        # 감성 결정
        if positive_score > negative_score:
            sentiment = 'positive'
        elif negative_score > positive_score:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'reaction_type': reaction_type,  # 새로운 반응 타입
            'confidence': confidence,
            'positive_score': positive_score,
            'negative_score': negative_score
        }
    
    def analyze_comments(self, comments: List[str]) -> Dict:
        """댓글 목록 분석"""
        results = []
        
        for comment in comments:
            if isinstance(comment, dict):
                content = comment.get('content', '')
            else:
                content = str(comment)
            
            analysis = self.predict_sentiment(content)
            
            result = {
                'content': content,
                'sentiment': analysis['sentiment'],
                'reaction_type': analysis['reaction_type'],
                'confidence': analysis['confidence'],
                'positive_score': analysis['positive_score'],
                'negative_score': analysis['negative_score']
            }
            
            # 원본 댓글의 다른 정보도 복사
            if isinstance(comment, dict):
                for key, value in comment.items():
                    if key != 'content':
                        result[key] = value
            
            results.append(result)
        
        return results
