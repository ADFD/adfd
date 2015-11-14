# coding: utf-8
from sqlalchemy import BigInteger, Column, DateTime, Index, Integer, \
    SmallInteger, String, Table, Text, VARBINARY, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

t_ajax_chat_bans = Table(
    'ajax_chat_bans', metadata,
    Column('userID', Integer, nullable=False),
    Column('userName', String(64, u'utf8_bin'), nullable=False),
    Column('dateTime', DateTime, nullable=False),
    Column('ip', VARBINARY(16), nullable=False)
)

t_ajax_chat_invitations = Table(
    'ajax_chat_invitations', metadata,
    Column('userID', Integer, nullable=False),
    Column('channel', Integer, nullable=False),
    Column('dateTime', DateTime, nullable=False)
)


class AjaxChatMessage(Base):
    __tablename__ = 'ajax_chat_messages'

    id = Column(Integer, primary_key=True)
    userID = Column(Integer, nullable=False)
    userName = Column(String(64, u'utf8_bin'), nullable=False)
    userRole = Column(Integer, nullable=False)
    channel = Column(Integer, nullable=False)
    dateTime = Column(DateTime, nullable=False)
    ip = Column(VARBINARY(16), nullable=False)
    text = Column(Text)


t_ajax_chat_online = Table(
    'ajax_chat_online', metadata,
    Column('userID', Integer, nullable=False),
    Column('userName', String(64, u'utf8_bin'), nullable=False),
    Column('userRole', Integer, nullable=False),
    Column('channel', Integer, nullable=False),
    Column('dateTime', DateTime, nullable=False),
    Column('ip', VARBINARY(16), nullable=False)
)

t_phpbb_acl_groups = Table(
    'phpbb_acl_groups', metadata,
    Column('group_id', Integer, nullable=False, index=True,
           server_default=text("'0'")),
    Column('forum_id', Integer, nullable=False, server_default=text("'0'")),
    Column('auth_option_id', Integer, nullable=False, index=True,
           server_default=text("'0'")),
    Column('auth_role_id', Integer, nullable=False, index=True,
           server_default=text("'0'")),
    Column('auth_setting', Integer, nullable=False, server_default=text("'0'"))
)


class PhpbbAclOption(Base):
    __tablename__ = 'phpbb_acl_options'

    auth_option_id = Column(Integer, primary_key=True)
    auth_option = Column(String(50, u'utf8_bin'), nullable=False, unique=True,
                         server_default=text("''"))
    is_global = Column(Integer, nullable=False, server_default=text("'0'"))
    is_local = Column(Integer, nullable=False, server_default=text("'0'"))
    founder_only = Column(Integer, nullable=False, server_default=text("'0'"))


class PhpbbAclRole(Base):
    __tablename__ = 'phpbb_acl_roles'

    role_id = Column(Integer, primary_key=True)
    role_name = Column(String(255, u'utf8_bin'), nullable=False,
                       server_default=text("''"))
    role_description = Column(Text, nullable=False)
    role_type = Column(String(10, u'utf8_bin'), nullable=False, index=True,
                       server_default=text("''"))
    role_order = Column(SmallInteger, nullable=False, index=True,
                        server_default=text("'0'"))


class PhpbbAclRolesDatum(Base):
    __tablename__ = 'phpbb_acl_roles_data'

    role_id = Column(Integer, primary_key=True, nullable=False,
                     server_default=text("'0'"))
    auth_option_id = Column(Integer, primary_key=True, nullable=False,
                            index=True, server_default=text("'0'"))
    auth_setting = Column(Integer, nullable=False, server_default=text("'0'"))


t_phpbb_acl_users = Table(
    'phpbb_acl_users', metadata,
    Column('user_id', Integer, nullable=False, index=True,
           server_default=text("'0'")),
    Column('forum_id', Integer, nullable=False, server_default=text("'0'")),
    Column('auth_option_id', Integer, nullable=False, index=True,
           server_default=text("'0'")),
    Column('auth_role_id', Integer, nullable=False, index=True,
           server_default=text("'0'")),
    Column('auth_setting', Integer, nullable=False, server_default=text("'0'"))
)


class PhpbbAttachment(Base):
    __tablename__ = 'phpbb_attachments'

    attach_id = Column(Integer, primary_key=True)
    post_msg_id = Column(Integer, nullable=False, index=True,
                         server_default=text("'0'"))
    topic_id = Column(Integer, nullable=False, index=True,
                      server_default=text("'0'"))
    in_message = Column(Integer, nullable=False, server_default=text("'0'"))
    poster_id = Column(Integer, nullable=False, index=True,
                       server_default=text("'0'"))
    is_orphan = Column(Integer, nullable=False, index=True,
                       server_default=text("'1'"))
    physical_filename = Column(String(255, u'utf8_bin'), nullable=False,
                               server_default=text("''"))
    real_filename = Column(String(255, u'utf8_bin'), nullable=False,
                           server_default=text("''"))
    download_count = Column(Integer, nullable=False,
                            server_default=text("'0'"))
    attach_comment = Column(Text, nullable=False)
    extension = Column(String(100, u'utf8_bin'), nullable=False,
                       server_default=text("''"))
    mimetype = Column(String(100, u'utf8_bin'), nullable=False,
                      server_default=text("''"))
    filesize = Column(Integer, nullable=False, server_default=text("'0'"))
    filetime = Column(Integer, nullable=False, index=True,
                      server_default=text("'0'"))
    thumbnail = Column(Integer, nullable=False, server_default=text("'0'"))


class PhpbbBanlist(Base):
    __tablename__ = 'phpbb_banlist'
    __table_args__ = (
        Index('ban_user', 'ban_userid', 'ban_exclude'),
        Index('ban_ip', 'ban_ip', 'ban_exclude'),
        Index('ban_email', 'ban_email', 'ban_exclude')
    )

    ban_id = Column(Integer, primary_key=True)
    ban_userid = Column(Integer, nullable=False, server_default=text("'0'"))
    ban_ip = Column(String(40, u'utf8_bin'), nullable=False,
                    server_default=text("''"))
    ban_email = Column(String(100, u'utf8_bin'), nullable=False,
                       server_default=text("''"))
    ban_start = Column(Integer, nullable=False, server_default=text("'0'"))
    ban_end = Column(Integer, nullable=False, index=True,
                     server_default=text("'0'"))
    ban_exclude = Column(Integer, nullable=False, server_default=text("'0'"))
    ban_reason = Column(String(255, u'utf8_bin'), nullable=False,
                        server_default=text("''"))
    ban_give_reason = Column(String(255, u'utf8_bin'), nullable=False,
                             server_default=text("''"))


class PhpbbBbcode(Base):
    __tablename__ = 'phpbb_bbcodes'

    bbcode_id = Column(SmallInteger, primary_key=True,
                       server_default=text("'0'"))
    bbcode_tag = Column(String(16, u'utf8_bin'), nullable=False,
                        server_default=text("''"))
    bbcode_helpline = Column(String(255, u'utf8_bin'), nullable=False,
                             server_default=text("''"))
    display_on_posting = Column(Integer, nullable=False, index=True,
                                server_default=text("'0'"))
    bbcode_match = Column(Text, nullable=False)
    bbcode_tpl = Column(String, nullable=False)
    first_pass_match = Column(String, nullable=False)
    first_pass_replace = Column(String, nullable=False)
    second_pass_match = Column(String, nullable=False)
    second_pass_replace = Column(String, nullable=False)


class PhpbbBoardrule(Base):
    __tablename__ = 'phpbb_boardrules'

    rule_id = Column(Integer, primary_key=True)
    rule_language = Column(Integer, nullable=False, server_default=text("'0'"))
    rule_left_id = Column(Integer, nullable=False, server_default=text("'0'"))
    rule_right_id = Column(Integer, nullable=False, server_default=text("'0'"))
    rule_parent_id = Column(Integer, nullable=False,
                            server_default=text("'0'"))
    rule_anchor = Column(String(255, u'utf8_bin'), nullable=False,
                         server_default=text("''"))
    rule_title = Column(String(200, u'utf8_bin'), nullable=False,
                        server_default=text("''"))
    rule_message = Column(Text, nullable=False)
    rule_message_bbcode_uid = Column(String(8, u'utf8_bin'), nullable=False,
                                     server_default=text("''"))
    rule_message_bbcode_bitfield = Column(String(255, u'utf8_bin'),
                                          nullable=False,
                                          server_default=text("''"))
    rule_message_bbcode_options = Column(Integer, nullable=False,
                                         server_default=text("'7'"))
    rule_parents = Column(String, nullable=False)


