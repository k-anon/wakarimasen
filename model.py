import config, config_defaults
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, Text, String, MetaData, Boolean
from sqlalchemy.orm import sessionmaker, mapper, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.exc import OperationalError

engine = create_engine(config.SQL_ENGINE, pool_size=100, max_overflow=10)
Session = scoped_session(sessionmaker(bind=engine))
metadata = MetaData()

_boards = {}

class CompactPost(object):
    '''A prematurely optimized post object'''

    __slots__ = [
        # columns copied directly from rowproxy
        'num', 'parent', 'timestamp', 'lasthit', 'ip', 'date', 'name', 'trip',
        'email', 'subject', 'password', 'comment', 'image', 'size', 'md5',
        'width', 'height', 'thumbnail', 'tn_width', 'tn_height', 'lastedit',
        'lastedit_ip', 'admin_post', 'stickied', 'locked', 'backup',
        'timestampofarchival',
        # extensions
        'abbrev',
    ]

    def __init__(self, rowproxy):
        for key, value in rowproxy.items():
            setattr(self, key, value)
        self.abbrev = 0
    
    def __repr__(self):
        parent = ''
        if self.parent:
            parent = ' in thread %s' % self.parent
        return '<Post >>%s%s>' % (self.num, parent)

def board(name):
    '''Generates board table objects'''
    if name in _boards:
        return _boards[name]

    table = Table(name, metadata,
        Column("num", Integer, primary_key=True),       # Post number, auto-increments
        Column("parent", Integer),                      # Parent post for replies in threads. For original posts, must be set to 0 (and not null)
        Column("timestamp", Integer),                   # Timestamp in seconds for when the post was created
        Column("lasthit", Integer),                     # Last activity in thread. Must be set to the same value for BOTH the original post and all replies!
        Column("ip", Text),                             # IP number of poster, in integer form!

        Column("date", Text),                           # The date, as a string
        Column("name", Text(convert_unicode=True)),     # Name of the poster
        Column("trip", Text),                           # Tripcode (encoded)
        Column("email", Text(convert_unicode=True)),                          # Email address
        Column("subject", Text(convert_unicode=True)),  # Subject
        Column("password", Text),                       # Deletion password (in plaintext) 
        Column("comment", Text(convert_unicode=True)),  # Comment text, HTML encoded.

        Column("image", Text(convert_unicode=True)),    # Image filename with path and extension (IE, src/1081231233721.jpg)
        Column("size", Integer),                        # File size in bytes
        Column("md5", Text),                            # md5 sum in hex
        Column("width", Integer),                       # Width of image in pixels
        Column("height", Integer),                      # Height of image in pixels
        Column("thumbnail", Text),                      # Thumbnail filename with path and extension
        Column("tn_width", Text),                       # Thumbnail width in pixels
        Column("tn_height", Text),                      # Thumbnail height in pixels
        Column("lastedit", Text),                       # ADDED - Date of previous edit, as a string 
        Column("lastedit_ip", Text),                    # ADDED - Previous editor of the post, if any
        Column("admin_post", Text),                  # ADDED - Admin post?
        # TODO: Probably should make this Boolean. Keeping as int for now to maintain compatibility with sorting functions.
        Column("stickied", Integer),                    # ADDED - Stickied?
        Column("locked", Text),                         # ADDED - Locked?

        Column("backup", Boolean),                      # Hide from normal view?
        Column("timestampofarchival", Integer),         # Time since sticking into backup.
    )

    table.create(bind=engine, checkfirst=True)
    _boards[name] = table
    return _boards[name]


admin = Table(config.SQL_ADMIN_TABLE, metadata,
    Column("num", Integer, primary_key=True),           # Entry number, auto-increments
    Column("type", Text),                               # Type of entry (ipban, wordban, etc)
    Column("comment", Text(convert_unicode=True)),      # Comment for the entry
    Column("ival1", Text),                              # Integer value 1 (usually IP)
    Column("ival2", Text),                              # Integer value 2 (usually netmask)
    Column("sval1", Text),                              # String value 1
    Column("total", Text),                              # ADDED - Total Ban?
    Column("expiration", Integer)                       # ADDED - Ban Expiration?
)

