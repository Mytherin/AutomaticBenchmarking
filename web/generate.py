

import os
import sys
import random


files = os.listdir('results');
files = sorted(files);

global_branches = []

def generate_html_output(active_branch):
    global global_branches
    global files
    tempname = random.randint(0, 1000000)
    fname = 'htmloutput-%s' % tempname
    if active_branch != None:
        fname += active_branch

    res = open(fname, 'w+')

    table_rows = []
    test_count = 22

    data_results = dict()
    benchmark_results = dict()

    prevResults = None
    for f in files:
        if active_branch == None:
            splits = f.split('.')
            if len(splits) != 2:
                continue
            global_branches.append(splits[1])
        elif (active_branch + '.').strip().lower() not in f.strip().lower(): continue
        inputfile = open(os.path.join('results', f), 'r')
        database = None
        date = None
        branch = None
        revision = None
        revisionlink = None
        crash = None
        benchmarks = {}
        current_benchmark = ''

        for line in inputfile:
            if 'database:' in line:
                database = line.split(':', 1)[1].strip()
            elif 'date:' in line:
                date = line.split(':', 1)[1].strip()
            elif 'branch:' in line:
                branch = line.split(':', 1)[1].strip()
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
            elif '-fail:' in line:
                name = line.split('-fail')[0]
                benchmarks[current_benchmark]['mean'][name] = -1
                benchmarks[current_benchmark]['std'][name] = -1
            elif 'fail:' in line:
                crash = line.split(':')[1].strip()

        datafile = "http://monetdb.cwi.nl/testweb/web/chronos/results/%s" % f;
        branchlink = "http://monetdb.cwi.nl/testweb/web/chronos?branch=%s" % branch

        table_row = '<tr><td><input type="checkbox" name="comparison" value="%s"></td>\n' % f
        table_row += '<td>%s</td>\n' % database
        table_row += '<td>%s</td>\n' % date
        table_row += '<td><a href="%s">%s (<a href="%s">Data</a>)</a></td>\n' % (revisionlink, revision, datafile)

        data_list = [database, branch, branchlink, revisionlink, revision, datafile, f]
        data_results[branch] = data_list
        if crash != None:
            for i in range(test_count):
                table_row += '<td><span class="crash node">C</span></td>\n'
        else:
            if prevResults == None:
                for key1 in benchmarks.keys():
                    meandict = benchmarks[key1]['mean']
                    for kv in sorted(meandict.keys()):
                        if kv not in benchmark_results:
                            benchmark_results[kv] = dict()
                        if key1 not in benchmark_results[kv]:
                            benchmark_results[kv][key1] = dict()
                        benchmark_results[kv][key1][branch] = meandict[kv]
            else:
                results = dict()
                testkeys = None
                for key in benchmarks.keys():
                    if key not in prevResults: continue
                    means1 = benchmarks[key]['mean']
                    means2 = prevResults[key]['mean']
                    std1 = benchmarks[key]['std']
                    std2 = prevResults[key]['std']
                    testkeys = sorted(means1.keys())
                    for testkey in testkeys:
                        if testkey not in results:
                            results[testkey] = 0
                        current_value = results[testkey]
                        measured_value = results[testkey]

                        if means1[testkey] < 0:
                            # measurement smaller than 0 means crash
                            means1[testkey] = means2[testkey]
                            std1[testkey] = std2[testkey]
                            measured_value = "crash"
                        elif (means1[testkey] + std1[testkey]) * 1.5 < (means2[testkey] - std2[testkey]):
                            measured_value = 3
                        elif (means1[testkey] + std1[testkey]) * 1.2 < (means2[testkey] - std2[testkey]):
                            measured_value = 2
                        elif (means1[testkey] + std1[testkey]) * 1.05 < (means2[testkey] - std2[testkey]):
                            measured_value = 1
                        elif (means2[testkey] + std2[testkey]) * 1.05 < (means1[testkey] - std1[testkey]):
                            measured_value = -1
                        elif (means2[testkey] + std2[testkey]) * 1.2 < (means1[testkey] - std1[testkey]):
                            measured_value = -2
                        elif (means2[testkey] + std2[testkey]) * 1.5 < (means1[testkey] - std1[testkey]):
                            measured_value = -3

                        if current_value == "crash" or measured_value == "crash": 
                            results[testkey] = "crash"
                        elif measured_value < 0 and current_value <= 0 and measured_value < current_value:
                            results[testkey] = measured_value
                        elif measured_value > 0 and current_value >= 0 and measured_value > current_value:
                            results[testkey] = measured_value
                        elif measured_value < 0 and current_value > 0:
                            results[testkey] = "mixed"

                for key in testkeys:
                    testval = None
                    if results[key] == "crash":
                        testval = '<span class="node crash">C</span>'
                    elif results[key] == "mixed":
                        testval = '<span class="node mixed">?</span>'
                    elif results[key] == 0:
                        testval = '<span class="node nochange">~</span>'
                    elif results[key] == 3:
                        testval = '<span class="node better3">&#8593</span>'
                    elif results[key] == 2:
                        testval = '<span class="node better2">&#8593</span>'
                    elif results[key] == 1:
                        testval = '<span class="node better">&#8593;</span>'
                    elif results[key] == -1:
                        testval = '<span class="node worse">&#8595;</span>'
                    elif results[key] == -2:
                        testval = '<span class="node worse2">&#8595</span>'
                    elif results[key] == -3:
                        testval = '<span class="node worse3">&#8595</span>'

                    table_row += '<td>%s</td>\n' % testval

        table_row += '</tr>'

        if active_branch != None:
            table_rows.append(table_row)

        if not crash and active_branch != None:
            prevResults = benchmarks

    if active_branch == None:
        index = 0
        for parameter in benchmarks.keys():
            table_rows.append("<tr><td></td><td style='font-weight:bold'>Parameters</td><td style='font-weight:bold'>%s</td></tr>" % parameter)
            for data_list in data_results.values():
                table_row = '<tr><td><input type="checkbox" name="comparison" value="%s"></td>\n' % data_list[6]
                table_row += '<td>%s</td>\n' % data_list[0]
                table_row += '<td><a href="%s">%s</a></td>\n' % (data_list[2], data_list[1])
                table_row += '<td><a href="%s">%s (<a href="%s">Data</a>)</a></td>\n' % (data_list[3], data_list[4], data_list[5])
                for kv in sorted(benchmark_results.keys()):
                    minval = min(benchmark_results[kv][parameter].values()) * 0.8
                    maxval = max(benchmark_results[kv][parameter].values()) * 1.2
                    value = benchmark_results[kv][parameter][data_list[1]]
                    position = (float(value) - float(minval)) / (float(maxval) - float(minval))
                    color = (255 * position, 255 * (1 - position), 0)
                    table_row += '<td><span style="color:#%s%s%s;">%g</span></td>' % (hex(int(color[0]))[2:], hex(int(color[1]))[2:], hex(int(color[1]))[2:], round(value, 2))
                table_row += '</tr>'

                table_rows.append(table_row)
            index += 1
        table_rows.reverse()


    table_rows.reverse()
    for row in table_rows:
        res.write(row)

    res.close()

    if active_branch != None:
        os.rename(fname, 'htmloutput-%s' % active_branch)
    else:
        os.rename(fname, 'htmloutput')

generate_html_output(None)
for branch in global_branches:
    generate_html_output(branch)