class PhpbbBookmark(Base):
    __tablename__ = 'phpbb_bookmarks'

    topic_id = Column(Integer, primary_key=True, nullable=False,
                      server_default=text("'0'"))
    user_id = Column(Integer, primary_key=True, nullable=False,
                     server_default=text("'0'"))


class PhpbbBot(Base):
    __tablename__ = 'phpbb_bots'

    bot_id = Column(Integer, primary_key=True)
    bot_active = Column(Integer, nullable=False, index=True,
                        server_default=text("'1'"))
    bot_name = Column(String(255, u'utf8_bin'), nullable=False,
                      server_default=text("''"))
    user_id = Column(Integer, nullable=False, server_default=text("'0'"))
    bot_agent = Column(String(255, u'utf8_bin'), nullable=False,
                       server_default=text("''"))
    bot_ip = Column(String(255, u'utf8_bin'), nullable=False,
                    server_default=text("''"))


t_phpbb_captcha_answers = Table(
    'phpbb_captcha_answers', metadata,
    Column('question_id', Integer, nullable=False, index=True,
           server_default=text("'0'")),
    Column('answer_text', String(255, u'utf8_bin'), nullable=False,
           server_default=text("''"))
)


class PhpbbCaptchaQuestion(Base):
    __tablename__ = 'phpbb_captcha_questions'

    question_id = Column(Integer, primary_key=True)
    strict = Column(Integer, nullable=False, server_default=text("'0'"))
    lang_id = Column(Integer, nullable=False, server_default=text("'0'"))
    lang_iso = Column(String(30, u'utf8_bin'), nullable=False, index=True,
                      server_default=text("''"))
    question_text = Column(Text, nullable=False)


class PhpbbConfig(Base):
    __tablename__ = 'phpbb_config'

    config_name = Column(String(255, u'utf8_bin'), primary_key=True,
                         server_default=text("''"))
    config_value = Column(String(255, u'utf8_bin'), nullable=False,
                          server_default=text("''"))
    is_dynamic = Column(Integer, nullable=False, index=True,
                        server_default=text("'0'"))


class PhpbbConfigText(Base):
    __tablename__ = 'phpbb_config_text'

    config_name = Column(String(255, u'utf8_bin'), primary_key=True,
                         server_default=text("''"))
    config_value = Column(String, nullable=False)


class PhpbbConfirm(Base):
    __tablename__ = 'phpbb_confirm'

    confirm_id = Column(String(32, u'utf8_bin'), primary_key=True,
                        nullable=False, server_default=text("''"))
    session_id = Column(String(32, u'utf8_bin'), primary_key=True,
                        nullable=False, server_default=text("''"))
    confirm_type = Column(Integer, nullable=False, index=True,
                          server_default=text("'0'"))
    code = Column(String(8, u'utf8_bin'), nullable=False,
                  server_default=text("''"))
    seed = Column(Integer, nullable=False, server_default=text("'0'"))
    attempts = Column(Integer, nullable=False, server_default=text("'0'"))


class PhpbbDisallow(Base):
    __tablename__ = 'phpbb_disallow'

    disallow_id = Column(Integer, primary_key=True)
    disallow_username = Column(String(255, u'utf8_bin'), nullable=False,
                               server_default=text("''"))


class PhpbbDraft(Base):
    __tablename__ = 'phpbb_drafts'

    draft_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, server_default=text("'0'"))
    topic_id = Column(Integer, nullable=False, server_default=text("'0'"))
    forum_id = Column(Integer, nullable=False, server_default=text("'0'"))
    save_time = Column(Integer, nullable=False, index=True,
                       server_default=text("'0'"))
    draft_subject = Column(String(255, u'utf8_bin'), nullable=False,
                           server_default=text("''"))
    draft_message = Column(String, nullable=False)


t_phpbb_ext = Table(
    'phpbb_ext', metadata,
    Column('ext_name', String(255, u'utf8_bin'), nullable=False, unique=True,
           server_default=text("''")),
    Column('ext_active', Integer, nullable=False, server_default=text("'0'")),
    Column('ext_state', Text, nullable=False)
)


class PhpbbExtensionGroup(Base):
    __tablename__ = 'phpbb_extension_groups'

    group_id = Column(Integer, primary_key=True)
    group_name = Column(String(255, u'utf8_bin'), nullable=False,
                        server_default=text("''"))
    cat_id = Column(Integer, nullable=False, server_default=text("'0'"))
    allow_group = Column(Integer, nullable=False, server_default=text("'0'"))
    download_mode = Column(Integer, nullable=False, server_default=text("'1'"))
    upload_icon = Column(String(255, u'utf8_bin'), nullable=False,
                         server_default=text("''"))
    max_filesize = Column(Integer, nullable=False, server_default=text("'0'"))
    allowed_forums = Column(Text, nullable=False)
    allow_in_pm = Column(Integer, nullable=False, server_default=text("'0'"))


class PhpbbExtension(Base):
    __tablename__ = 'phpbb_extensions'

    extension_id = Column(Integer, primary_key=True)
    group_id = Column(Integer, nullable=False, server_default=text("'0'"))
    extension = Column(String(100, u'utf8_bin'), nullable=False,
                       server_default=text("''"))


class PhpbbForum(Base):
    __tablename__ = 'phpbb_forums'
    __table_args__ = (
        Index('left_right_id', 'left_id', 'right_id'),
    )

    forum_id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, nullable=False, server_default=text("'0'"))
    left_id = Column(Integer, nullable=False, server_default=text("'0'"))
    right_id = Column(Integer, nullable=False, server_default=text("'0'"))
    forum_parents = Column(String, nullable=False)
    forum_name = Column(String(255, u'utf8_bin'), nullable=False,
                        server_default=text("''"))
    forum_desc = Column(Text, nullable=False)
    forum_desc_bitfield = Column(String(255, u'utf8_bin'), nullable=False,
                                 server_default=text("''"))
    forum_desc_options = Column(Integer, nullable=False,
                                server_default=text("'7'"))
    forum_desc_uid = Column(String(8, u'utf8_bin'), nullable=False,
                            server_default=text("''"))
    forum_link = Column(String(255, u'utf8_bin'), nullable=False,
                        server_default=text("''"))
    forum_password = Column(String(255, u'utf8_bin'), nullable=False,
                            server_default=text("''"))
    forum_style = Column(Integer, nullable=False, server_default=text("'0'"))
    forum_image = Column(String(255, u'utf8_bin'), nullable=False,
                         server_default=text("''"))
    forum_rules = Column(Text, nullable=False)
    forum_rules_link = Column(String(255, u'utf8_bin'), nullable=False,
                              server_default=text("''"))
    forum_rules_bitfield = Column(String(255, u'utf8_bin'), nullable=False,
                                  server_default=text("''"))
    forum_rules_options = Column(Integer, nullable=False,
                                 server_default=text("'7'"))
    forum_rules_uid = Column(String(8, u'utf8_bin'), nullable=False,
                             server_default=text("''"))
    forum_topics_per_page = Column(Integer, nullable=False,
                                   server_default=text("'0'"))
    forum_type = Column(Integer, nullable=False, server_default=text("'0'"))
    forum_status = Column(Integer, nullable=False, server_default=text("'0'"))
    forum_last_post_id = Column(Integer, nullable=False, index=True,
                                server_default=text("'0'"))
    forum_last_poster_id = Column(Integer, nullable=False,
                                  server_default=text("'0'"))
    forum_last_post_subject = Column(String(255, u'utf8_bin'), nullable=False,
                                     server_default=text("''"))
    forum_last_post_time = Column(Integer, nullable=False,
                                  server_default=text("'0'"))
    forum_last_poster_name = Column(String(255, u'utf8_bin'), nullable=False,
                                    server_default=text("''"))
    forum_last_poster_colour = Column(String(6, u'utf8_bin'), nullable=False,
                                      server_default=text("''"))
    forum_flags = Column(Integer, nullable=False, server_default=text("'32'"))
    display_subforum_list = Column(Integer, nullable=False,
                                   server_default=text("'1'"))
    display_on_index = Column(Integer, nullable=False,
                              server_default=text("'1'"))
    enable_indexing = Column(Integer, nullable=False,
                             server_default=text("'1'"))
    enable_icons = Column(Integer, nullable=False, server_default=text("'1'"))
    enable_prune = Column(Integer, nullable=False, server_default=text("'0'"))
    prune_next = Column(Integer, nullable=False, server_default=text("'0'"))
    prune_days = Column(Integer, nullable=False, server_default=text("'0'"))
    prune_viewed = Column(Integer, nullable=False, server_default=text("'0'"))
    prune_freq = Column(Integer, nullable=False, server_default=text("'0'"))
    forum_options = Column(Integer, nullable=False, server_default=text("'0'"))
    enable_reputation = Column(Integer, nullable=False,
                               server_default=text("'0'"))
    forum_posts_approved = Column(Integer, nullable=False,
                                  server_default=text("'0'"))
    forum_posts_unapproved = Column(Integer, nullable=False,
                                    server_default=text("'0'"))
    forum_posts_softdeleted = Column(Integer, nullable=False,
                                     server_default=text("'0'"))
    forum_topics_approved = Column(Integer, nullable=False,
                                   server_default=text("'0'"))
    forum_topics_unapproved = Column(Integer, nullable=False,
                                     server_default=text("'0'"))
    forum_topics_softdeleted = Column(Integer, nullable=False,
                                      server_default=text("'0'"))
    enable_shadow_prune = Column(Integer, nullable=False,
                                 server_default=text("'0'"))
    prune_shadow_days = Column(Integer, nullable=False,
                               server_default=text("'7'"))
    prune_shadow_freq = Column(Integer, nullable=False,
                               server_default=text("'1'"))
    prune_shadow_next = Column(Integer, nullable=False,
                               server_default=text("'0'"))


