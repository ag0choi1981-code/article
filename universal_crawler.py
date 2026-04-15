import requests
from bs4 import BeautifulSoup
import json
import time
import random
import re
from urllib.parse import urlparse, urljoin, parse_qs
from datetime import datetime

class UniversalNewsCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 언론사별 설정
        self.news_sites = {
            'naver': {
                'domain': 'news.naver.com',
                'title_selector': ['h2.media_end_head_headline', 'h3.tit_view', 'h1#articleTitle'],
                'content_selector': ['div.newsct_article', 'div#articleBodyContents'],
                'comment_api': self._get_naver_comments
            },
            'chosun': {
                'domain': 'chosun.com',
                'title_selector': ['h1.news-title', 'h1.article-head-title', 'h1.title'],
                'content_selector': ['div.article-body', 'div.news-body', 'div#news_body_id'],
                'comment_api': None
            },
            'kyunghyang': {
                'domain': 'kyunghyang.com',
                'title_selector': ['h1.title', 'h1.article-title', 'h2.headline'],
                'content_selector': ['div.article-body', 'div.news-content', 'div.article-content'],
                'comment_api': None
            },
            'joongang': {
                'domain': 'joongang.joins.com',
                'title_selector': ['h1.headline', 'h1.article-title', 'h2.title'],
                'content_selector': ['div.article-body', 'div#article_body', 'div.content'],
                'comment_api': None
            },
            'hankyung': {
                'domain': 'hankyung.com',
                'title_selector': ['h1.title', 'h1.article-title', 'h2.headline'],
                'content_selector': ['div.article-body', 'div.news-content', 'div.article-content'],
                'comment_api': None
            },
            'donga': {
                'domain': 'donga.com',
                'title_selector': ['h1.title', 'h1.article-title', 'h2.headline'],
                'content_selector': ['div.article-body', 'div#articleBody', 'div.content'],
                'comment_api': None
            },
            'munhwa': {
                'domain': 'munhwa.com',
                'title_selector': ['h1.title', 'h1.article-title', 'h2.headline'],
                'content_selector': ['div.article-body', 'div#articleBody', 'div.content'],
                'comment_api': None
            },
            'seoul': {
                'domain': 'seoul.co.kr',
                'title_selector': ['h1.title', 'h1.article-title', 'h2.headline'],
                'content_selector': ['div.article-body', 'div#articleBody', 'div.content'],
                'comment_api': None
            },
            'yonhap': {
                'domain': ['yna.co.kr', 'yonhapnews.com'],
                'title_selector': ['h1.title', 'h1.article-title', 'h2.headline', 'h1.tit-article'],
                'content_selector': ['div.article-body', 'div.news-content', 'div.article-txt', 'div.contribute'],
                'comment_api': None
            },
            'kookmin': {
                'domain': 'kookminilbo.com',
                'title_selector': ['h1.title', 'h1.article-title', 'h2.headline'],
                'content_selector': ['div.article-body', 'div.news-content', 'div.article-content'],
                'comment_api': None
            },
            'segye': {
                'domain': 'segye.com',
                'title_selector': ['h1.title', 'h1.article-title', 'h2.headline'],
                'content_selector': ['div.article-body', 'div.news-content', 'div.article-content'],
                'comment_api': None
            },
            'asiatoday': {
                'domain': 'asiatoday.co.kr',
                'title_selector': ['h1.title', 'h1.article-title', 'h2.headline'],
                'content_selector': ['div.article-body', 'div.news-content', 'div.article-content'],
                'comment_api': None
            },
            'hani': {
                'domain': ['hani.co.kr', 'hankyung.com'],
                'title_selector': ['h1.title', 'h1.article-title', 'h2.headline', 'h4.title'],
                'content_selector': ['div.article-body', 'div.news-content', 'div.article-text', 'div.text'],
                'comment_api': None
            },
            'etoday': {
                'domain': 'etoday.co.kr',
                'title_selector': ['h1.title', 'h1.article-title', 'h2.headline'],
                'content_selector': ['div.article-body', 'div.news-content', 'div.article-content'],
                'comment_api': None
            },
            'newstomato': {
                'domain': 'newstomato.com',
                'title_selector': ['h1.title', 'h1.article-title', 'h2.headline'],
                'content_selector': ['div.article-body', 'div.news-content', 'div.article-content'],
                'comment_api': None
            },
            'moneytoday': {
                'domain': 'moneytoday.co.kr',
                'title_selector': ['h1.title', 'h1.article-title', 'h2.headline'],
                'content_selector': ['div.article-body', 'div.news-content', 'div.article-content'],
                'comment_api': None
            },
            'bridgeeconomy': {
                'domain': 'bridgeeconomy.com',
                'title_selector': ['h1.title', 'h1.article-title', 'h2.headline'],
                'content_selector': ['div.article-body', 'div.news-content', 'div.article-content'],
                'comment_api': None
            },
            'seouleconomy': {
                'domain': ['seouleconomy.com', 'sedaily.com'],
                'title_selector': ['h1.title', 'h1.article-title', 'h2.headline'],
                'content_selector': ['div.article-body', 'div.news-content', 'div.article-content'],
                'comment_api': None
            },
            'edaily': {
                'domain': 'edaily.co.kr',
                'title_selector': ['h1.title', 'h1.article-title', 'h2.headline'],
                'content_selector': ['div.article-body', 'div.news-content', 'div.article-content'],
                'comment_api': None
            },
            'financialnews': {
                'domain': 'fnnews.com',
                'title_selector': ['h1.title', 'h1.article-title', 'h2.headline'],
                'content_selector': ['div.article-body', 'div.news-content', 'div.article-content'],
                'comment_api': None
            },
            'electronic': {
                'domain': 'electotimes.com',
                'title_selector': ['h1.title', 'h1.article-title', 'h2.headline'],
                'content_selector': ['div.article-body', 'div.news-content', 'div.article-content'],
                'comment_api': None
            }
        }
    
    def detect_news_site(self, url):
        """URL에서 언론사 감지"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        for site_name, site_config in self.news_sites.items():
            site_domains = site_config['domain']
            if isinstance(site_domains, list):
                for site_domain in site_domains:
                    if site_domain in domain:
                        return site_name, site_config
            elif site_domains in domain:
                return site_name, site_config
        
        return 'unknown', None
    
    def get_news_info(self, url):
        """기사 제목과 내용 가져오기"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 언론사 감지
            site_name, site_config = self.detect_news_site(url)
            
            # 제목 추출
            title = self._extract_title(soup, site_config)
            
            # 내용 추출
            content = self._extract_content(soup, site_config)

            # 조회수 및 댓글수 추출 (네이버 뉴스 특화)
            view_count = "정보없음"
            comment_count = "정보없음"
            
            if site_name == 'naver':
                # 언론사명 추출 (예: 동아일보)
                press_elem = soup.select_one('.media_end_head_top_logo img')
                if press_elem:
                    press_name = press_elem.get('alt', '정보없음')
                else:
                    press_elem = soup.select_one('.media_end_head_top_logo_text')
                    press_name = press_elem.get_text().strip() if press_elem else "네이버뉴스"
                
                # 조회수
                view_elem = soup.select_one('.media_end_head_view_count_number')
                if view_elem:
                    view_count = view_elem.get_text().strip()
                
                # 댓글수 (다양한 선택자 시도 및 API 응답 기반 추적)
                comment_count_selectors = [
                    '.media_end_head_comment_count_number',
                    '#comment_count',
                    '.u_cbox_count',
                    'span.count',
                    '.media_end_head_comment_count_number'
                ]
                comment_count = "정보없음"
                for selector in comment_count_selectors:
                    comment_elem = soup.select_one(selector)
                    if comment_elem and comment_elem.get_text().strip():
                        comment_count = comment_elem.get_text().strip()
                        # 숫자만 남기기 (예: "댓글 229" -> "229")
                        comment_count = re.sub(r'[^0-9]', '', comment_count)
                        if comment_count:
                            break
                
                # 만약 HTML에서 찾지 못했다면 API 응답에서 실제 댓글 수로 대체
                if comment_count == "정보없음" or not comment_count:
                    # 이 기사의 댓글 수를 API로 직접 확인 (예외 처리)
                    try:
                        # 먼저 댓글 API의 첫 페이지를 요청하여 총 댓글 수 확인
                        comment_url = f"https://comment.news.naver.com/comment/list.naver"
                        params = {
                            'serviceId': 'news',
                            'articleId': article_id,
                            'sort': 'FAVORITE',
                            'page': 1,
                            'pageSize': 100
                        }
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                            'Referer': pc_url
                        }
                        response = requests.get(comment_url, params=params, headers=headers, timeout=10)
                        if response.status_code == 200:
                            # JSONP 응답에서 총 댓글 수 추출 시도
                            import json
                            text = response.text
                            if '_callback(' in text:
                                json_str = text.split('_callback(')[1].rstrip(');')
                                data = json.loads(json_str)
                                if 'result' in data and 'count' in data['result']:
                                    comment_count = str(data['result']['count']['total'])
                        
                        # 위 방법이 안되면 실제 댓글을 가져와서 개수 확인
                        if comment_count == "정보없음" or not comment_count:
                            api_comments = self._get_naver_comments(pc_url, 1)  # 1개만 요청하여 확인
                            if api_comments:
                                # 실제 댓글 수를 API 응답의 총 개수로 설정
                                comment_count = str(len(api_comments))
                    except:
                        pass

            return {
                'title': title,
                'content': content,
                'site': site_name,
                'site_display': press_name if site_name == 'naver' else (site_config.get('domain', '알수없음') if site_config else '알수없음'),
                'url': url,
                'view_count': view_count,
                'comment_count': comment_count if comment_count else "정보없음"
            }
            
        except Exception as e:
            print(f"기사 정보 가져오기 오류: {e}")
            return None
    
    def _extract_title(self, soup, site_config):
        """제목 추출"""
        if site_config and 'title_selector' in site_config:
            for selector in site_config['title_selector']:
                title_element = soup.select_one(selector)
                if title_element:
                    return title_element.get_text().strip()
        
        # 일반적인 제목 선택자
        title_selectors = [
            'h1', 'h2.title', 'h1.title', 'h1.article-title',
            'h1.headline', 'title', 'meta[property="og:title"]'
        ]
        
        for selector in title_selectors:
            title_element = soup.select_one(selector)
            if title_element:
                title = title_element.get_text().strip() if title_element.name != 'meta' else title_element.get('content', '')
                if title:
                    return title
        
        return "제목 없음"
    
    def _extract_content(self, soup, site_config):
        """내용 추출"""
        if site_config and 'content_selector' in site_config:
            for selector in site_config['content_selector']:
                content_element = soup.select_one(selector)
                if content_element:
                    return self._clean_content(content_element)
        
        # 일반적인 내용 선택자
        content_selectors = [
            'div.article-body', 'div.news-body', 'div#articleBody',
            'div#article_body', 'div.content', 'div.article-content',
            'div.news-content', 'article', 'main'
        ]
        
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                return self._clean_content(content_element)
        
        # 모든 p 태그에서 내용 추출
        paragraphs = soup.find_all('p')
        if paragraphs:
            return '\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        
        return "내용 없음"
    
    def _clean_content(self, element):
        """내용 정제"""
        # 불필요한 태그 제거
        for tag in element.find_all(['script', 'style', 'aside', 'nav', 'footer', 'header', 'ad']):
            tag.decompose()
        
        content = element.get_text().strip()
        
        # 다중 공백 제거
        content = re.sub(r'\s+', ' ', content)
        
        return content
    
    def get_comments(self, url, max_comments=100):
        """댓글 가져오기"""
        site_name, site_config = self.detect_news_site(url)
        
        if site_name == 'naver':
            return self._get_naver_comments(url, max_comments)
        else:
            # 다른 언론사들은 일반적인 방법으로 시도
            return self._get_general_comments(url, max_comments)
    
    def _get_naver_comments(self, url, max_comments=10000):
        """네이버 뉴스 댓글 가져오기 (모바일/PC 모두 지원, 모든 댓글 수집 가능)"""
        try:
            # 모바일 URL을 PC URL로 변환
            pc_url = self._convert_naver_mobile_to_pc(url)
            
            parsed_url = urlparse(pc_url)
            path_parts = parsed_url.path.split('/')
            
                # 네이버 뉴스 URL 형식 확인
            office_id = None
            article_id = None
            
            # 1. n.news.naver.com 형식 (모바일 및 최신 공유용)
            if 'n.news.naver.com' in pc_url:
                query_params = parse_qs(parsed_url.query)
                # 기사 ID가 경로에 있는 경우: /mnews/article/001/0015951775
                if '/mnews/article/' in parsed_url.path:
                    path_parts = parsed_url.path.split('/')
                    # /mnews/article/{oid}/{aid}
                    if len(path_parts) >= 4:
                        office_id = path_parts[path_parts.index('article') + 1]
                        article_id = path_parts[path_parts.index('article') + 2]
                # 댓글 페이지인 경우: /mnews/article/comment/001/0015951775
                elif '/comment/' in parsed_url.path:
                    path_parts = parsed_url.path.split('/')
                    if len(path_parts) >= 5:
                        office_id = path_parts[path_parts.index('comment') + 1]
                        article_id = path_parts[path_parts.index('comment') + 2]

            # 2. news.naver.com 형식 (PC)
            elif 'news.naver.com' in pc_url:
                query_params = parse_qs(parsed_url.query)
                office_id = query_params.get('oid', [None])[0]
                article_id = query_params.get('aid', [None])[0]
                
                # 경로에 포함된 경우 (드문 경우)
                if not office_id and len(path_parts) >= 4:
                    office_id = path_parts[2]
                    article_id = path_parts[3]
            
            if not office_id or not article_id:
                print(f"네이버 뉴스 ID 추출 실패: {pc_url}")
                return []
            
            comments = []
            page = 1
            
            # 모든 댓글을 가져오기 위해 정렬 방식을 바꿔가며 수집 시도 가능 (현재는 공감순 우선)
            sort_types = ['FAVORITE', 'NEW'] # 공감순 수집 후 최신순으로 보강
            
            for sort_type in sort_types:
                page = 1
                while len(comments) < max_comments:
                    comment_url = f"https://apis.naver.com/commentBox/cbox/web_neo_list_jsonp.json"
                    
                    params = {
                        'ticket': 'news',
                        'templateId': 'default_society',
                        'pool': 'cbox5',
                        'lang': 'ko',
                        'country': 'KR',
                        'objectId': f'news{office_id},{article_id}',
                        'pageSize': 100, # 한 번에 더 많이 가져옴
                        'indexSize': 10,
                        'groupId': '',
                        'listType': 'OBJECT',
                        'page': page,
                        'refresh': 'false',
                        'sort': sort_type
                    }
                    
                    # 개선된 헤더 설정
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': '*/*',
                        'Referer': pc_url
                    }
                    
                    response = requests.get(comment_url, params=params, headers=headers, timeout=15)
                    if response.status_code != 200: break
                        
                    content = response.text
                    json_str = None
                    if content.startswith('_callback(') and content.endswith(');'): json_str = content[10:-2]
                    elif content.startswith('_callback(') and content.endswith(')'): json_str = content[10:-1]
                    elif content.startswith('{') and content.endswith('}'): json_str = content
                    
                    if not json_str: break
                        
                    try:
                        data = json.loads(json_str)
                        if 'result' not in data or 'commentList' not in data['result']: break
                            
                        comment_list = data['result']['commentList']
                        if not comment_list: break
                            
                        for comment in comment_list:
                            comment_content = comment.get('contents', '').strip()
                            if comment_content:
                                # 중복 체크 (정렬 방식을 바꿔 수집하므로)
                                exists = any(c['content'] == comment_content for c in comments)
                                if not exists:
                                    comments.append({
                                        'content': comment_content,
                                        'author': comment.get('userNickName', '익명'),
                                        'like_count': comment.get('sympathyCount', 0),
                                        'reg_time': comment.get('modTime', ''),
                                        'site': 'naver'
                                    })
                        
                        if len(comment_list) < 100: break
                        page += 1
                        time.sleep(random.uniform(0.1, 0.3)) # 속도 최적화
                        
                    except: break
                
                # 공감순으로 이미 충분히 가져왔다면 종료 (너무 오래 걸릴 수 있음)
                if len(comments) >= 500: break 

            return comments[:max_comments]
            
        except Exception as e:
            print(f"네이버 댓글 가져오기 오류: {e}")
            return []
    
    def _convert_naver_mobile_to_pc(self, url):
        """네이버 모바일 URL을 PC URL로 변환"""
        # 모바일 URL: https://n.news.naver.com/mnews/article/001/0015951775
        # PC URL: https://news.naver.com/main/read.naver?mode=LSD&mid=shm&sid1=102&oid=001&aid=0015951775
        # 댓글 URL: https://n.news.naver.com/mnews/article/comment/001/0015950393
        
        if 'n.news.naver.com' in url:
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.split('/')
            
            # /mnews/article/001/0015951775 형식 또는 /mnews/article/comment/001/0015950393 형식
            if len(path_parts) >= 4 and path_parts[1] == 'mnews' and path_parts[2] == 'article':
                if path_parts[3] == 'comment':
                    # 댓글 URL: /mnews/article/comment/001/0015950393
                    if len(path_parts) >= 5:
                        office_id = path_parts[4]
                        article_id = path_parts[5] if len(path_parts) > 5 else path_parts[4]
                else:
                    # 일반 기사 URL: /mnews/article/001/0015951775
                    office_id = path_parts[3]
                    article_id = path_parts[4]
                
                # PC URL로 변환
                pc_url = f"https://news.naver.com/main/read.naver?mode=LSD&mid=shm&sid1=102&oid={office_id}&aid={article_id}"
                print(f"모바일 URL을 PC URL로 변환: {url} -> {pc_url}")
                return pc_url
        
        return url
    
    def _get_general_comments(self, url, max_comments=100):
        """다른 언론사 댓글 가져오기 (개선된 방법)"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            comments = []
            
            # 언론사별 댓글 선택자 확장
            comment_selectors = [
                # 조선일보
                'div.comment-item', 'li.comment', 'div.reply-item',
                'div.comment-content', 'article.comment', 'div.comment-body',
                'div[id*="comment"]', 'div[class*="comment"]',
                'li[id*="comment"]', 'li[class*="comment"]',
                # 경향신문
                'div.comment_list', 'div.comment-text', 'div.comment-wrap',
                # 중앙일보
                'div.comment-box', 'div.comment-row', 'div.cmt-item',
                # 일반적인 선택자
                'div.comment', 'li.comment', 'div.reply', 'article.comment'
            ]
            
            for selector in comment_selectors:
                comment_elements = soup.select(selector)
                if comment_elements:
                    for element in comment_elements[:max_comments]:
                        # 여러 방법으로 댓글 내용 추출 시도
                        content = None
                        
                        # 직접 텍스트
                        if element.get_text().strip():
                            content = element.get_text().strip()
                        
                        # 자식 요소에서 텍스트 찾기
                        if not content or len(content) < 10:
                            text_elements = element.find_all(text=True)
                            content = ' '.join([text.strip() for text in text_elements if text.strip()])
                        
                        # 특정 클래스에서 찾기
                        if not content or len(content) < 10:
                            for child in element.find_all():
                                if child.name in ['p', 'span', 'div'] and child.get_text().strip():
                                    content = child.get_text().strip()
                                    break
                        
                        # 의미 있는 댓글만 필터링
                        if content and len(content) > 10 and not self._is_menu_text(content):
                            comments.append({
                                'content': content,
                                'author': self._extract_author(element),
                                'like_count': self._extract_likes(element),
                                'reg_time': '',
                                'site': self.detect_news_site(url)[0]
                            })
                    
                    if comments:  # 댓글을 찾았으면 중단
                        break
            
            # 만약 댓글을 찾지 못했다면, 페이지에서 대화 형태의 텍스트 찾기
            if not comments:
                comments = self._extract_conversation_like_text(soup, url, max_comments)
            
            return comments[:max_comments]
            
        except Exception as e:
            print(f"일반 댓글 가져오기 오류: {e}")
            return []
    
    def _is_menu_text(self, text):
        """메뉴나 버튼 텍스트인지 확인"""
        menu_texts = [
            '댓글', '답글', '삭제', '수정', '신고', '추천', '공유', '더보기', '닫기',
            '등록', '취소', '확인', '로그인', '회원가입', '페이스북', '카카오', '네이버',
            'google', 'facebook', 'kakao', 'naver', 'twitter'
        ]
        
        text_lower = text.lower().strip()
        return any(menu in text_lower for menu in menu_texts) or len(text.strip()) < 5
    
    def _extract_author(self, element):
        """작성자 이름 추출"""
        author_selectors = [
            '.author', '.name', '.user', '.writer', '.nickname',
            '[class*="author"]', '[class*="name"]', '[class*="user"]',
            '[class*="writer"]', '[class*="nick"]'
        ]
        
        for selector in author_selectors:
            author_element = element.select_one(selector)
            if author_element:
                author = author_element.get_text().strip()
                if author and len(author) < 20:  # 합리적인 이름 길이
                    return author
        
        return '익명'
    
    def _extract_likes(self, element):
        """좋아요 수 추출"""
        like_selectors = [
            '.like', '.recommend', '.good', '.thumb', '.up',
            '[class*="like"]', '[class*="recommend"]', '[class*="good"]',
            '[class*="thumb"]', '[class*="up"]'
        ]
        
        for selector in like_selectors:
            like_element = element.select_one(selector)
            if like_element:
                like_text = like_element.get_text().strip()
                # 숫자만 추출
                import re
                numbers = re.findall(r'\d+', like_text)
                if numbers:
                    return int(numbers[0])
        
        return 0
    
    def _extract_conversation_like_text(self, soup, url, max_comments=100):
        """페이지에서 대화 형태의 텍스트 추출 (fallback)"""
        comments = []
        
        # 문단 단위로 텍스트 추출
        paragraphs = soup.find_all(['p', 'div'])
        
        for p in paragraphs:
            text = p.get_text().strip()
            
            # 대화 형태의 텍스트인지 확인 (길이가 길고, 의미 있는 내용)
            if (len(text) > 20 and 
                len(text) < 500 and 
                not self._is_menu_text(text) and
                any(char in text for char in ['다', '요', '죠', '네', '어', '아'])):
                
                comments.append({
                    'content': text,
                    'author': '익명',
                    'like_count': 0,
                    'reg_time': '',
                    'site': self.detect_news_site(url)[0]
                })
                
                if len(comments) >= max_comments:
                    break
        
        return comments

# 레거시 호환성을 위한 함수들
def get_naver_news_comments(news_url, max_comments=100):
    """기존 호환성을 위한 함수"""
    crawler = UniversalNewsCrawler()
    return crawler.get_comments(news_url, max_comments)

def get_news_title_and_content(news_url):
    """기존 호환성을 위한 함수"""
    crawler = UniversalNewsCrawler()
    info = crawler.get_news_info(news_url)
    if info:
        return info['title'], info['content']
    return None, None
