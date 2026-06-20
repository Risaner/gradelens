import requests
from core.base import Scorer, Essay
from typing import Dict, List

class PigaiScorer(Scorer):
    BASE_URL = 'http://api.pigai.org'
    ENDPOINT = '/essays/rapid_experience'
    
    def __init__(self):
        super().__init__('PIGAI')
    
    def score(self, essay: Essay) -> Dict:
        url = f'{self.BASE_URL}{self.ENDPOINT}'
        payload = {
            'title': essay.title,
            'content': essay.content,
            'comcontext': 'AES-Bench Evaluation'
        }
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f'  [!] PIGAI API error: {e}')
            return self._fallback_result(essay)
        
        if 'score' not in data:
            print(f'  [!] PIGAI response format unexpected: {data}')
            return self._fallback_result(essay)
        
        return {
            'score': data['score'],
            'dimensions': self._map_dimensions(data.get('score_cat', {})),
            'feedback': data.get('total_feedback', ''),
            'errors': self._extract_errors(data),
        }
    
    def _map_dimensions(self, score_cat: Dict) -> Dict:
        language = score_cat.get('1', {}).get('score', 0) + score_cat.get('3', {}).get('score', 0) + score_cat.get('5', {}).get('score', 0)
        language = round(language / 15, 2) * 25
        
        content = score_cat.get('6', {}).get('score', 0) + score_cat.get('12', {}).get('score', 0)
        content = round(content / 10, 2) * 25
        
        structure = score_cat.get('11', {}).get('score', 0) + score_cat.get('12', {}).get('score', 0)
        structure = round(structure / 10, 2) * 25
        
        technical = score_cat.get('4', {}).get('score', 0) + score_cat.get('5', {}).get('score', 0) + score_cat.get('8', {}).get('score', 0) + score_cat.get('7', {}).get('score', 0)
        technical = round(technical / 20, 2) * 25
        
        return {
            'language': min(25, max(0, language)),
            'content': min(25, max(0, content)),
            'structure': min(25, max(0, structure)),
            'technical': min(25, max(0, technical)),
        }
    
    def _extract_errors(self, data: Dict) -> List[Dict]:
        errors = []
        for comment in data.get('sentence_comments', []):
            sentence = comment.get('original_sentence', '')
            if sentence and comment.get('comment') and comment['comment'] != 'OK':
                errors.append({
                    'sentence': sentence,
                    'error': comment.get('comment', ''),
                    'suggestion': comment.get('suggested_sentence', '')
                })
        return errors[:20]
    
    def _fallback_result(self, essay: Essay) -> Dict:
        return {
            'score': 0,
            'dimensions': {'language': 0, 'content': 0, 'structure': 0, 'technical': 0},
            'feedback': 'PIGAI API unavailable',
            'errors': []
        }