class PhpbbForumsAcces(Base):
    __tablename__ = 'phpbb_forums_access'

    forum_id = Column(Integer, primary_key=True, nullable=False,
                      server_default=text("'0'"))
    user_id = Column(Integer, primary_key=True, nullable=False,
                     server_default=text("'0'"))
    session_id = Column(String(32, u'utf8_bin'), primary_key=True,
                        nullable=False, server_default=text("''"))


class PhpbbForumsTrack(Base):
    __tablename__ = 'phpbb_forums_track'

    user_id = Column(Integer, primary_key=True, nullable=False,
                     server_default=text("'0'"))
    forum_id = Column(Integer, primary_key=True, nullable=False,
                      server_default=text("'0'"))
    mark_time = Column(Integer, nullable=False, server_default=text("'0'"))


t_phpbb_forums_watch = Table(
    'phpbb_forums_watch', metadata,
    Column('forum_id', Integer, nullable=False, index=True,
           server_default=text("'0'")),
    Column('user_id', Integer, nullable=False, index=True,
           server_default=text("'0'")),
    Column('notify_status', Integer, nullable=False, index=True,
           server_default=text("'0'"))
)


class PhpbbGroup(Base):
    __tablename__ = 'phpbb_groups'
    __table_args__ = (
        Index('group_legend_name', 'group_legend', 'group_name'),
    )

    group_id = Column(Integer, primary_key=True)
    group_type = Column(Integer, nullable=False, server_default=text("'1'"))
    group_founder_manage = Column(Integer, nullable=False,
                                  server_default=text("'0'"))
    group_name = Column(String(255, u'utf8_bin'), nullable=False,
                        server_default=text("''"))
    group_desc = Column(Text, nullable=False)
    group_desc_bitfield = Column(String(255, u'utf8_bin'), nullable=False,
                                 server_default=text("''"))
    group_desc_options = Column(Integer, nullable=False,
                                server_default=text("'7'"))
    group_desc_uid = Column(String(8, u'utf8_bin'), nullable=False,
                            server_default=text("''"))
    group_display = Column(Integer, nullable=False, server_default=text("'0'"))
    group_avatar = Column(String(255, u'utf8_bin'), nullable=False,
                          server_default=text("''"))
    group_avatar_type = Column(String(255, u'utf8_bin'), nullable=False,
                               server_default=text("''"))
    group_avatar_width = Column(SmallInteger, nullable=False,
                                server_default=text("'0'"))
    group_avatar_height = Column(SmallInteger, nullable=False,
                                 server_default=text("'0'"))
    group_rank = Column(Integer, nullable=False, server_default=text("'0'"))
    group_colour = Column(String(6, u'utf8_bin'), nullable=False,
                          server_default=text("''"))
    group_sig_chars = Column(Integer, nullable=False,
                             server_default=text("'0'"))
    group_receive_pm = Column(Integer, nullable=False,
                              server_default=text("'0'"))
    group_message_limit = Column(Integer, nullable=False,
                                 server_default=text("'0'"))
    group_legend = Column(Integer, nullable=False, server_default=text("'0'"))
    group_max_recipients = Column(Integer, nullable=False,
                                  server_default=text("'0'"))
    group_skip_auth = Column(Integer, nullable=False,
                             server_default=text("'0'"))
    group_reputation_power = Column(Integer, nullable=False,
                                    server_default=text("'0'"))


class PhpbbIcon(Base):
    __tablename__ = 'phpbb_icons'

    icons_id = Column(Integer, primary_key=True)
    icons_url = Column(String(255, u'utf8_bin'), nullable=False,
                       server_default=text("''"))
    icons_width = Column(Integer, nullable=False, server_default=text("'0'"))
    icons_height = Column(Integer, nullable=False, server_default=text("'0'"))
    icons_order = Column(Integer, nullable=False, server_default=text("'0'"))
    display_on_posting = Column(Integer, nullable=False, index=True,
                                server_default=text("'1'"))


class PhpbbLang(Base):
    __tablename__ = 'phpbb_lang'

    lang_id = Column(Integer, primary_key=True)
    lang_iso = Column(String(30, u'utf8_bin'), nullable=False, index=True,
                      server_default=text("''"))
    lang_dir = Column(String(30, u'utf8_bin'), nullable=False,
                      server_default=text("''"))
    lang_english_name = Column(String(100, u'utf8_bin'), nullable=False,
                               server_default=text("''"))
    lang_local_name = Column(String(255, u'utf8_bin'), nullable=False,
                             server_default=text("''"))
    lang_author = Column(String(255, u'utf8_bin'), nullable=False,
                         server_default=text("''"))


class PhpbbLog(Base):
    __tablename__ = 'phpbb_log'

    log_id = Column(Integer, primary_key=True)
    log_type = Column(Integer, nullable=False, index=True,
                      server_default=text("'0'"))
    user_id = Column(Integer, nullable=False, index=True,
                     server_default=text("'0'"))
    forum_id = Column(Integer, nullable=False, index=True,
                      server_default=text("'0'"))
    topic_id = Column(Integer, nullable=False, index=True,
                      server_default=text("'0'"))
    reportee_id = Column(Integer, nullable=False, index=True,
                         server_default=text("'0'"))
    log_ip = Column(String(40, u'utf8_bin'), nullable=False,
                    server_default=text("''"))
    log_time = Column(Integer, nullable=False, server_default=text("'0'"))
    log_operation = Column(Text, nullable=False)
    log_data = Column(String, nullable=False)


t_phpbb_login_attempts = Table(
    'phpbb_login_attempts', metadata,
    Column('attempt_ip', String(40, u'utf8_bin'), nullable=False,
           server_default=text("''")),
    Column('attempt_browser', String(150, u'utf8_bin'), nullable=False,
           server_default=text("''")),
    Column('attempt_forwarded_for', String(255, u'utf8_bin'), nullable=False,
           server_default=text("''")),
    Column('attempt_time', Integer, nullable=False, index=True,
           server_default=text("'0'")),
    Column('user_id', Integer, nullable=False, index=True,
           server_default=text("'0'")),
    Column('username', String(255, u'utf8_bin'), nullable=False,
           server_default=text("'0'")),
    Column('username_clean', String(255, u'utf8_bin'), nullable=False,
           server_default=text("'0'")),
    Index('att_ip', 'attempt_ip', 'attempt_time'),
    Index('att_for', 'attempt_forwarded_for', 'attempt_time')
)