proxy = Table(config.SQL_PROXY_TABLE, metadata,
    Column("num", Integer, primary_key=True),           # Entry number, auto-increments
    Column("type", Text),                               # Type of entry (black, white, etc)
    Column("ip", Text),                                 # IP address
    Column("timestamp", Integer),                       # Age since epoch
    Column("date", Text)                                # Human-readable form of date 
)

account = Table(config.SQL_ACCOUNT_TABLE, metadata,
    Column("username", String(25), primary_key=True),   # Name of user--must be unique
    Column("account", Text, nullable=False),            # Account type/class: mod, globmod, admin
    Column("password", Text, nullable=False),           # Encrypted password
    Column("reign", Text),                              # List of board (tables) under jurisdiction: globmod and admin have global power and are exempt
    Column("disabled", Integer)                         # Disabled account?
)

activity = Table(config.SQL_STAFFLOG_TABLE, metadata,
    Column("num", Integer, primary_key=True),           # ID
    Column("username", String(25), nullable=False),     # Name of moderator involved
    Column("action", Text),                             # Action performed: post_delete, admin_post, admin_edit, ip_ban, ban_edit, ban_remove
    Column("info", Text),                               # Information
    Column("date", Text),                               # Date of action
    Column("ip", Text),                                 # IP address of the moderator
    Column("admin_id", Integer),                        # For associating certain entries with the corresponding key on the admin table
    Column("timestamp", Integer)                        # Timestamp, for trimming
)

common = Table(config.SQL_COMMON_SITE_TABLE, metadata,
    Column("board", String(25), primary_key=True),      # Name of comment table
    Column("type", Text)                                # Corresponding board type? (Later use)
)

report = Table(config.SQL_REPORT_TABLE, metadata,
    Column("num", Integer, primary_key=True),           # Report number, auto-increments
    Column("board", String(25), nullable=False),        # Board name
    Column("reporter", Text, nullable=False),           # Reporter's IP address (decimal encoded)
    Column("offender", Text),                           # IP Address of the offending poster. Why the form-breaking redundancy with SQL_TABLE? If a post is deleted by the perpetrator, the trace is still logged. :)
    Column("postnum", Integer, nullable=False),         # Post number
    Column("comment", Text(convert_unicode=True),
                      nullable=False),                  # Mandated reason for the report.
    Column("timestamp", Integer),                       # Timestamp in seconds for when the post was created
    Column("date", Text),                               # Date of the report
    Column("resolved", Integer)                         # Is it resolved? (1: yes 0: no)
)

passprompt = Table(config.SQL_PASSPROMPT_TABLE, metadata,
    Column("id", Integer, primary_key=True),
    Column("host", Text),
    Column("task", String(25)),
    Column("boardname", String(25)),
    Column("post", Integer),
    Column("timestamp", Integer),
    Column("passfail", Integer) 
)

class Page(object):
    '''Pagination class: Given an SQL query and pagination information,
    produce only the relevant rows. N.B.: The board.Board class uses
    different pagination logic.'''

    def __init__(self, query, page_num, per_page):
        assert str(page_num).isdigit() and page_num > 0,\
            'Invalid page number.'
        assert str(per_page).isdigit() and per_page > 0,\
            'Invalid page entry count.'

        self.num = page_num
        if per_page > 200:
            self.per_page = 200
        else:
            self.per_page = per_page
        self.offset = (page_num - 1) * self.per_page

        session = Session()

        count = query.column(func.count())
        self.total_entries = session.execute(count).fetchone()['count_1']
        row_proxies = session.execute(query.limit(per_page)\
                                           .offset(self.offset))

        self.rows = [dict(row.items()) for row in row_proxies]

        self.total_pages = (self.total_entries + self.per_page - 1)\
                            / self.per_page
        if self.total_pages == 0:
            self.total_pages = 1

        if self.total_pages < self.num:
            self.num = self.total_pages

        # Quick fix for 'board' -> 'board_name' column renaming.
        if self.rows:
            ren_board = 'board' in self.rows[0].keys()

        row_ctr = row_cycle = 1
        for row in self.rows:
            row_cycle ^= 0x3
            row['rowtype'] = row_cycle
            row['entry_number'] = row_ctr
            if ren_board:
                row['board_name'] = row['board']
