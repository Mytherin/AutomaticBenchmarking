



def history(tool):
    if tool == 'hg':
        return 'hg history'
    raise Exception("Unknown tool" + tool)

def clone(tool, folder, url):
    if tool == 'hg':
        return 'hg clone "%s" "%s"' % (url, folder)
    raise Exception("Unknown tool" + tool)

def update(tool, revision):
    if tool == 'hg':
        return 'hg update %s' % revision
    raise Exception("Unknown tool" + tool)

def pull(tool):
    if tool == 'hg':
        return 'hg pull'
    raise Exception("Unknown tool" + tool)