class PhpbbMigration(Base):
    __tablename__ = 'phpbb_migrations'

    migration_name = Column(String(255, u'utf8_bin'), primary_key=True,
                            server_default=text("''"))
    migration_depends_on = Column(Text, nullable=False)
    migration_schema_done = Column(Integer, nullable=False,
                                   server_default=text("'0'"))
    migration_data_done = Column(Integer, nullable=False,
                                 server_default=text("'0'"))
    migration_data_state = Column(Text, nullable=False)
    migration_start_time = Column(Integer, nullable=False,
                                  server_default=text("'0'"))
    migration_end_time = Column(Integer, nullable=False,
                                server_default=text("'0'"))


t_phpbb_moderator_cache = Table(
    'phpbb_moderator_cache', metadata,
    Column('forum_id', Integer, nullable=False, index=True,
           server_default=text("'0'")),
    Column('user_id', Integer, nullable=False, server_default=text("'0'")),
    Column('username', String(255, u'utf8_bin'), nullable=False,
           server_default=text("''")),
    Column('group_id', Integer, nullable=False, server_default=text("'0'")),
    Column('group_name', String(255, u'utf8_bin'), nullable=False,
           server_default=text("''")),
    Column('display_on_index', Integer, nullable=False, index=True,
           server_default=text("'1'"))
)


class PhpbbModule(Base):
    __tablename__ = 'phpbb_modules'
    __table_args__ = (
        Index('class_left_id', 'module_class', 'left_id'),
        Index('left_right_id', 'left_id', 'right_id')
    )

    module_id = Column(Integer, primary_key=True)
    module_enabled = Column(Integer, nullable=False, index=True,
                            server_default=text("'1'"))
    module_display = Column(Integer, nullable=False,
                            server_default=text("'1'"))
    module_basename = Column(String(255, u'utf8_bin'), nullable=False,
                             server_default=text("''"))
    module_class = Column(String(10, u'utf8_bin'), nullable=False,
                          server_default=text("''"))
    parent_id = Column(Integer, nullable=False, server_default=text("'0'"))
    left_id = Column(Integer, nullable=False, server_default=text("'0'"))
    right_id = Column(Integer, nullable=False, server_default=text("'0'"))
    module_langname = Column(String(255, u'utf8_bin'), nullable=False,
                             server_default=text("''"))
    module_mode = Column(String(255, u'utf8_bin'), nullable=False,
                         server_default=text("''"))
    module_auth = Column(String(255, u'utf8_bin'), nullable=False,
                         server_default=text("''"))


class PhpbbNotificationType(Base):
    __tablename__ = 'phpbb_notification_types'

    notification_type_id = Column(SmallInteger, primary_key=True)
    notification_type_name = Column(String(255, u'utf8_bin'), nullable=False,
                                    unique=True, server_default=text("''"))
    notification_type_enabled = Column(Integer, nullable=False,
                                       server_default=text("'1'"))


class PhpbbNotification(Base):
    __tablename__ = 'phpbb_notifications'
    __table_args__ = (
        Index('item_ident', 'notification_type_id', 'item_id'),
        Index('user', 'user_id', 'notification_read')
    )

    notification_id = Column(Integer, primary_key=True)
    notification_type_id = Column(SmallInteger, nullable=False,
                                  server_default=text("'0'"))
    item_id = Column(Integer, nullable=False, server_default=text("'0'"))
    item_parent_id = Column(Integer, nullable=False,
                            server_default=text("'0'"))
    user_id = Column(Integer, nullable=False, server_default=text("'0'"))
    notification_read = Column(Integer, nullable=False,
                               server_default=text("'0'"))
    notification_time = Column(Integer, nullable=False,
                               server_default=text("'1'"))
    notification_data = Column(Text, nullable=False)


class PhpbbOauthAccount(Base):
    __tablename__ = 'phpbb_oauth_accounts'

    user_id = Column(Integer, primary_key=True, nullable=False,
                     server_default=text("'0'"))
    provider = Column(String(255, u'utf8_bin'), primary_key=True,
                      nullable=False, server_default=text("''"))
    oauth_provider_id = Column(Text, nullable=False)


t_phpbb_oauth_tokens = Table(
    'phpbb_oauth_tokens', metadata,
    Column('user_id', Integer, nullable=False, index=True,
           server_default=text("'0'")),
    Column('session_id', String(32, u'utf8_bin'), nullable=False,
           server_default=text("''")),
    Column('provider', String(255, u'utf8_bin'), nullable=False, index=True,
           server_default=text("''")),
    Column('oauth_token', String, nullable=False)
)

t_phpbb_poll_options = Table(
    'phpbb_poll_options', metadata,
    Column('poll_option_id', Integer, nullable=False, index=True,
           server_default=text("'0'")),
    Column('topic_id', Integer, nullable=False, index=True,
           server_default=text("'0'")),
    Column('poll_option_text', Text, nullable=False),
    Column('poll_option_total', Integer, nullable=False,
           server_default=text("'0'"))
)

t_phpbb_poll_votes = Table(
    'phpbb_poll_votes', metadata,
    Column('topic_id', Integer, nullable=False, index=True,
           server_default=text("'0'")),
    Column('poll_option_id', Integer, nullable=False,
           server_default=text("'0'")),
    Column('vote_user_id', Integer, nullable=False, index=True,
           server_default=text("'0'")),
    Column('vote_user_ip', String(40, u'utf8_bin'), nullable=False, index=True,
           server_default=text("''"))
)


class PhpbbPost(Base):
    __tablename__ = 'phpbb_posts'
    __table_args__ = (
        Index('tid_post_time', 'topic_id', 'post_time'),
        Index('post_content', 'post_text', 'post_subject')
    )

    post_id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, nullable=False, index=True,
                      server_default=text("'0'"))
    forum_id = Column(Integer, nullable=False, index=True,
                      server_default=text("'0'"))
    poster_id = Column(Integer, nullable=False, index=True,
                       server_default=text("'0'"))
    icon_id = Column(Integer, nullable=False, server_default=text("'0'"))
    poster_ip = Column(String(40, u'utf8_bin'), nullable=False, index=True,
                       server_default=text("''"))
    post_time = Column(Integer, nullable=False, server_default=text("'0'"))
    post_reported = Column(Integer, nullable=False, server_default=text("'0'"))
    enable_bbcode = Column(Integer, nullable=False, server_default=text("'1'"))
    enable_smilies = Column(Integer, nullable=False,
                            server_default=text("'1'"))
    enable_magic_url = Column(Integer, nullable=False,
                              server_default=text("'1'"))
    enable_sig = Column(Integer, nullable=False, server_default=text("'1'"))
    post_username = Column(String(255, u'utf8_bin'), nullable=False,
                           server_default=text("''"))
    post_subject = Column(String(255, u'utf8_unicode_ci'), nullable=False,
                          index=True, server_default=text("''"))
    post_text = Column(String(collation=u'utf8_unicode_ci'), nullable=False)
    post_checksum = Column(String(32, u'utf8_bin'), nullable=False,
                           server_default=text("''"))
    post_attachment = Column(Integer, nullable=False,
                             server_default=text("'0'"))
    bbcode_bitfield = Column(String(255, u'utf8_bin'), nullable=False,
                             server_default=text("''"))
    bbcode_uid = Column(String(8, u'utf8_bin'), nullable=False,
                        server_default=text("''"))
    post_postcount = Column(Integer, nullable=False,
                            server_default=text("'1'"))
    post_edit_time = Column(Integer, nullable=False,
                            server_default=text("'0'"))
    post_edit_reason = Column(String(255, u'utf8_bin'), nullable=False,
                              server_default=text("''"))
    post_edit_user = Column(Integer, nullable=False,
                            server_default=text("'0'"))
    post_edit_count = Column(SmallInteger, nullable=False,
                             server_default=text("'0'"))
    post_edit_locked = Column(Integer, nullable=False,
                              server_default=text("'0'"))
    post_reputation = Column(Integer, nullable=False,
                             server_default=text("'0'"))
    post_visibility = Column(Integer, nullable=False, index=True,
                             server_default=text("'0'"))
    post_delete_time = Column(Integer, nullable=False,
                              server_default=text("'0'"))
    post_delete_reason = Column(String(255, u'utf8_bin'), nullable=False,
                                server_default=text("''"))
    post_delete_user = Column(Integer, nullable=False,
                              server_default=text("'0'"))


