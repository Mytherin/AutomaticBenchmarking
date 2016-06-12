
base_revision = '501372bf12c0'

import sqlite3

conn = sqlite3.connect('settings.db')
c = conn.cursor();

c.execute('DROP TABLE IF EXISTS revision')
c.execute('CREATE TABLE revision(currentrevision STRING)')
c.execute('INSERT INTO revision VALUES (?)', (base_revision,))

conn.commit()