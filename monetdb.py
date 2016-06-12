
import os
import subprocess
import time

DEVNULL = open(os.devnull, 'w')

monetdb_tool = 'hg'
monetdb_name = 'monetdb'
monetdb_displayname = 'MonetDB'
monetdb_folder = 'MonetDB'
monetdb_repository = 'http://dev.monetdb.org/hg/MonetDB/'
monetdb_branches = ['default', 'Jun2016', 'python3udf', 'cand', 'jit', 'leftmart', 'orderidx', 'Jul2015']
monetdb_compile = './bootstrap && ./configure %s --prefix=%s && make clean && make install'
monetdb_port = 51113
monetdb_server = '%s/bin/mserver5 --dbpath=%s %s --set mapi_port=' + str(monetdb_port)
monetdb_client = '%s/bin/mclient -fcsv -p ' + str(monetdb_port)
monetdb_last_changeset = '59987:3c74ddd2cdc5'
monetdb_compile_parameters = [('Default', '--enable-geom=no --enable-jdbc=no --enable-debug=no --enable-assert=no --enable-optimize=yes')]
monetdb_runtime_parameters = [('Threads: 1', '--set gdk_nr_threads=1'), ('Threads: 8', '--set gdk_nr_threads=8')]

def name():
    return monetdb_name

def displayname():
    return monetdb_displayname

def versioncontrol(): 
    return monetdb_tool

def folder(): 
    return monetdb_folder

def repository():
    return monetdb_repository

def server(target_dir, db_path, runtime_parameter):
    return monetdb_server % (target_dir, db_path, runtime_parameter)

def client(target_dir):
    return monetdb_client % target_dir

def clear(db_path):
    print('rm -rf %s' % db_path)
    os.system('rm -rf %s' % db_path)

def branches():
    return [branch.lower().strip() for branch in monetdb_branches]

def compile_parameters():
    return monetdb_compile_parameters

def runtime_parameters():
    return monetdb_runtime_parameters

def compile(target_dir, parameters):
    return monetdb_compile % (parameters, target_dir)

def start_database(target_dir, db_path, runtime_parameter):
    subprocess.Popen(filter(None, server(target_dir, db_path, runtime_parameter).split(' ')))

def shutdown_database(target_dir):
    os.system('killall mserver5')
    time.sleep(10) #hacky

def force_shutdown_database():
    os.system('killall -9 mserver5')

def execute_statement(target_dir, statement, silent=True):
    return "%s -s \"%s\"%s" % (client(target_dir), statement, " &>/dev/null" if silent else "")

def execute_file(target_dir, filepath, silent=True):
    return "%s \"%s\"%s" % (client(target_dir), filepath, " &>/dev/null" if silent else "")

def revision_link(revision):
    return 'http://dev.monetdb.org/hg/MonetDB/rev/%s' % revision
