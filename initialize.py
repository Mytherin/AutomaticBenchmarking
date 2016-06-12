
base_revision = 'f8d19a6c2a88'

import sqlite3

conn = sqlite3.connect('settings.db')
c = conn.cursor();

c.execute('CREATE TABLE revision(currentrevision STRING)')
c.execute('INSERT INTO revision VALUES (?)', (base_revision,))

conn.commit()