from sqlalchemy import *
from migrate import *
import os

import sys
sys.path.append('../../')

import model
import config
import board

metadata = MetaData()

backup = Table(config.SQL_BACKUP_TABLE, metadata,
    Column("num", Integer, primary_key=True),
    Column("board_name", String(25), nullable=False),
    Column("postnum", Integer),
    Column("parent", Integer),
    Column("timestamp", Integer),
    Column("lasthit", Integer),
    Column("ip", Text),

    Column("date", Text),
    Column("name", Text(convert_unicode=True)),
    Column("trip", Text),
    Column("email", Text),
    Column("subject", Text(convert_unicode=True)),
    Column("password", Text),
    Column("comment", Text(convert_unicode=True)),

    Column("image", Text(convert_unicode=True)),
    Column("size", Integer),
    Column("md5", Text),
    Column("width", Integer),
    Column("height", Integer),
    Column("thumbnail", Text),
    Column("tn_width", Text),
    Column("tn_height", Text),
    Column("lastedit", Text),
    Column("lastedit_ip", Text),
    Column("admin_post", Text),
    Column("stickied", Integer),
    Column("locked", Text),
    Column("timestampofarchival", Integer)
)

def brd_table(name):
    '''Generates new board table objects'''
    return Table(name, metadata,
        Column("num", Integer, primary_key=True),
        Column("parent", Integer),
        Column("timestamp", Integer),
        Column("lasthit", Integer),
        Column("ip", Text),

        Column("date", Text),
        Column("name", Text(convert_unicode=True)),
        Column("trip", Text),
        Column("email", Text(convert_unicode=True)),
        Column("subject", Text(convert_unicode=True)),
        Column("password", Text),
        Column("comment", Text(convert_unicode=True)),

        Column("image", Text(convert_unicode=True)),
        Column("size", Integer),
        Column("md5", Text),
        Column("width", Integer),
        Column("height", Integer),
        Column("thumbnail", Text),
        Column("tn_width", Text),
        Column("tn_height", Text),
        Column("lastedit", Text),
        Column("lastedit_ip", Text),
        Column("admin_post", Text),

        Column("stickied", Integer),
        Column("locked", Text),
    )

def board_with_backup(name):
    '''Generates new board table objects'''
    return Table(name, metadata,
        Column("num", Integer, primary_key=True),
        Column("parent", Integer),
        Column("timestamp", Integer),
        Column("lasthit", Integer),
        Column("ip", Text),

        Column("date", Text),
        Column("name", Text(convert_unicode=True)),
        Column("trip", Text),
        Column("email", Text(convert_unicode=True)),
        Column("subject", Text(convert_unicode=True)),
        Column("password", Text),
        Column("comment", Text(convert_unicode=True)),

        Column("image", Text(convert_unicode=True)),
        Column("size", Integer),
        Column("md5", Text),
        Column("width", Integer),
        Column("height", Integer),
        Column("thumbnail", Text),
        Column("tn_width", Text),
        Column("tn_height", Text),
        Column("lastedit", Text),
        Column("lastedit_ip", Text),
        Column("admin_post", Text),

        Column("stickied", Integer),
        Column("locked", Text),
        Column("backup", Boolean, default=False),
        Column("timestampofarchival", Integer)
    )

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    metadata.bind = migrate_engine
    backup.drop()

    sql = model.common.select()
    os.chdir('../')
    for b in model.Session().execute(sql).fetchall():
        brd_name = board.Board(b.board).options['SQL_TABLE']
        table = brd_table(brd_name)
        backup_col = Column("backup", Boolean, default=False)
        backup_col.create(table, populate_default=True)
        tstamp_col = Column("timestampofarchival", Integer)
        tstamp_col.create(table, populate_default=True)

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    metadata.bind = migrate_engine
    backup.create()

    sql = model.common.select()
    os.chdir('../')
    for b in model.Session().execute(sql).fetchall():
        brd_name = board.Board(b.board).options['SQL_TABLE']
        table = brd_table(brd_name)
        backup_col = Column("backup", Boolean, default=False)
        backup_col.drop(table)
        tstamp_col = Column("timestampofarchival", Integer)
        tstamp_col.drop(table)
