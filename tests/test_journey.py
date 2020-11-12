
from nondeterministic.interpreter import Interpreter

LANDMARKS = {
    'Kyoto': ['tower', 'shrine', 'temple', 'moutain', 'museum'],
    'Shiga': ['lake', 'mountain', 'castle'],
    'Mie':   ['shrine', 'sea', 'circuit'],
    'Aichi': ['castle', 'building', 'sea', 'monkey', 'museum'],
    'Hyogo': ['castle', 'mountain', 'tower', 'onsen'],
    'Osaka': ['building', 'tower', 'museum', 'castle'],
    'Nara':  ['temple', 'mountain', 'museum'],
    'Wakayama': ['sea', 'shrine', 'moutain', 'onsen'],
    'Fukui': ['museum', 'sea', 'temple', 'onsen'],
    'Gifu':  ['onsen', 'building', 'mountain']
}

PATHS = {
    'Kyoto': ['Osaka', 'Hyogo', 'Nara', 'Shiga', 'Fukui'],
    'Shiga': ['Fukui', 'Gifu', 'Mie', 'Kyoto'],
    'Mie':   ['Wakayama', 'Nara', 'Shiga', 'Gifu', 'Aichi'],
    'Aichi': ['Gifu', 'Mie'],
    'Hyogo': ['Kyoto', 'Osaka'],
    'Osaka': ['Hyogo', 'Kyoto', 'Nara', 'Wakayama'],
    'Nara':  ['Kyoto', 'Osaka', 'Wakayama', 'Mie'],
    'Wakayama': ['Osaka', 'Nara', 'Mie'],
    'Fukui': ['Kyoto', 'Shiga', 'Gifu'],
    'Gifu':  ['Fukui', 'Shiga', 'Mie', 'Aichi']
}


def is_location_match(description, location):
    verb, obj = description.split()
    if verb == 'arrived_in':
        if obj == location:
            return True
        return False
    if verb == 'saw':
        if obj in LANDMARKS[location]:
            return True
        return False
    raise RuntimeError('{} is nonsence!'.format(description))


def guess(history, description):
    try:
        return [
            history + [p] for p in PATHS[history[-1]]
            if is_location_match(description, p)
            if p not in history
        ]
    except (RuntimeError, ValueError, KeyError):
        return [history] # skip this nonsence line


def test_find_journey():
    start = 'Kyoto'
    diary = [
        'saw mountain',
        'saw temple',
        'saw building',
        'drink a lot',
        'saw castle',
        'saw shrine',
        'saw onsen',
        'saw temple',
        'saw tower',
        'arrived_in Hyogo'
    ]
    it = Interpreter(guess, [start])
    for sentence in diary:
        it.interpret(sentence)
    journey = list(it)
    assert journey == [
        ['Kyoto', 'Shiga', 'Fukui', 'Gifu',
         'Aichi', 'Mie', 'Wakayama', 'Nara',
         'Osaka', 'Hyogo']
    ]