class PhpbbPrivmsg(Base):
    __tablename__ = 'phpbb_privmsgs'

    msg_id = Column(Integer, primary_key=True)
    root_level = Column(Integer, nullable=False, index=True,
                        server_default=text("'0'"))
    author_id = Column(Integer, nullable=False, index=True,
                       server_default=text("'0'"))
    icon_id = Column(Integer, nullable=False, server_default=text("'0'"))
    author_ip = Column(String(40, u'utf8_bin'), nullable=False, index=True,
                       server_default=text("''"))
    message_time = Column(Integer, nullable=False, index=True,
                          server_default=text("'0'"))
    enable_bbcode = Column(Integer, nullable=False, server_default=text("'1'"))
    enable_smilies = Column(Integer, nullable=False,
                            server_default=text("'1'"))
    enable_magic_url = Column(Integer, nullable=False,
                              server_default=text("'1'"))
    enable_sig = Column(Integer, nullable=False, server_default=text("'1'"))
    message_subject = Column(String(255, u'utf8_bin'), nullable=False,
                             server_default=text("''"))
    message_text = Column(String, nullable=False)
    message_edit_reason = Column(String(255, u'utf8_bin'), nullable=False,
                                 server_default=text("''"))
    message_edit_user = Column(Integer, nullable=False,
                               server_default=text("'0'"))
    message_attachment = Column(Integer, nullable=False,
                                server_default=text("'0'"))
    bbcode_bitfield = Column(String(255, u'utf8_bin'), nullable=False,
                             server_default=text("''"))
    bbcode_uid = Column(String(8, u'utf8_bin'), nullable=False,
                        server_default=text("''"))
    message_edit_time = Column(Integer, nullable=False,
                               server_default=text("'0'"))
    message_edit_count = Column(SmallInteger, nullable=False,
                                server_default=text("'0'"))
    to_address = Column(Text, nullable=False)
    bcc_address = Column(Text, nullable=False)
    message_reported = Column(Integer, nullable=False,
                              server_default=text("'0'"))


class PhpbbPrivmsgsFolder(Base):
    __tablename__ = 'phpbb_privmsgs_folder'

    folder_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True,
                     server_default=text("'0'"))
    folder_name = Column(String(255, u'utf8_bin'), nullable=False,
                         server_default=text("''"))
    pm_count = Column(Integer, nullable=False, server_default=text("'0'"))


class PhpbbPrivmsgsRule(Base):
    __tablename__ = 'phpbb_privmsgs_rules'

    rule_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True,
                     server_default=text("'0'"))
    rule_check = Column(Integer, nullable=False, server_default=text("'0'"))
    rule_connection = Column(Integer, nullable=False,
                             server_default=text("'0'"))
    rule_string = Column(String(255, u'utf8_bin'), nullable=False,
                         server_default=text("''"))
    rule_user_id = Column(Integer, nullable=False, server_default=text("'0'"))
    rule_group_id = Column(Integer, nullable=False, server_default=text("'0'"))
    rule_action = Column(Integer, nullable=False, server_default=text("'0'"))
    rule_folder_id = Column(Integer, nullable=False,
                            server_default=text("'0'"))


t_phpbb_privmsgs_to = Table(
    'phpbb_privmsgs_to', metadata,
    Column('msg_id', Integer, nullable=False, index=True,
           server_default=text("'0'")),
    Column('user_id', Integer, nullable=False, server_default=text("'0'")),
    Column('author_id', Integer, nullable=False, index=True,
           server_default=text("'0'")),
    Column('pm_deleted', Integer, nullable=False, server_default=text("'0'")),
    Column('pm_new', Integer, nullable=False, server_default=text("'1'")),
    Column('pm_unread', Integer, nullable=False, server_default=text("'1'")),
    Column('pm_replied', Integer, nullable=False, server_default=text("'0'")),
    Column('pm_marked', Integer, nullable=False, server_default=text("'0'")),
    Column('pm_forwarded', Integer, nullable=False,
           server_default=text("'0'")),
    Column('folder_id', Integer, nullable=False, server_default=text("'0'")),
    Index('usr_flder_id', 'user_id', 'folder_id')
)


class PhpbbProfileField(Base):
    __tablename__ = 'phpbb_profile_fields'

    field_id = Column(Integer, primary_key=True)
    field_name = Column(String(255, u'utf8_bin'), nullable=False,
                        server_default=text("''"))
    field_type = Column(String(100, u'utf8_bin'), nullable=False, index=True,
                        server_default=text("''"))
    field_ident = Column(String(20, u'utf8_bin'), nullable=False,
                         server_default=text("''"))
    field_length = Column(String(20, u'utf8_bin'), nullable=False,
                          server_default=text("''"))
    field_minlen = Column(String(255, u'utf8_bin'), nullable=False,
                          server_default=text("''"))
    field_maxlen = Column(String(255, u'utf8_bin'), nullable=False,
                          server_default=text("''"))
    field_novalue = Column(String(255, u'utf8_bin'), nullable=False,
                           server_default=text("''"))
    field_default_value = Column(String(255, u'utf8_bin'), nullable=False,
                                 server_default=text("''"))
    field_validation = Column(String(64, u'utf8_bin'), nullable=False,
                              server_default=text("''"))
    field_required = Column(Integer, nullable=False,
                            server_default=text("'0'"))
    field_show_on_reg = Column(Integer, nullable=False,
                               server_default=text("'0'"))
    field_hide = Column(Integer, nullable=False, server_default=text("'0'"))
    field_no_view = Column(Integer, nullable=False, server_default=text("'0'"))
    field_active = Column(Integer, nullable=False, server_default=text("'0'"))
    field_order = Column(Integer, nullable=False, index=True,
                         server_default=text("'0'"))
    field_show_profile = Column(Integer, nullable=False,
                                server_default=text("'0'"))
    field_show_on_vt = Column(Integer, nullable=False,
                              server_default=text("'0'"))
    field_show_novalue = Column(Integer, nullable=False,
                                server_default=text("'0'"))
    field_show_on_pm = Column(Integer, nullable=False,
                              server_default=text("'0'"))
    field_show_on_ml = Column(Integer, nullable=False,
                              server_default=text("'0'"))
    field_is_contact = Column(Integer, nullable=False,
                              server_default=text("'0'"))
    field_contact_desc = Column(String(255, u'utf8_bin'), nullable=False,
                                server_default=text("''"))
    field_contact_url = Column(String(255, u'utf8_bin'), nullable=False,
                               server_default=text("''"))


class PhpbbProfileFieldsDatum(Base):
    __tablename__ = 'phpbb_profile_fields_data'

    user_id = Column(Integer, primary_key=True, server_default=text("'0'"))
    pf_phpbb_interests = Column(String, nullable=False)
    pf_phpbb_occupation = Column(String, nullable=False)
    pf_phpbb_icq = Column(String(255, u'utf8_bin'), nullable=False,
                          server_default=text("''"))
    pf_phpbb_website = Column(String(255, u'utf8_bin'), nullable=False,
                              server_default=text("''"))
    pf_phpbb_wlm = Column(String(255, u'utf8_bin'), nullable=False,
                          server_default=text("''"))
    pf_phpbb_yahoo = Column(String(255, u'utf8_bin'), nullable=False,
                            server_default=text("''"))
    pf_phpbb_aol = Column(String(255, u'utf8_bin'), nullable=False,
                          server_default=text("''"))
    pf_phpbb_location = Column(String(255, u'utf8_bin'), nullable=False,
                               server_default=text("''"))
    pf_phpbb_facebook = Column(String(255, u'utf8_bin'), nullable=False,
                               server_default=text("''"))
    pf_phpbb_googleplus = Column(String(255, u'utf8_bin'), nullable=False,
                                 server_default=text("''"))
    pf_phpbb_skype = Column(String(255, u'utf8_bin'), nullable=False,
                            server_default=text("''"))
    pf_phpbb_twitter = Column(String(255, u'utf8_bin'), nullable=False,
                              server_default=text("''"))
    pf_phpbb_youtube = Column(String(255, u'utf8_bin'), nullable=False,
                              server_default=text("''"))


