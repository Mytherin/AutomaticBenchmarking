
import bash
import os

scalefactor = 1


def generate(basedir, syscalls_log):
    os.chdir(basedir)
    tpchpath = os.path.join(basedir, 'TPCH')
    dbgenpath = os.path.join(tpchpath, 'tpch', 'dbgen')
    if not os.path.exists(tpchpath):
        bash.system(syscalls_log, 'hg clone ssh://hg@dev.monetdb.org/benchmarks/ %s' % tpchpath)
        os.rename(os.path.join(dbgenpath, 'makefile.suite'), os.path.join(dbgenpath, 'Makefile'))
        os.chdir(dbgenpath)
        bash.system(syscalls_log, 'make')
    bash.system(syscalls_log, '%s -s %d' % (os.path.join(dbgenpath, 'dbgen'), scalefactor))
