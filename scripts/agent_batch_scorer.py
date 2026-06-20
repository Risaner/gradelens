
import os
import sys
import json
from pathlib import Path
from collections import defaultdict

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from core.dataset import Dataset
from core.scorers import LLMScorer

def run():
    print('=' * 60)
    print('GradeLens Agent Batch Scorer')
    print('=' * 60)
    
    ds = Dataset('data')
    essays = ds.load_all()
    print('Loaded %d essays' % len(essays))
    
    scorer = LLMScorer()
    
    results = []
    for i, essay in enumerate(essays, 1):
        print('[%2d/%d] Scoring: %s (%s)' % (i, len(essays), essay.id, essay.title[:30]))
        try:
            result = scorer.score(essay)
            result['id'] = essay.id
            result['title'] = essay.title
            result['category'] = essay.category
            result['difficulty'] = essay.difficulty
            result['strategy'] = essay.strategy
            results.append(result)
            print('       Score: %d' % result['overall'])
        except Exception as e:
            print('       Error: %s' % e)
            results.append({
                'id': essay.id,
                'title': essay.title,
                'category': essay.category,
                'difficulty': essay.difficulty,
                'strategy': essay.strategy,
                'overall': 0,
                'dimensions': {'language': 0, 'content': 0, 'structure': 0, 'technical': 0},
                'feedback': 'Error: %s' % str(e),
                'errors': [],
                'reasoning': 'Evaluation failed'
            })
    
    os.makedirs('data/results', exist_ok=True)
    output_file = 'data/results/agent_scores.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({'essays': results}, f, ensure_ascii=False, indent=2)
    
    print('Saved %d results to %s' % (len(results), output_file))
    
    if results:
        scores = [r.get('overall', 0) for r in results]
        print('Average score: %.1f' % (sum(scores)/len(scores)))
        print('Max: %d, Min: %d' % (max(scores), min(scores)))
        
        cat_scores = defaultdict(list)
        for r in results:
            cat_scores[r['category']].append(r['score'])
        print('By category:')
        for cat, cs in sorted(cat_scores.items()):
            print('  %s: %.1f (%d essays)' % (cat, sum(cs)/len(cs), len(cs)))

if __name__ == '__main__':
    run()