class PhpbbProfileFieldsLang(Base):
    __tablename__ = 'phpbb_profile_fields_lang'

    field_id = Column(Integer, primary_key=True, nullable=False,
                      server_default=text("'0'"))
    lang_id = Column(Integer, primary_key=True, nullable=False,
                     server_default=text("'0'"))
    option_id = Column(Integer, primary_key=True, nullable=False,
                       server_default=text("'0'"))
    field_type = Column(String(100, u'utf8_bin'), nullable=False,
                        server_default=text("''"))
    lang_value = Column(String(255, u'utf8_bin'), nullable=False,
                        server_default=text("''"))


class PhpbbProfileLang(Base):
    __tablename__ = 'phpbb_profile_lang'

    field_id = Column(Integer, primary_key=True, nullable=False,
                      server_default=text("'0'"))
    lang_id = Column(Integer, primary_key=True, nullable=False,
                     server_default=text("'0'"))
    lang_name = Column(String(255, u'utf8_bin'), nullable=False,
                       server_default=text("''"))
    lang_explain = Column(Text, nullable=False)
    lang_default_value = Column(String(255, u'utf8_bin'), nullable=False,
                                server_default=text("''"))


class PhpbbQaConfirm(Base):
    __tablename__ = 'phpbb_qa_confirm'
    __table_args__ = (
        Index('lookup', 'confirm_id', 'session_id', 'lang_iso'),
    )

    session_id = Column(String(32, u'utf8_bin'), nullable=False, index=True,
                        server_default=text("''"))
    confirm_id = Column(String(32, u'utf8_bin'), primary_key=True,
                        server_default=text("''"))
    lang_iso = Column(String(30, u'utf8_bin'), nullable=False,
                      server_default=text("''"))
    question_id = Column(Integer, nullable=False, server_default=text("'0'"))
    attempts = Column(Integer, nullable=False, server_default=text("'0'"))
    confirm_type = Column(SmallInteger, nullable=False,
                          server_default=text("'0'"))


class PhpbbRank(Base):
    __tablename__ = 'phpbb_ranks'

    rank_id = Column(Integer, primary_key=True)
    rank_title = Column(String(255, u'utf8_bin'), nullable=False,
                        server_default=text("''"))
    rank_min = Column(Integer, nullable=False, server_default=text("'0'"))
    rank_special = Column(Integer, nullable=False, server_default=text("'0'"))
    rank_image = Column(String(255, u'utf8_bin'), nullable=False,
                        server_default=text("''"))


class PhpbbReport(Base):
    __tablename__ = 'phpbb_reports'

    report_id = Column(Integer, primary_key=True)
    reason_id = Column(SmallInteger, nullable=False,
                       server_default=text("'0'"))
    post_id = Column(Integer, nullable=False, index=True,
                     server_default=text("'0'"))
    user_id = Column(Integer, nullable=False, server_default=text("'0'"))
    user_notify = Column(Integer, nullable=False, server_default=text("'0'"))
    report_closed = Column(Integer, nullable=False, server_default=text("'0'"))
    report_time = Column(Integer, nullable=False, server_default=text("'0'"))
    report_text = Column(String, nullable=False)
    pm_id = Column(Integer, nullable=False, index=True,
                   server_default=text("'0'"))
    reported_post_enable_bbcode = Column(Integer, nullable=False,
                                         server_default=text("'1'"))
    reported_post_enable_smilies = Column(Integer, nullable=False,
                                          server_default=text("'1'"))
    reported_post_enable_magic_url = Column(Integer, nullable=False,
                                            server_default=text("'1'"))
    reported_post_text = Column(String, nullable=False)
    reported_post_uid = Column(String(8, u'utf8_bin'), nullable=False,
                               server_default=text("''"))
    reported_post_bitfield = Column(String(255, u'utf8_bin'), nullable=False,
                                    server_default=text("''"))


class PhpbbReportsReason(Base):
    __tablename__ = 'phpbb_reports_reasons'

    reason_id = Column(SmallInteger, primary_key=True)
    reason_title = Column(String(255, u'utf8_bin'), nullable=False,
                          server_default=text("''"))
    reason_description = Column(String, nullable=False)
    reason_order = Column(SmallInteger, nullable=False,
                          server_default=text("'0'"))


class PhpbbSearchResult(Base):
    __tablename__ = 'phpbb_search_results'

    search_key = Column(String(32, u'utf8_bin'), primary_key=True,
                        server_default=text("''"))
    search_time = Column(Integer, nullable=False, server_default=text("'0'"))
    search_keywords = Column(String, nullable=False)
    search_authors = Column(String, nullable=False)


class PhpbbSearchWordlist(Base):
    __tablename__ = 'phpbb_search_wordlist'

    word_id = Column(Integer, primary_key=True)
    word_text = Column(String(255, u'utf8_bin'), nullable=False, unique=True,
                       server_default=text("''"))
    word_common = Column(Integer, nullable=False, server_default=text("'0'"))
    word_count = Column(Integer, nullable=False, index=True,
                        server_default=text("'0'"))


t_phpbb_search_wordmatch = Table(
    'phpbb_search_wordmatch', metadata,
    Column('post_id', Integer, nullable=False, index=True,
           server_default=text("'0'")),
    Column('word_id', Integer, nullable=False, index=True,
           server_default=text("'0'")),
    Column('title_match', Integer, nullable=False, server_default=text("'0'")),
    Index('unq_mtch', 'word_id', 'post_id', 'title_match', unique=True),
    Index('un_mtch', 'word_id', 'post_id', 'title_match', unique=True)
)


class PhpbbSession(Base):
    __tablename__ = 'phpbb_sessions'

    session_id = Column(String(32, u'utf8_bin'), primary_key=True,
                        server_default=text("''"))
    session_user_id = Column(Integer, nullable=False, index=True,
                             server_default=text("'0'"))
    session_forum_id = Column(Integer, nullable=False, index=True,
                              server_default=text("'0'"))
    session_last_visit = Column(Integer, nullable=False,
                                server_default=text("'0'"))
    session_start = Column(Integer, nullable=False, server_default=text("'0'"))
    session_time = Column(Integer, nullable=False, index=True,
                          server_default=text("'0'"))
    session_ip = Column(String(40, u'utf8_bin'), nullable=False,
                        server_default=text("''"))
    session_browser = Column(String(150, u'utf8_bin'), nullable=False,
                             server_default=text("''"))
    session_forwarded_for = Column(String(255, u'utf8_bin'), nullable=False,
                                   server_default=text("''"))
    session_page = Column(String(255, u'utf8_bin'), nullable=False,
                          server_default=text("''"))
    session_viewonline = Column(Integer, nullable=False,
                                server_default=text("'1'"))
    session_autologin = Column(Integer, nullable=False,
                               server_default=text("'0'"))
    session_admin = Column(Integer, nullable=False, server_default=text("'0'"))


class PhpbbSessionsKey(Base):
    __tablename__ = 'phpbb_sessions_keys'

    key_id = Column(String(32, u'utf8_bin'), primary_key=True, nullable=False,
                    server_default=text("''"))
    user_id = Column(Integer, primary_key=True, nullable=False,
                     server_default=text("'0'"))
    last_ip = Column(String(40, u'utf8_bin'), nullable=False,
                     server_default=text("''"))
    last_login = Column(Integer, nullable=False, index=True,
                        server_default=text("'0'"))


class PhpbbSitelist(Base):
    __tablename__ = 'phpbb_sitelist'

    site_id = Column(Integer, primary_key=True)
    site_ip = Column(String(40, u'utf8_bin'), nullable=False,
                     server_default=text("''"))
    site_hostname = Column(String(255, u'utf8_bin'), nullable=False,
                           server_default=text("''"))
    ip_exclude = Column(Integer, nullable=False, server_default=text("'0'"))


class PhpbbSmily(Base):
    __tablename__ = 'phpbb_smilies'

    smiley_id = Column(Integer, primary_key=True)
    code = Column(String(50, u'utf8_bin'), nullable=False,
                  server_default=text("''"))
    emotion = Column(String(50, u'utf8_bin'), nullable=False,
                     server_default=text("''"))
    smiley_url = Column(String(50, u'utf8_bin'), nullable=False,
                        server_default=text("''"))
    smiley_width = Column(SmallInteger, nullable=False,
                          server_default=text("'0'"))
    smiley_height = Column(SmallInteger, nullable=False,
                           server_default=text("'0'"))
    smiley_order = Column(Integer, nullable=False, server_default=text("'0'"))
    display_on_posting = Column(Integer, nullable=False, index=True,
                                server_default=text("'1'"))


