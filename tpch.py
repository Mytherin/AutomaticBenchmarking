
import os

scalefactor = 1


def generate(basedir):
    os.chdir(basedir)
    tpchpath = os.path.join(basedir, 'TPCH')
	dbgenpath = os.path.join(tpchpath, 'tpch', 'dbgen')
    if not os.path.exists(tpchpath):
        os.system('hg clone ssh://hg@dev.monetdb.org/benchmarks/ %s' % tpchpath)
        os.rename(os.path.join(dbgenpath, 'makefile.suite'), os.path.join(dbgenpath, 'Makefile'))
        os.chdir(dbgenpath)
        os.system('make')
	os.system('%s -s %d' % (os.path.join(dbgenpath, 'dbgen'), scalefactor))
