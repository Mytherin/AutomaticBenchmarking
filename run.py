
import monetdb
import versioncontrol
import tpch

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

current_revision = results[0][0]

basedir = os.getcwd()

def initial_setup():
    # generate tpch code
    tpch.generate(basedir)

def run_test(branch, revision, date):
    dt = dateutil.parser.parse(date)
    monetdb.force_shutdown_database()

    os.chdir(basedir)
    # setup parameters
    dbpath = '/tmp/tmpdb'
    compiledir = '/tmp/build'
    tool = monetdb.versioncontrol()

    sourcedir = os.path.join(basedir, monetdb.folder())
    # if monetdb repository does not exist clone it
    if not os.path.exists(sourcedir):
        os.system(versioncontrol.clone(tool, sourcedir, monetdb.repository()))

    if not os.path.exists('results'):
        os.mkdir('results')

    # update to revision
    os.system(versioncontrol.update(tool, revision))

    compile_parameters = monetdb.compile_parameters()
    runtime_parameters = monetdb.runtime_parameters()

    result_file_name = 'results/%s.%s.%s' % (monetdb.name(), calendar.timegm(dt.timetuple()), revision)
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
            os.system('rm -rf %s' % compiledir)

            # install monetdb
            os.chdir(sourcedir)
            print(monetdb.compile(compiledir, cp_param))
            res = os.system(monetdb.compile(compiledir, cp_param))
            if res != 0:
                raise Exception("Failed to compile MonetDB")

            # clear database
            monetdb.clear(dbpath)

            # start monetdb server
            monetdb.start_database(compiledir, dbpath, '')

            # wait for monetdb to start
            success = False
            for i in range(100):
                res = os.system(monetdb.execute_statement(compiledir, "SELECT * FROM tables") + " &> /dev/null")
                if res == 0:
                    success = True
                    break
                time.sleep(1)

            if not success:
                raise Exception("Failed to start server")

            # load ddl
            res = os.system(monetdb.execute_file(compiledir, os.path.join(basedir, 'scripts', '%s.schema.sql' % monetdb.name())))
            if res != 0:
                raise Exception("Failed to load DDL")

            # load data
            f = open(os.path.join(basedir, 'scripts', '%s.load.sql' % monetdb.name()), 'r')
            script = f.read()
            f.close()

            f = open('/tmp/load.sql', 'w+')
            f.write(script.replace('_DIR_', os.path.join(basedir, 'TPCH', 'tpch', 'dbgen')))
            f.close()

            res = os.system(monetdb.execute_file(compiledir, '/tmp/load.sql'))
            if res != 0:
                raise Exception("Failed to load data")

            monetdb.shutdown_database(compiledir)

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
                    res = os.system(monetdb.execute_statement(compiledir, "SELECT * FROM tables") + " &> /dev/null")
                    if res == 0:
                        success = True
                        break
                    time.sleep(1)

                if not success:
                    raise Exception("Failed to start server")

                # run the actual tests
                querydir = os.path.join(basedir, 'queries')
                queries = os.listdir(querydir)
                queries.sort()
                for query in queries:
                    try:
                        execute_query = monetdb.execute_file(compiledir, os.path.join(querydir, query))
                        # warmup
                        for i in range(2):
                            res = os.system(execute_query)
                            if res != 0:
                                raise Exception("Failed to execute query %s" % query)

                        times = []
                        for i in range(5):
                            start = time.time()
                            res = os.system(execute_query)
                            end = time.time()
                            if res != 0:
                                raise Exception("Failed to execute query %s" % query)
                            times.append(end - start)
                        result_file.write('%s-mean:%g\n' % (query, numpy.mean(times)))
                        result_file.write('%s-std:%g\n' % (query, numpy.std(times)))
                        print('Query %s completed in ' % query, numpy.mean(times))
                    except:
                        result_file.write('%s-fail:execute\n' % query)

                monetdb.shutdown_database(compiledir)
                result_file.write('endresults:\n')
                result_file.write('endresultblock:\n')

    except:
        exception_message = sys.exc_info()[1].message.lower()
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
    os.system('scp %s lab05:/export/data1/testweb/web/chronos/results' % result_file_name)
    os.system("ssh lab05 'cd /export/data1/testweb/web/chronos && python generate.py'")

initial_setup()


while True:
    # get new revisions to run
    os.chdir(basedir)
    tool = monetdb.versioncontrol()

    sourcedir = os.path.join(basedir, monetdb.folder())
    # if monetdb repository does not exist clone it
    if not os.path.exists(sourcedir):
        os.system(versioncontrol.clone(tool, sourcedir, monetdb.repository()))

    os.chdir(sourcedir)
    os.system(versioncontrol.pull(tool))

    history = os.popen(versioncontrol.history(tool))
    revisions = []
    branch = None
    revision = None
    date = None
    for line in history:
        if len(line.strip()) == 0:
            if branch == None and revision != None:
                dt = dateutil.parser.parse(date)
                revisions.append((revision, date, calendar.timegm(dt.timetuple())))
            branch = None
        elif 'branch:' in line:
            branch = line.split(':')[1].strip()
        elif 'changeset:' in line:
            revision = line.split(':')[2].strip()
            if revision == current_revision:
                break
        elif 'date:' in line:
            date = line.split(':', 1)[1].strip()

    for revision in sorted(revisions, key=lambda x: x[2]):
        run_test('default', revision[0], revision[1])
        c.execute('UPDATE revision SET currentrevision=?', (current_revision,))
        conn.commit()

    time.sleep(5)
    

#run_test('default', '1bfd244713e3', 'Fri Jun 10 09:27:20 2016 +0200')
#run_test('default', '9fda1be9c35f', 'Thu Jun 09 14:57:08 2016 +0200')