class PhpbbStyle(Base):
    __tablename__ = 'phpbb_styles'

    style_id = Column(Integer, primary_key=True)
    style_name = Column(String(255, u'utf8_bin'), nullable=False, unique=True,
                        server_default=text("''"))
    style_copyright = Column(String(255, u'utf8_bin'), nullable=False,
                             server_default=text("''"))
    style_active = Column(Integer, nullable=False, server_default=text("'1'"))
    style_path = Column(String(100, u'utf8_bin'), nullable=False,
                        server_default=text("''"))
    bbcode_bitfield = Column(String(255, u'utf8_bin'), nullable=False,
                             server_default=text("'kNg='"))
    style_parent_id = Column(Integer, nullable=False,
                             server_default=text("'0'"))
    style_parent_tree = Column(Text, nullable=False)
    topic_preview_theme = Column(String(255, u'utf8_bin'), nullable=False,
                                 server_default=text("'light'"))


class PhpbbTeampage(Base):
    __tablename__ = 'phpbb_teampage'

    teampage_id = Column(Integer, primary_key=True)
    group_id = Column(Integer, nullable=False, server_default=text("'0'"))
    teampage_name = Column(String(255, u'utf8_bin'), nullable=False,
                           server_default=text("''"))
    teampage_position = Column(Integer, nullable=False,
                               server_default=text("'0'"))
    teampage_parent = Column(Integer, nullable=False,
                             server_default=text("'0'"))


class PhpbbThank(Base):
    __tablename__ = 'phpbb_thanks'

    post_id = Column(Integer, primary_key=True, nullable=False, index=True,
                     server_default=text("'0'"))
    poster_id = Column(Integer, nullable=False, index=True,
                       server_default=text("'0'"))
    user_id = Column(Integer, primary_key=True, nullable=False, index=True,
                     server_default=text("'0'"))
    topic_id = Column(Integer, nullable=False, index=True,
                      server_default=text("'0'"))
    forum_id = Column(Integer, nullable=False, index=True,
                      server_default=text("'0'"))
    thanks_time = Column(Integer, nullable=False, server_default=text("'0'"))


class PhpbbTopic(Base):
    __tablename__ = 'phpbb_topics'
    __table_args__ = (
        Index('forum_id_type', 'forum_id', 'topic_type'),
        Index('forum_vis_last', 'forum_id', 'topic_visibility',
              'topic_last_post_id'),
        Index('fid_time_moved', 'forum_id', 'topic_last_post_time',
              'topic_moved_id')
    )

    topic_id = Column(Integer, primary_key=True)
    forum_id = Column(Integer, nullable=False, index=True,
                      server_default=text("'0'"))
    icon_id = Column(Integer, nullable=False, server_default=text("'0'"))
    topic_attachment = Column(Integer, nullable=False,
                              server_default=text("'0'"))
    topic_reported = Column(Integer, nullable=False,
                            server_default=text("'0'"))
    topic_title = Column(String(255, u'utf8_unicode_ci'), nullable=False,
                         server_default=text("''"))
    topic_poster = Column(Integer, nullable=False, server_default=text("'0'"))
    topic_time = Column(Integer, nullable=False, server_default=text("'0'"))
    topic_time_limit = Column(Integer, nullable=False,
                              server_default=text("'0'"))
    topic_views = Column(Integer, nullable=False, server_default=text("'0'"))
    topic_status = Column(Integer, nullable=False, server_default=text("'0'"))
    topic_type = Column(Integer, nullable=False, server_default=text("'0'"))
    topic_first_post_id = Column(Integer, nullable=False,
                                 server_default=text("'0'"))
    topic_first_poster_name = Column(String(255, u'utf8_unicode_ci'),
                                     nullable=False, server_default=text("''"))
    topic_first_poster_colour = Column(String(6, u'utf8_bin'), nullable=False,
                                       server_default=text("''"))
    topic_last_post_id = Column(Integer, nullable=False,
                                server_default=text("'0'"))
    topic_last_poster_id = Column(Integer, nullable=False,
                                  server_default=text("'0'"))
    topic_last_poster_name = Column(String(255, u'utf8_bin'), nullable=False,
                                    server_default=text("''"))
    topic_last_poster_colour = Column(String(6, u'utf8_bin'), nullable=False,
                                      server_default=text("''"))
    topic_last_post_subject = Column(String(255, u'utf8_bin'), nullable=False,
                                     server_default=text("''"))
    topic_last_post_time = Column(Integer, nullable=False, index=True,
                                  server_default=text("'0'"))
    topic_last_view_time = Column(Integer, nullable=False,
                                  server_default=text("'0'"))
    topic_moved_id = Column(Integer, nullable=False,
                            server_default=text("'0'"))
    topic_bumped = Column(Integer, nullable=False, server_default=text("'0'"))
    topic_bumper = Column(Integer, nullable=False, server_default=text("'0'"))
    poll_title = Column(String(255, u'utf8_bin'), nullable=False,
                        server_default=text("''"))
    poll_start = Column(Integer, nullable=False, server_default=text("'0'"))
    poll_length = Column(Integer, nullable=False, server_default=text("'0'"))
    poll_max_options = Column(Integer, nullable=False,
                              server_default=text("'1'"))
    poll_last_vote = Column(Integer, nullable=False,
                            server_default=text("'0'"))
    poll_vote_change = Column(Integer, nullable=False,
                              server_default=text("'0'"))
    topic_visibility = Column(Integer, nullable=False, index=True,
                              server_default=text("'0'"))
    topic_delete_time = Column(Integer, nullable=False,
                               server_default=text("'0'"))
    topic_delete_reason = Column(String(255, u'utf8_bin'), nullable=False,
                                 server_default=text("''"))
    topic_delete_user = Column(Integer, nullable=False,
                               server_default=text("'0'"))
    topic_posts_approved = Column(Integer, nullable=False,
                                  server_default=text("'0'"))
    topic_posts_unapproved = Column(Integer, nullable=False,
                                    server_default=text("'0'"))
    topic_posts_softdeleted = Column(Integer, nullable=False,
                                     server_default=text("'0'"))


class PhpbbTopicsPosted(Base):
    __tablename__ = 'phpbb_topics_posted'

    user_id = Column(Integer, primary_key=True, nullable=False,
                     server_default=text("'0'"))
    topic_id = Column(Integer, primary_key=True, nullable=False,
                      server_default=text("'0'"))
    topic_posted = Column(Integer, nullable=False, server_default=text("'0'"))


class PhpbbTopicsTrack(Base):
    __tablename__ = 'phpbb_topics_track'

    user_id = Column(Integer, primary_key=True, nullable=False,
                     server_default=text("'0'"))
    topic_id = Column(Integer, primary_key=True, nullable=False, index=True,
                      server_default=text("'0'"))
    forum_id = Column(Integer, nullable=False, index=True,
                      server_default=text("'0'"))
    mark_time = Column(Integer, nullable=False, server_default=text("'0'"))


t_phpbb_topics_watch = Table(
    'phpbb_topics_watch', metadata,
    Column('topic_id', Integer, nullable=False, index=True,
           server_default=text("'0'")),
    Column('user_id', Integer, nullable=False, index=True,
           server_default=text("'0'")),
    Column('notify_status', Integer, nullable=False, index=True,
           server_default=text("'0'"))
)

t_phpbb_user_group = Table(
    'phpbb_user_group', metadata,
    Column('group_id', Integer, nullable=False, index=True,
           server_default=text("'0'")),
    Column('user_id', Integer, nullable=False, index=True,
           server_default=text("'0'")),
    Column('group_leader', Integer, nullable=False, index=True,
           server_default=text("'0'")),
    Column('user_pending', Integer, nullable=False, server_default=text("'1'"))
)

t_phpbb_user_notifications = Table(
    'phpbb_user_notifications', metadata,
    Column('item_type', String(255, u'utf8_bin'), nullable=False,
           server_default=text("''")),
    Column('item_id', Integer, nullable=False, server_default=text("'0'")),
    Column('user_id', Integer, nullable=False, server_default=text("'0'")),
    Column('method', String(255, u'utf8_bin'), nullable=False,
           server_default=text("''")),
    Column('notify', Integer, nullable=False, server_default=text("'1'"))
)


