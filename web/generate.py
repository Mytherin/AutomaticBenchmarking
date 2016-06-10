

import os
import sys
import random


tempname = random.randint(0, 1000000)
fname = 'htmloutput-%s' % tempname


res = open(fname, 'w+')

files = os.listdir('results');
files = sorted(files);

table_rows = []

prevResults = None
for f in files:
    inputfile = open(os.path.join('results', f), 'r')
    database = None
    date = None
    revision = None
    revisionlink = None
    benchmarks = {}
    current_benchmark = ''
    for line in inputfile:
        if 'database:' in line:
            database = line.split(':', 1)[1].strip()
        elif 'date:' in line:
            date = line.split(':', 1)[1].strip()
        elif 'revision:' in line:
            revision = line.split(':', 1)[1].strip()
        elif 'revisionlink:' in line:
            revisionlink = line.split(':', 1)[1].strip()
        elif 'startresultblock:' in line:
            current_benchmark = ''
        elif 'compileparameters:' in line:
            current_benchmark += line.split(':', 1)[1].strip()
        elif 'runtimeparameters:' in line:
            current_benchmark += " - " + line.split(':', 1)[1].strip()
        elif 'startresults:' in line:
            benchmarks[current_benchmark] = {'mean': {}, 'std': {}}
        elif '-mean:' in line:
            name = line.split('-mean')[0]
            result = float(line.split(':')[1].strip())
            benchmarks[current_benchmark]['mean'][name] = result
        elif '-std:' in line:
            name = line.split('-std')[0]
            result = float(line.split(':')[1].strip())
            benchmarks[current_benchmark]['std'][name] = result

    table_row = '<tr><td><input type="checkbox" name="comparison" value="%s"></td>\n' % revision
    table_row += '<td>%s</td>\n' % database
    table_row += '<td>%s</td>\n' % date
    table_row += '<td><a href="%s">%s</a></td>\n' % (revisionlink, revision)

    if prevResults == None:
        for key1 in benchmarks.keys():
            meandict = benchmarks[key1]['mean']
            for kv in sorted(meandict.keys()):
                table_row += '<td>%g</td>\n' % round(meandict[kv], 2)
            break
    else:
        for key in benchmarks.keys():
            if key not in prevResults: continue
            means1 = benchmarks[key]['mean']
            means2 = prevResults[key]['mean']
            std1 = benchmarks[key]['std']
            std2 = benchmarks[key]['std']
            for testkey in sorted(means1.keys()):
                testval = '<span class="node nochange">~</span>'
                if (means1[testkey] + 10 * std1[testkey]) < (means2[testkey] - 10 * std2[testkey]):
                    testval = '<span class="node better3">+++</span>'
                elif (means1[testkey] + 5 * std1[testkey]) < (means2[testkey] - 5 * std2[testkey]):
                    testval = '<span class="node better2">++</span>'
                elif (means1[testkey] + std1[testkey]) < (means2[testkey] - std2[testkey]):
                    testval = '<span class="node better">+</span>'
                elif (means2[testkey] + std2[testkey]) < (means1[testkey] - std1[testkey]):
                    testval = '<span class="node worse">x</span>'
                elif (means2[testkey] + 5 * std2[testkey]) < (means1[testkey] - 5 * std1[testkey]):
                    testval = '<span class="node worse2">xx</span>'
                elif (means2[testkey] + 10 * std2[testkey]) < (means1[testkey] - 10 * std1[testkey]):
                    testval = '<span class="node worse3">xxx</span>'
                table_row += '<td>%s</td>\n' % testval
            break

    table_row += '</tr>'

    table_rows.append(table_row)

    prevResults = benchmarks

table_rows.reverse()
for row in table_rows:
    res.write(row)

res.close()

os.rename(fname, 'htmloutput')