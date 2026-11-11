"""Correlate defensive event telemetry with supplied threat indicators."""
import json

from collections import defaultdict, deque
def analyze(data):
    threshold = data.get('failure_threshold', 3)
    window = data.get('window_seconds', 60)
    if threshold < 1 or window < 0:
        raise ValueError('Invalid detection thresholds')
    indicators = defaultdict(list)
    for indicator in data.get('indicators', []):
        if not 0 <= indicator['confidence'] <= 1:
            raise ValueError('Confidence must be between zero and one')
        indicators[indicator['value']].append(indicator)
    seen, queues, alerts = set(), defaultdict(deque), []
    for event in sorted(data.get('events', []), key=lambda e:(e['time'], e['id'])):
        if event['id'] in seen:
            continue
        seen.add(event['id'])
        active = [i for i in indicators[event['source']] if i['expires'] > event['time']]
        if active:
            alerts.append({'event':event['id'], 'rule':'indicator-match',
                           'score':round(max(i['confidence'] for i in active)*100),
                           'evidence':sorted(i['id'] for i in active)})
        if event['type'] == 'login-failed':
            queue = queues[(event['source'], event.get('account',''))]
            while queue and queue[0][0] < event['time'] - window:
                queue.popleft()
            queue.append((event['time'],event['id']))
            if len(queue) == threshold:
                alerts.append({'event':event['id'], 'rule':'failed-login-burst',
                               'score':70, 'evidence':[item[1] for item in queue]})
    return {'processed':len(seen), 'alerts':alerts}

if __name__ == '__main__':
    import argparse, sys
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='Path to a JSON scenario')
    args = parser.parse_args()
    try:
        with open(args.input, encoding='utf-8') as source:
            data = json.load(source)
        if not isinstance(data, dict):
            raise ValueError('Input must be a JSON object')
        print(json.dumps(analyze(data), indent=2, sort_keys=True))
    except (ValueError, TypeError, KeyError, OSError) as error:
        print('Input error: '+str(error), file=sys.stderr)
        sys.exit(2)