class PhpbbUser(Base):
    __tablename__ = 'phpbb_users'

    user_id = Column(Integer, primary_key=True)
    user_type = Column(Integer, nullable=False, index=True,
                       server_default=text("'0'"))
    group_id = Column(Integer, nullable=False, server_default=text("'3'"))
    user_permissions = Column(String, nullable=False)
    user_perm_from = Column(Integer, nullable=False,
                            server_default=text("'0'"))
    user_ip = Column(String(40, u'utf8_bin'), nullable=False,
                     server_default=text("''"))
    user_regdate = Column(Integer, nullable=False, server_default=text("'0'"))
    username = Column(String(255, u'utf8_bin'), nullable=False,
                      server_default=text("''"))
    username_clean = Column(String(255, u'utf8_bin'), nullable=False,
                            unique=True, server_default=text("''"))
    user_password = Column(String(255, u'utf8_bin'), nullable=False,
                           server_default=text("''"))
    user_passchg = Column(Integer, nullable=False, server_default=text("'0'"))
    user_email = Column(String(100, u'utf8_bin'), nullable=False,
                        server_default=text("''"))
    user_email_hash = Column(BigInteger, nullable=False, index=True,
                             server_default=text("'0'"))
    user_birthday = Column(String(10, u'utf8_bin'), nullable=False, index=True,
                           server_default=text("''"))
    user_lastvisit = Column(Integer, nullable=False,
                            server_default=text("'0'"))
    user_lastmark = Column(Integer, nullable=False, server_default=text("'0'"))
    user_lastpost_time = Column(Integer, nullable=False,
                                server_default=text("'0'"))
    user_lastpage = Column(String(200, u'utf8_bin'), nullable=False,
                           server_default=text("''"))
    user_last_confirm_key = Column(String(10, u'utf8_bin'), nullable=False,
                                   server_default=text("''"))
    user_last_search = Column(Integer, nullable=False,
                              server_default=text("'0'"))
    user_warnings = Column(Integer, nullable=False, server_default=text("'0'"))
    user_last_warning = Column(Integer, nullable=False,
                               server_default=text("'0'"))
    user_login_attempts = Column(Integer, nullable=False,
                                 server_default=text("'0'"))
    user_inactive_reason = Column(Integer, nullable=False,
                                  server_default=text("'0'"))
    user_inactive_time = Column(Integer, nullable=False,
                                server_default=text("'0'"))
    user_posts = Column(Integer, nullable=False, server_default=text("'0'"))
    user_lang = Column(String(30, u'utf8_bin'), nullable=False,
                       server_default=text("''"))
    user_timezone = Column(String(100, u'utf8_bin'), nullable=False,
                           server_default=text("''"))
    user_dateformat = Column(String(30, u'utf8_bin'), nullable=False,
                             server_default=text("'d M Y H:i'"))
    user_style = Column(Integer, nullable=False, server_default=text("'0'"))
    user_rank = Column(Integer, nullable=False, server_default=text("'0'"))
    user_colour = Column(String(6, u'utf8_bin'), nullable=False,
                         server_default=text("''"))
    user_new_privmsg = Column(Integer, nullable=False,
                              server_default=text("'0'"))
    user_unread_privmsg = Column(Integer, nullable=False,
                                 server_default=text("'0'"))
    user_last_privmsg = Column(Integer, nullable=False,
                               server_default=text("'0'"))
    user_message_rules = Column(Integer, nullable=False,
                                server_default=text("'0'"))
    user_full_folder = Column(Integer, nullable=False,
                              server_default=text("'-3'"))
    user_emailtime = Column(Integer, nullable=False,
                            server_default=text("'0'"))
    user_topic_show_days = Column(SmallInteger, nullable=False,
                                  server_default=text("'0'"))
    user_topic_sortby_type = Column(String(1, u'utf8_bin'), nullable=False,
                                    server_default=text("'t'"))
    user_topic_sortby_dir = Column(String(1, u'utf8_bin'), nullable=False,
                                   server_default=text("'d'"))
    user_post_show_days = Column(SmallInteger, nullable=False,
                                 server_default=text("'0'"))
    user_post_sortby_type = Column(String(1, u'utf8_bin'), nullable=False,
                                   server_default=text("'t'"))
    user_post_sortby_dir = Column(String(1, u'utf8_bin'), nullable=False,
                                  server_default=text("'a'"))
    user_notify = Column(Integer, nullable=False, server_default=text("'0'"))
    user_notify_pm = Column(Integer, nullable=False,
                            server_default=text("'1'"))
    user_notify_type = Column(Integer, nullable=False,
                              server_default=text("'0'"))
    user_allow_pm = Column(Integer, nullable=False, server_default=text("'1'"))
    user_allow_viewonline = Column(Integer, nullable=False,
                                   server_default=text("'1'"))
    user_allow_viewemail = Column(Integer, nullable=False,
                                  server_default=text("'1'"))
    user_allow_massemail = Column(Integer, nullable=False,
                                  server_default=text("'1'"))
    user_options = Column(Integer, nullable=False,
                          server_default=text("'230271'"))
    user_avatar = Column(String(255, u'utf8_bin'), nullable=False,
                         server_default=text("''"))
    user_avatar_type = Column(String(255, u'utf8_bin'), nullable=False,
                              server_default=text("''"))
    user_avatar_width = Column(SmallInteger, nullable=False,
                               server_default=text("'0'"))
    user_avatar_height = Column(SmallInteger, nullable=False,
                                server_default=text("'0'"))
    user_sig = Column(String, nullable=False)
    user_sig_bbcode_uid = Column(String(8, u'utf8_bin'), nullable=False,
                                 server_default=text("''"))
    user_sig_bbcode_bitfield = Column(String(255, u'utf8_bin'), nullable=False,
                                      server_default=text("''"))
    user_jabber = Column(String(255, u'utf8_bin'), nullable=False,
                         server_default=text("''"))
    user_actkey = Column(String(32, u'utf8_bin'), nullable=False,
                         server_default=text("''"))
    user_newpasswd = Column(String(255, u'utf8_bin'), nullable=False,
                            server_default=text("''"))
    user_form_salt = Column(String(32, u'utf8_bin'), nullable=False,
                            server_default=text("''"))
    user_new = Column(Integer, nullable=False, server_default=text("'1'"))
    user_reminded = Column(Integer, nullable=False, server_default=text("'0'"))
    user_reminded_time = Column(Integer, nullable=False,
                                server_default=text("'0'"))
    user_reputation = Column(Integer, nullable=False,
                             server_default=text("'0'"))
    user_rep_new = Column(Integer, nullable=False, server_default=text("'0'"))
    user_rep_last = Column(Integer, nullable=False, server_default=text("'0'"))
    user_rs_notification = Column(Integer, nullable=False,
                                  server_default=text("'1'"))
    user_rs_default_power = Column(Integer, nullable=False,
                                   server_default=text("'0'"))
    user_last_rep_ban = Column(Integer, nullable=False,
                               server_default=text("'0'"))
    board_announcements_status = Column(Integer, nullable=False,
                                        server_default=text("'0'"))
    user_topic_preview = Column(Integer, nullable=False,
                                server_default=text("'1'"))


class PhpbbWarning(Base):
    __tablename__ = 'phpbb_warnings'

    warning_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, server_default=text("'0'"))
    post_id = Column(Integer, nullable=False, server_default=text("'0'"))
    log_id = Column(Integer, nullable=False, server_default=text("'0'"))
    warning_time = Column(Integer, nullable=False, server_default=text("'0'"))


class PhpbbWord(Base):
    __tablename__ = 'phpbb_words'

    word_id = Column(Integer, primary_key=True)
    word = Column(String(255, u'utf8_bin'), nullable=False,
                  server_default=text("''"))
    replacement = Column(String(255, u'utf8_bin'), nullable=False,
                         server_default=text("''"))


class PhpbbZebra(Base):
    __tablename__ = 'phpbb_zebra'

    user_id = Column(Integer, primary_key=True, nullable=False,
                     server_default=text("'0'"))
    zebra_id = Column(Integer, primary_key=True, nullable=False,
                      server_default=text("'0'"))
    friend = Column(Integer, nullable=False, server_default=text("'0'"))
    foe = Column(Integer, nullable=False, server_default=text("'0'"))
