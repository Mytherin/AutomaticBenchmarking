
import monetdb
import versioncontrol
import tpch
import bash

import os
import sys
import time
import dateutil.parser
import calendar
import numpy

import sqlite3

conn = sqlite3.connect('settings.db')
c = conn.cursor();

c.execute('SELECT currentrevision FROM revision');
results = c.fetchall()

syscalls_log = open('syscalls.txt', 'w+')
log_file = open('logs.txt', 'w+')

current_revision = results[0][0]

basedir = os.getcwd()

def initial_setup():
    # generate tpch code
    tpch.generate(basedir, syscalls_log)

def run_test(branch, revision, date):
    dt = dateutil.parser.parse(date)
    monetdb.force_shutdown_database(syscalls_log)

    os.chdir(basedir)
    # setup parameters
    dbpath = '/scratch/raasveld/database'
    compiledir = '/scratch/raasveld/build'
    tool = monetdb.versioncontrol()

    sourcedir = os.path.join(basedir, monetdb.folder())
    # if monetdb repository does not exist clone it
    if not os.path.exists(sourcedir):
        bash.system(syscalls_log, versioncontrol.clone(tool, sourcedir, monetdb.repository()))

    print(revision)

    os.chdir(sourcedir)
    # update to revision
    bash.system(syscalls_log, versioncontrol.update(tool, revision))
    os.chdir(basedir)

    if not os.path.exists('results'):
        os.mkdir('results')

    compile_parameters = monetdb.compile_parameters()
    runtime_parameters = monetdb.runtime_parameters()

    result_file_name = 'results/%s.%s.%s.%s' % (monetdb.name(), branch, calendar.timegm(dt.timetuple()), revision)
    result_file = open(result_file_name, 'w+')
    result_file.write('database:%s\n' % monetdb.displayname())
    result_file.write('branch:%s\n' % branch)
    result_file.write('date:%s\n' % date)
    rev = revision.split(':')[1] if ':' in revision else revision
    result_file.write('revision:%s\n' % rev)
    result_file.write('revisionlink:%s\n' % monetdb.revision_link(rev))
    result_file.write('startbenchmark:\n')
    try: 
        for cp in compile_parameters:
            cp_name = cp[0]
            cp_param = cp[1]

            # clear previous installation
            bash.system(syscalls_log, 'rm -rf %s' % compiledir)

            # install monetdb
            os.chdir(sourcedir)
            print(monetdb.compile(compiledir, cp_param))
            res = bash.system(syscalls_log, monetdb.compile(compiledir, cp_param))
            if res != 0:
                raise Exception("Failed to compile MonetDB")

            # clear database
            monetdb.clear(dbpath, syscalls_log)

            # start monetdb server
            monetdb.start_database(compiledir, dbpath, '')

            # wait for monetdb to start
            success = False
            for i in range(100):
                res = bash.system(syscalls_log, monetdb.execute_statement(compiledir, "SELECT * FROM tables") + " &> /dev/null")
                if res == 0:
                    success = True
                    break
                time.sleep(1)

            if not success:
                raise Exception("Failed to start server")

            # load ddl
            res = bash.system(syscalls_log, monetdb.execute_file(compiledir, os.path.join(basedir, 'scripts', '%s.schema.sql' % monetdb.name())))
            if res != 0:
                raise Exception("Failed to load DDL")

            # load data
            f = open(os.path.join(basedir, 'scripts', '%s.load.sql' % monetdb.name()), 'r')
            script = f.read()
            f.close()

            f = open('/tmp/load.sql', 'w+')
            f.write(script.replace('_DIR_', os.path.join(basedir, 'TPCH', 'tpch', 'dbgen')))
            f.close()

            res = bash.system(syscalls_log, monetdb.execute_file(compiledir, '/tmp/load.sql'))
            if res != 0:
                raise Exception("Failed to load data")

            monetdb.shutdown_database(compiledir, syscalls_log)

            for rp in runtime_parameters:
                rp_name = rp[0]
                rp_param = rp[1]

                result_file.write('startresultblock:\n')
                result_file.write('compileparameters:%s\n' % cp_name)
                result_file.write('runtimeparameters:%s\n' % rp_name)
                result_file.write('startresults:\n')

                monetdb.start_database(compiledir, dbpath, rp_param)

                # wait for monetdb to start
                success = False
                for i in range(100):
                    res = bash.system(syscalls_log, monetdb.execute_statement(compiledir, "SELECT * FROM tables") + " &> /dev/null")
                    if res == 0:
                        success = True
                        break
                    time.sleep(1)

                if not success:
                    raise Exception("Failed to start server")

                # run the actual tests
                log_file.write('Starting tests with parameters (Runtime: %s, Compilation: %s)\n' % (str(rp_name), str(cp_name)))
                log_file.flush()

                querydir = os.path.join(basedir, 'queries')
                queries = os.listdir(querydir)
                queries.sort()
                for query in queries:
                    try:
                        execute_query = monetdb.execute_file(compiledir, os.path.join(querydir, query))
                        # warmup
                        for i in range(2):
                            res = bash.system(syscalls_log, execute_query)
                            if res != 0:
                                raise Exception("Failed to execute query %s" % query)

                        times = []
                        for i in range(5):
                            start = time.time()
                            res = bash.system(syscalls_log, execute_query)
                            end = time.time()
                            if res != 0:
                                raise Exception("Failed to execute query %s" % query)
                            times.append(end - start)
                            result_file.write('%s-run-%d:%g\n' % (query, i, end - start))
                        result_file.write('%s-mean:%g\n' % (query, numpy.mean(times)))
                        result_file.write('%s-std:%g\n' % (query, numpy.std(times)))
                        log_file.write('Query %s completed in %g\n' % (query, numpy.mean(times)))
                        log_file.flush()
                    except:
                        result_file.write('%s-fail:execute\n' % query)
                        log_file.write('Failed to execute query %s\n' % (query,))
                        log_file.flush()

                monetdb.shutdown_database(compiledir, syscalls_log)
                result_file.write('endresults:\n')
                result_file.write('endresultblock:\n')

    except:
        exception_message = sys.exc_info()[1].message.lower()
        log_file.write('Exception: %s\n' % (exception_message,))
        log_file.flush()
        print(exception_message)
        if 'compile' in exception_message:
            result_file.write('fail:compile\n')
        elif 'start server' in exception_message:
            result_file.write('fail:start\n')
        elif 'load' in exception_message:
            result_file.write('fail:load\n')
        elif 'execute' in exception_message:
            result_file.write('fail:execute\n')
        else:
            result_file.write('fail:unknown\n')

    result_file.write('endbenchmark:\n')
    result_file.close()

    # copy the files to the web server machine thingy
    bash.system(syscalls_log, 'scp %s lab05:/export/data1/testweb/web/chronos/results' % (os.path.join(basedir, result_file_name)))
    bash.system(syscalls_log, "ssh lab05 'cp /export/data1/testweb/web/chronos/%s /export/data1/testweb/web/chronos/results/%s && cd /export/data1/testweb/web/chronos && python generate.py'" % (result_file_name, "%s.%s" % (monetdb.name(), branch)))

