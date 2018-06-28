import sys
import os.path
import re
import json

from urllib.request import Request, urlopen

urlBase='http://www.listademaestros.com/fime/maestro/'

def getUrl(url):
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0'}) 
    return urlopen(request).read().decode('utf-8')

def getMaestro(data):
    
    regex = r'n_r[\S\s]+<h1>\s*(\w+[\s\w\.]*)'
    
    match = re.search(regex, data)
    if not match: return None
    
    name = match.groups()[0]
    
    offsets = ['ex_li', 'ac_li', 'pa_li', 'as_li', 'se_li']

    regex = r'<li\s+id="#####">\s*(\d+(?:\.\d+)?)'
    index = regex.find('#')

    scores = []

    for i in offsets:
        regex = regex[:index] + i + regex[index + len(offsets[0]):]
        match = re.search(regex, data)
        if not match: return None
        
        scores.append(float(match.groups()[0]))
     
    offsets = ['Chido', 'Gacho']

    regex = r'#####:\s*<span>\s*(\d+)'
    index = regex.find('#')

    votes = []

    for i in offsets:
        regex = regex[:index] + i + regex[index + len(offsets[0]):]

        match = re.search(regex, data)
        if not match: return None
        
        votes.append(int(match.groups()[0])) 

    maestro = { 'name' : name, 'scores' : scores, 'votes' : votes }
    return maestro

def main():
    argc = len(sys.argv) 
    if argc < 2 or argc > 4:
        print('usage:', sys.argv[0], 'output_file [begin_range] [end_range]')
        exit(1)

    rng = [1, sys.maxsize]
    tolerance = 10
    
    if argc > 2:
        for i in range(2, argc):
            try: rng[i - 2] = int(sys.argv[i])
            except: 
                print('[info] invalid range')
                exit(1)

    if rng[0] > rng[1] or rng[0] < 1 or rng[1] < 1:
        print('[error] invalid range')
        exit(1)
    maestros = []
     
    tolCount = 0
    for i in range(rng[0], rng[1] + 1):
        try:
            if tolCount == tolerance: break
            url = urlBase + str(i)
            maestro = getMaestro(getUrl(url))
            if maestro:
                maestro["id"] = i
                maestros.append(maestro)
                tolCount = 0
            else: tolCount = tolCount + 1
            print(maestro)
            print('[info] done (', i, '/', rng[1], ')')
            print('[info] tolerance(max ', tolerance,'): ', tolCount, '\n', sep='') 
        except KeyboardInterrupt: break
        except Exception as e:
            print('[error]', e)
            continue
    if maestros:
        with open(sys.argv[1]+'.json', 'w') as f:
            json.dump(maestros, f)
    else: exit(1)

if __name__ == '__main__':
    main()