initial_setup()

while True:
    # get new revisions to run
    os.chdir(basedir)
    tool = monetdb.versioncontrol()
    tested_branches = monetdb.branches()

    sourcedir = os.path.join(basedir, monetdb.folder())
    # if monetdb repository does not exist clone it
    if not os.path.exists(sourcedir):
        bash.system(syscalls_log, versioncontrol.clone(tool, sourcedir, monetdb.repository()))

    os.chdir(sourcedir)
    bash.system(syscalls_log, versioncontrol.pull(tool))

    history = os.popen(versioncontrol.history(tool))
    revisions = []
    branch = 'default'
    revision = None
    date = None
    for line in history:
        if len(line.strip()) == 0:
            if branch.strip().lower() in tested_branches and revision != None:
                dt = dateutil.parser.parse(date)
                revisions.append((revision, date, calendar.timegm(dt.timetuple()), branch))
            branch = 'default'
        elif 'branch:' in line:
            branch = line.split(':')[1].strip()
        elif 'changeset:' in line:
            revision = line.split(':')[2].strip()
            if revision == current_revision:
                break
        elif 'date:' in line:
            date = line.split(':', 1)[1].strip()

    for revision in sorted(revisions, key=lambda x: x[2]):
        log_file.write("Testing Revision\n%s\n\n" % str(revision))
        log_file.flush()
        run_test(revision[3], revision[0], revision[1])
        c.execute('UPDATE revision SET currentrevision=?', (revision[0],))
        conn.commit()

    time.sleep(5)
    

log_file.close()
syscalls_log.close()