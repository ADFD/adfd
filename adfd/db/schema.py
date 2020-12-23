# coding: utf-8
from sqlalchemy import Column, Index, Integer, Table, text
from sqlalchemy.dialects.mysql import (
    CHAR,
    INTEGER,
    MEDIUMINT,
    MEDIUMTEXT,
    SMALLINT,
    TEXT,
    TINYINT,
    VARCHAR,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


t_phpbb_acl_groups = Table(
    "phpbb_acl_groups",
    metadata,
    Column(
        "group_id", MEDIUMINT, nullable=False, index=True, server_default=text("'0'")
    ),
    Column("forum_id", MEDIUMINT, nullable=False, server_default=text("'0'")),
    Column(
        "auth_option_id",
        MEDIUMINT,
        nullable=False,
        index=True,
        server_default=text("'0'"),
    ),
    Column(
        "auth_role_id",
        MEDIUMINT,
        nullable=False,
        index=True,
        server_default=text("'0'"),
    ),
    Column("auth_setting", TINYINT, nullable=False, server_default=text("'0'")),
)


class PhpbbAclOption(Base):
    __tablename__ = "phpbb_acl_options"

    auth_option_id = Column(MEDIUMINT, primary_key=True)
    auth_option = Column(
        VARCHAR(50), nullable=False, unique=True, server_default=text("''")
    )
    is_global = Column(TINYINT, nullable=False, server_default=text("'0'"))
    is_local = Column(TINYINT, nullable=False, server_default=text("'0'"))
    founder_only = Column(TINYINT, nullable=False, server_default=text("'0'"))


class PhpbbAclRole(Base):
    __tablename__ = "phpbb_acl_roles"

    role_id = Column(MEDIUMINT, primary_key=True)
    role_name = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    role_description = Column(TEXT, nullable=False)
    role_type = Column(
        VARCHAR(10), nullable=False, index=True, server_default=text("''")
    )
    role_order = Column(
        SMALLINT, nullable=False, index=True, server_default=text("'0'")
    )


class PhpbbAclRolesDatum(Base):
    __tablename__ = "phpbb_acl_roles_data"

    role_id = Column(
        MEDIUMINT, primary_key=True, nullable=False, server_default=text("'0'")
    )
    auth_option_id = Column(
        MEDIUMINT,
        primary_key=True,
        nullable=False,
        index=True,
        server_default=text("'0'"),
    )
    auth_setting = Column(TINYINT, nullable=False, server_default=text("'0'"))


t_phpbb_acl_users = Table(
    "phpbb_acl_users",
    metadata,
    Column("user_id", INTEGER, nullable=False, index=True, server_default=text("'0'")),
    Column("forum_id", MEDIUMINT, nullable=False, server_default=text("'0'")),
    Column(
        "auth_option_id",
        MEDIUMINT,
        nullable=False,
        index=True,
        server_default=text("'0'"),
    ),
    Column(
        "auth_role_id",
        MEDIUMINT,
        nullable=False,
        index=True,
        server_default=text("'0'"),
    ),
    Column("auth_setting", TINYINT, nullable=False, server_default=text("'0'")),
)


class PhpbbAttachment(Base):
    __tablename__ = "phpbb_attachments"

    attach_id = Column(INTEGER, primary_key=True)
    post_msg_id = Column(
        INTEGER, nullable=False, index=True, server_default=text("'0'")
    )
    topic_id = Column(INTEGER, nullable=False, index=True, server_default=text("'0'"))
    in_message = Column(TINYINT, nullable=False, server_default=text("'0'"))
    poster_id = Column(INTEGER, nullable=False, index=True, server_default=text("'0'"))
    is_orphan = Column(TINYINT, nullable=False, index=True, server_default=text("'1'"))
    physical_filename = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    real_filename = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    download_count = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    attach_comment = Column(TEXT, nullable=False)
    extension = Column(VARCHAR(100), nullable=False, server_default=text("''"))
    mimetype = Column(VARCHAR(100), nullable=False, server_default=text("''"))
    filesize = Column(INTEGER, nullable=False, server_default=text("'0'"))
    filetime = Column(INTEGER, nullable=False, index=True, server_default=text("'0'"))
    thumbnail = Column(TINYINT, nullable=False, server_default=text("'0'"))


class PhpbbBanlist(Base):
    __tablename__ = "phpbb_banlist"
    __table_args__ = (
        Index("ban_ip", "ban_ip", "ban_exclude"),
        Index("ban_email", "ban_email", "ban_exclude"),
        Index("ban_user", "ban_userid", "ban_exclude"),
    )

    ban_id = Column(INTEGER, primary_key=True)
    ban_userid = Column(INTEGER, nullable=False, server_default=text("'0'"))
    ban_ip = Column(VARCHAR(40), nullable=False, server_default=text("''"))
    ban_email = Column(VARCHAR(100), nullable=False, server_default=text("''"))
    ban_start = Column(INTEGER, nullable=False, server_default=text("'0'"))
    ban_end = Column(INTEGER, nullable=False, index=True, server_default=text("'0'"))
    ban_exclude = Column(TINYINT, nullable=False, server_default=text("'0'"))
    ban_reason = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    ban_give_reason = Column(VARCHAR(255), nullable=False, server_default=text("''"))


class PhpbbBbcode(Base):
    __tablename__ = "phpbb_bbcodes"

    bbcode_id = Column(SMALLINT, primary_key=True, server_default=text("'0'"))
    bbcode_tag = Column(VARCHAR(16), nullable=False, server_default=text("''"))
    bbcode_helpline = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    display_on_posting = Column(
        TINYINT, nullable=False, index=True, server_default=text("'0'")
    )
    bbcode_match = Column(TEXT, nullable=False)
    bbcode_tpl = Column(MEDIUMTEXT, nullable=False)
    first_pass_match = Column(MEDIUMTEXT, nullable=False)
    first_pass_replace = Column(MEDIUMTEXT, nullable=False)
    second_pass_match = Column(MEDIUMTEXT, nullable=False)
    second_pass_replace = Column(MEDIUMTEXT, nullable=False)
    bbcode_order = Column(SMALLINT, nullable=False, server_default=text("'0'"))
    bbcode_group = Column(VARCHAR(255), nullable=False, server_default=text("''"))


class PhpbbBoardrule(Base):
    __tablename__ = "phpbb_boardrules"

    rule_id = Column(MEDIUMINT, primary_key=True)
    rule_language = Column(
        VARCHAR(30), nullable=False, index=True, server_default=text("''")
    )
    rule_left_id = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    rule_right_id = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    rule_parent_id = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    rule_anchor = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    rule_title = Column(VARCHAR(200), nullable=False, server_default=text("''"))
    rule_message = Column(MEDIUMTEXT, nullable=False)
    rule_message_bbcode_uid = Column(
        VARCHAR(8), nullable=False, server_default=text("''")
    )
    rule_message_bbcode_bitfield = Column(
        VARCHAR(255), nullable=False, server_default=text("''")
    )
    rule_message_bbcode_options = Column(
        INTEGER, nullable=False, server_default=text("'7'")
    )
    rule_parents = Column(MEDIUMTEXT, nullable=False)


class PhpbbBookmark(Base):
    __tablename__ = "phpbb_bookmarks"

    topic_id = Column(
        INTEGER, primary_key=True, nullable=False, server_default=text("'0'")
    )
    user_id = Column(
        INTEGER, primary_key=True, nullable=False, server_default=text("'0'")
    )


class PhpbbBot(Base):
    __tablename__ = "phpbb_bots"

    bot_id = Column(INTEGER, primary_key=True)
    bot_active = Column(TINYINT, nullable=False, index=True, server_default=text("'1'"))
    bot_name = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    user_id = Column(INTEGER, nullable=False, server_default=text("'0'"))
    bot_agent = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    bot_ip = Column(VARCHAR(255), nullable=False, server_default=text("''"))


t_phpbb_captcha_answers = Table(
    "phpbb_captcha_answers",
    metadata,
    Column(
        "question_id", MEDIUMINT, nullable=False, index=True, server_default=text("'0'")
    ),
    Column("answer_text", VARCHAR(255), nullable=False, server_default=text("''")),
)


class PhpbbCaptchaQuestion(Base):
    __tablename__ = "phpbb_captcha_questions"

    question_id = Column(MEDIUMINT, primary_key=True)
    strict = Column(TINYINT, nullable=False, server_default=text("'0'"))
    lang_id = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    lang_iso = Column(
        VARCHAR(30), nullable=False, index=True, server_default=text("''")
    )
    question_text = Column(TEXT, nullable=False)


class PhpbbConfig(Base):
    __tablename__ = "phpbb_config"

    config_name = Column(VARCHAR(255), primary_key=True, server_default=text("''"))
    config_value = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    is_dynamic = Column(TINYINT, nullable=False, index=True, server_default=text("'0'"))


class PhpbbConfigText(Base):
    __tablename__ = "phpbb_config_text"

    config_name = Column(VARCHAR(255), primary_key=True, server_default=text("''"))
    config_value = Column(MEDIUMTEXT, nullable=False)


class PhpbbConfirm(Base):
    __tablename__ = "phpbb_confirm"

    confirm_id = Column(
        CHAR(32), primary_key=True, nullable=False, server_default=text("''")
    )
    session_id = Column(
        CHAR(32), primary_key=True, nullable=False, server_default=text("''")
    )
    confirm_type = Column(
        TINYINT, nullable=False, index=True, server_default=text("'0'")
    )
    code = Column(VARCHAR(8), nullable=False, server_default=text("''"))
    seed = Column(INTEGER, nullable=False, server_default=text("'0'"))
    attempts = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))


class PhpbbDisallow(Base):
    __tablename__ = "phpbb_disallow"

    disallow_id = Column(MEDIUMINT, primary_key=True)
    disallow_username = Column(VARCHAR(255), nullable=False, server_default=text("''"))


class PhpbbDraft(Base):
    __tablename__ = "phpbb_drafts"

    draft_id = Column(INTEGER, primary_key=True)
    user_id = Column(INTEGER, nullable=False, server_default=text("'0'"))
    topic_id = Column(INTEGER, nullable=False, server_default=text("'0'"))
    forum_id = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    save_time = Column(INTEGER, nullable=False, index=True, server_default=text("'0'"))
    draft_subject = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    draft_message = Column(MEDIUMTEXT, nullable=False)


t_phpbb_ext = Table(
    "phpbb_ext",
    metadata,
    Column(
        "ext_name", VARCHAR(255), nullable=False, unique=True, server_default=text("''")
    ),
    Column("ext_active", TINYINT, nullable=False, server_default=text("'0'")),
    Column("ext_state", TEXT, nullable=False),
)


class PhpbbExtensionGroup(Base):
    __tablename__ = "phpbb_extension_groups"

    group_id = Column(MEDIUMINT, primary_key=True)
    group_name = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    cat_id = Column(TINYINT, nullable=False, server_default=text("'0'"))
    allow_group = Column(TINYINT, nullable=False, server_default=text("'0'"))
    download_mode = Column(TINYINT, nullable=False, server_default=text("'1'"))
    upload_icon = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    max_filesize = Column(INTEGER, nullable=False, server_default=text("'0'"))
    allowed_forums = Column(TEXT, nullable=False)
    allow_in_pm = Column(TINYINT, nullable=False, server_default=text("'0'"))


class PhpbbExtension(Base):
    __tablename__ = "phpbb_extensions"

    extension_id = Column(MEDIUMINT, primary_key=True)
    group_id = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    extension = Column(VARCHAR(100), nullable=False, server_default=text("''"))


class PhpbbForum(Base):
    __tablename__ = "phpbb_forums"
    __table_args__ = (Index("left_right_id", "left_id", "right_id"),)

    forum_id = Column(MEDIUMINT, primary_key=True)
    parent_id = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    left_id = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    right_id = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    forum_parents = Column(MEDIUMTEXT, nullable=False)
    forum_name = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    forum_desc = Column(TEXT, nullable=False)
    forum_desc_bitfield = Column(
        VARCHAR(255), nullable=False, server_default=text("''")
    )
    forum_desc_options = Column(INTEGER, nullable=False, server_default=text("'7'"))
    forum_desc_uid = Column(VARCHAR(8), nullable=False, server_default=text("''"))
    forum_link = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    forum_password = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    forum_style = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    forum_image = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    forum_rules = Column(TEXT, nullable=False)
    forum_rules_link = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    forum_rules_bitfield = Column(
        VARCHAR(255), nullable=False, server_default=text("''")
    )
    forum_rules_options = Column(INTEGER, nullable=False, server_default=text("'7'"))
    forum_rules_uid = Column(VARCHAR(8), nullable=False, server_default=text("''"))
    forum_topics_per_page = Column(SMALLINT, nullable=False, server_default=text("'0'"))
    forum_type = Column(TINYINT, nullable=False, server_default=text("'0'"))
    forum_status = Column(TINYINT, nullable=False, server_default=text("'0'"))
    forum_last_post_id = Column(
        INTEGER, nullable=False, index=True, server_default=text("'0'")
    )
    forum_last_poster_id = Column(INTEGER, nullable=False, server_default=text("'0'"))
    forum_last_post_subject = Column(
        VARCHAR(255), nullable=False, server_default=text("''")
    )
    forum_last_post_time = Column(INTEGER, nullable=False, server_default=text("'0'"))
    forum_last_poster_name = Column(
        VARCHAR(255), nullable=False, server_default=text("''")
    )
    forum_last_poster_colour = Column(
        VARCHAR(6), nullable=False, server_default=text("''")
    )
    forum_flags = Column(TINYINT, nullable=False, server_default=text("'32'"))
    display_subforum_list = Column(TINYINT, nullable=False, server_default=text("'1'"))
    display_subforum_limit = Column(TINYINT, nullable=False, server_default=text("'0'"))
    display_on_index = Column(TINYINT, nullable=False, server_default=text("'1'"))
    enable_indexing = Column(TINYINT, nullable=False, server_default=text("'1'"))
    enable_icons = Column(TINYINT, nullable=False, server_default=text("'1'"))
    enable_prune = Column(TINYINT, nullable=False, server_default=text("'0'"))
    prune_next = Column(INTEGER, nullable=False, server_default=text("'0'"))
    prune_days = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    prune_viewed = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    prune_freq = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    forum_options = Column(INTEGER, nullable=False, server_default=text("'0'"))
    enable_reputation = Column(TINYINT, nullable=False, server_default=text("'0'"))
    forum_posts_approved = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    forum_posts_unapproved = Column(
        MEDIUMINT, nullable=False, server_default=text("'0'")
    )
    forum_posts_softdeleted = Column(
        MEDIUMINT, nullable=False, server_default=text("'0'")
    )
    forum_topics_approved = Column(
        MEDIUMINT, nullable=False, server_default=text("'0'")
    )
    forum_topics_unapproved = Column(
        MEDIUMINT, nullable=False, server_default=text("'0'")
    )
    forum_topics_softdeleted = Column(
        MEDIUMINT, nullable=False, server_default=text("'0'")
    )
    enable_shadow_prune = Column(TINYINT, nullable=False, server_default=text("'0'"))
    prune_shadow_days = Column(MEDIUMINT, nullable=False, server_default=text("'7'"))
    prune_shadow_freq = Column(MEDIUMINT, nullable=False, server_default=text("'1'"))
    prune_shadow_next = Column(Integer, nullable=False, server_default=text("'0'"))


class PhpbbForumsAcces(Base):
    __tablename__ = "phpbb_forums_access"

    forum_id = Column(
        MEDIUMINT, primary_key=True, nullable=False, server_default=text("'0'")
    )
    user_id = Column(
        INTEGER, primary_key=True, nullable=False, server_default=text("'0'")
    )
    session_id = Column(
        CHAR(32), primary_key=True, nullable=False, server_default=text("''")
    )


class PhpbbForumsTrack(Base):
    __tablename__ = "phpbb_forums_track"

    user_id = Column(
        INTEGER, primary_key=True, nullable=False, server_default=text("'0'")
    )
    forum_id = Column(
        MEDIUMINT, primary_key=True, nullable=False, server_default=text("'0'")
    )
    mark_time = Column(INTEGER, nullable=False, server_default=text("'0'"))


t_phpbb_forums_watch = Table(
    "phpbb_forums_watch",
    metadata,
    Column(
        "forum_id", MEDIUMINT, nullable=False, index=True, server_default=text("'0'")
    ),
    Column("user_id", INTEGER, nullable=False, index=True, server_default=text("'0'")),
    Column(
        "notify_status", TINYINT, nullable=False, index=True, server_default=text("'0'")
    ),
)


class PhpbbGroup(Base):
    __tablename__ = "phpbb_groups"
    __table_args__ = (Index("group_legend_name", "group_legend", "group_name"),)

    group_id = Column(MEDIUMINT, primary_key=True)
    group_type = Column(TINYINT, nullable=False, server_default=text("'1'"))
    group_founder_manage = Column(TINYINT, nullable=False, server_default=text("'0'"))
    group_name = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    group_desc = Column(TEXT, nullable=False)
    group_desc_bitfield = Column(
        VARCHAR(255), nullable=False, server_default=text("''")
    )
    group_desc_options = Column(INTEGER, nullable=False, server_default=text("'7'"))
    group_desc_uid = Column(VARCHAR(8), nullable=False, server_default=text("''"))
    group_display = Column(TINYINT, nullable=False, server_default=text("'0'"))
    group_avatar = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    group_avatar_type = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    group_avatar_width = Column(SMALLINT, nullable=False, server_default=text("'0'"))
    group_avatar_height = Column(SMALLINT, nullable=False, server_default=text("'0'"))
    group_rank = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    group_colour = Column(VARCHAR(6), nullable=False, server_default=text("''"))
    group_sig_chars = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    group_receive_pm = Column(TINYINT, nullable=False, server_default=text("'0'"))
    group_message_limit = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    group_legend = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    group_max_recipients = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    group_skip_auth = Column(TINYINT, nullable=False, server_default=text("'0'"))
    group_reputation_power = Column(
        MEDIUMINT, nullable=False, server_default=text("'0'")
    )


class PhpbbIcon(Base):
    __tablename__ = "phpbb_icons"

    icons_id = Column(MEDIUMINT, primary_key=True)
    icons_url = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    icons_width = Column(TINYINT, nullable=False, server_default=text("'0'"))
    icons_height = Column(TINYINT, nullable=False, server_default=text("'0'"))
    icons_alt = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    icons_order = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    display_on_posting = Column(
        TINYINT, nullable=False, index=True, server_default=text("'1'")
    )


class PhpbbLang(Base):
    __tablename__ = "phpbb_lang"

    lang_id = Column(TINYINT, primary_key=True)
    lang_iso = Column(
        VARCHAR(30), nullable=False, index=True, server_default=text("''")
    )
    lang_dir = Column(VARCHAR(30), nullable=False, server_default=text("''"))
    lang_english_name = Column(VARCHAR(100), nullable=False, server_default=text("''"))
    lang_local_name = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    lang_author = Column(VARCHAR(255), nullable=False, server_default=text("''"))


class PhpbbLog(Base):
    __tablename__ = "phpbb_log"

    log_id = Column(INTEGER, primary_key=True)
    log_type = Column(TINYINT, nullable=False, index=True, server_default=text("'0'"))
    user_id = Column(INTEGER, nullable=False, index=True, server_default=text("'0'"))
    forum_id = Column(MEDIUMINT, nullable=False, index=True, server_default=text("'0'"))
    topic_id = Column(INTEGER, nullable=False, index=True, server_default=text("'0'"))
    post_id = Column(INTEGER, nullable=False, server_default=text("'0'"))
    reportee_id = Column(
        INTEGER, nullable=False, index=True, server_default=text("'0'")
    )
    log_ip = Column(VARCHAR(40), nullable=False, server_default=text("''"))
    log_time = Column(INTEGER, nullable=False, index=True, server_default=text("'0'"))
    log_operation = Column(TEXT, nullable=False)
    log_data = Column(MEDIUMTEXT, nullable=False)


t_phpbb_login_attempts = Table(
    "phpbb_login_attempts",
    metadata,
    Column("attempt_ip", VARCHAR(40), nullable=False, server_default=text("''")),
    Column("attempt_browser", VARCHAR(150), nullable=False, server_default=text("''")),
    Column(
        "attempt_forwarded_for", VARCHAR(255), nullable=False, server_default=text("''")
    ),
    Column(
        "attempt_time", INTEGER, nullable=False, index=True, server_default=text("'0'")
    ),
    Column("user_id", INTEGER, nullable=False, index=True, server_default=text("'0'")),
    Column("username", VARCHAR(255), nullable=False, server_default=text("'0'")),
    Column("username_clean", VARCHAR(255), nullable=False, server_default=text("'0'")),
    Index("att_for", "attempt_forwarded_for", "attempt_time"),
    Index("att_ip", "attempt_ip", "attempt_time"),
)


class PhpbbMigration(Base):
    __tablename__ = "phpbb_migrations"

    migration_name = Column(VARCHAR(255), primary_key=True, server_default=text("''"))
    migration_depends_on = Column(TEXT, nullable=False)
    migration_schema_done = Column(TINYINT, nullable=False, server_default=text("'0'"))
    migration_data_done = Column(TINYINT, nullable=False, server_default=text("'0'"))
    migration_data_state = Column(TEXT, nullable=False)
    migration_start_time = Column(INTEGER, nullable=False, server_default=text("'0'"))
    migration_end_time = Column(INTEGER, nullable=False, server_default=text("'0'"))


t_phpbb_moderator_cache = Table(
    "phpbb_moderator_cache",
    metadata,
    Column(
        "forum_id", MEDIUMINT, nullable=False, index=True, server_default=text("'0'")
    ),
    Column("user_id", INTEGER, nullable=False, server_default=text("'0'")),
    Column("username", VARCHAR(255), nullable=False, server_default=text("''")),
    Column("group_id", MEDIUMINT, nullable=False, server_default=text("'0'")),
    Column("group_name", VARCHAR(255), nullable=False, server_default=text("''")),
    Column(
        "display_on_index",
        TINYINT,
        nullable=False,
        index=True,
        server_default=text("'1'"),
    ),
)


class PhpbbModule(Base):
    __tablename__ = "phpbb_modules"
    __table_args__ = (
        Index("class_left_id", "module_class", "left_id"),
        Index("left_right_id", "left_id", "right_id"),
    )

    module_id = Column(MEDIUMINT, primary_key=True)
    module_enabled = Column(
        TINYINT, nullable=False, index=True, server_default=text("'1'")
    )
    module_display = Column(TINYINT, nullable=False, server_default=text("'1'"))
    module_basename = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    module_class = Column(VARCHAR(10), nullable=False, server_default=text("''"))
    parent_id = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    left_id = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    right_id = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    module_langname = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    module_mode = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    module_auth = Column(VARCHAR(255), nullable=False, server_default=text("''"))


class PhpbbNotificationEmail(Base):
    __tablename__ = "phpbb_notification_emails"

    notification_type_id = Column(
        SMALLINT, primary_key=True, nullable=False, server_default=text("'0'")
    )
    item_id = Column(
        INTEGER, primary_key=True, nullable=False, server_default=text("'0'")
    )
    item_parent_id = Column(
        INTEGER, primary_key=True, nullable=False, server_default=text("'0'")
    )
    user_id = Column(
        INTEGER, primary_key=True, nullable=False, server_default=text("'0'")
    )


class PhpbbNotificationType(Base):
    __tablename__ = "phpbb_notification_types"

    notification_type_id = Column(SMALLINT, primary_key=True)
    notification_type_name = Column(
        VARCHAR(255), nullable=False, unique=True, server_default=text("''")
    )
    notification_type_enabled = Column(
        TINYINT, nullable=False, server_default=text("'1'")
    )


class PhpbbNotification(Base):
    __tablename__ = "phpbb_notifications"
    __table_args__ = (
        Index("user", "user_id", "notification_read"),
        Index("item_ident", "notification_type_id", "item_id"),
    )

    notification_id = Column(INTEGER, primary_key=True)
    notification_type_id = Column(SMALLINT, nullable=False, server_default=text("'0'"))
    item_id = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    item_parent_id = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    user_id = Column(INTEGER, nullable=False, server_default=text("'0'"))
    notification_read = Column(TINYINT, nullable=False, server_default=text("'0'"))
    notification_time = Column(INTEGER, nullable=False, server_default=text("'1'"))
    notification_data = Column(TEXT, nullable=False)


class PhpbbOauthAccount(Base):
    __tablename__ = "phpbb_oauth_accounts"

    user_id = Column(
        INTEGER, primary_key=True, nullable=False, server_default=text("'0'")
    )
    provider = Column(
        VARCHAR(255), primary_key=True, nullable=False, server_default=text("''")
    )
    oauth_provider_id = Column(TEXT, nullable=False)


t_phpbb_oauth_states = Table(
    "phpbb_oauth_states",
    metadata,
    Column("user_id", INTEGER, nullable=False, index=True, server_default=text("'0'")),
    Column("session_id", CHAR(32), nullable=False, server_default=text("''")),
    Column(
        "provider", VARCHAR(255), nullable=False, index=True, server_default=text("''")
    ),
    Column("oauth_state", VARCHAR(255), nullable=False, server_default=text("''")),
)


t_phpbb_oauth_tokens = Table(
    "phpbb_oauth_tokens",
    metadata,
    Column("user_id", INTEGER, nullable=False, index=True, server_default=text("'0'")),
    Column("session_id", CHAR(32), nullable=False, server_default=text("''")),
    Column(
        "provider", VARCHAR(255), nullable=False, index=True, server_default=text("''")
    ),
    Column("oauth_token", MEDIUMTEXT, nullable=False),
)


t_phpbb_poll_options = Table(
    "phpbb_poll_options",
    metadata,
    Column(
        "poll_option_id",
        TINYINT,
        nullable=False,
        index=True,
        server_default=text("'0'"),
    ),
    Column("topic_id", INTEGER, nullable=False, index=True, server_default=text("'0'")),
    Column("poll_option_text", TEXT, nullable=False),
    Column("poll_option_total", MEDIUMINT, nullable=False, server_default=text("'0'")),
)


t_phpbb_poll_votes = Table(
    "phpbb_poll_votes",
    metadata,
    Column("topic_id", INTEGER, nullable=False, index=True, server_default=text("'0'")),
    Column("poll_option_id", TINYINT, nullable=False, server_default=text("'0'")),
    Column(
        "vote_user_id", INTEGER, nullable=False, index=True, server_default=text("'0'")
    ),
    Column(
        "vote_user_ip",
        VARCHAR(40),
        nullable=False,
        index=True,
        server_default=text("''"),
    ),
)


class PhpbbPost(Base):
    __tablename__ = "phpbb_posts"
    __table_args__ = (
        Index("post_content", "post_text", "post_subject"),
        Index("tid_post_time", "topic_id", "post_time"),
    )

    post_id = Column(INTEGER, primary_key=True)
    topic_id = Column(INTEGER, nullable=False, index=True, server_default=text("'0'"))
    forum_id = Column(MEDIUMINT, nullable=False, index=True, server_default=text("'0'"))
    poster_id = Column(INTEGER, nullable=False, index=True, server_default=text("'0'"))
    icon_id = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    poster_ip = Column(
        VARCHAR(40), nullable=False, index=True, server_default=text("''")
    )
    post_time = Column(INTEGER, nullable=False, server_default=text("'0'"))
    post_reported = Column(TINYINT, nullable=False, server_default=text("'0'"))
    enable_bbcode = Column(TINYINT, nullable=False, server_default=text("'1'"))
    enable_smilies = Column(TINYINT, nullable=False, server_default=text("'1'"))
    enable_magic_url = Column(TINYINT, nullable=False, server_default=text("'1'"))
    enable_sig = Column(TINYINT, nullable=False, server_default=text("'1'"))
    post_username = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    post_subject = Column(
        VARCHAR(255), nullable=False, index=True, server_default=text("''")
    )
    post_text = Column(MEDIUMTEXT, nullable=False, index=True)
    post_checksum = Column(VARCHAR(32), nullable=False, server_default=text("''"))
    post_attachment = Column(TINYINT, nullable=False, server_default=text("'0'"))
    bbcode_bitfield = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    bbcode_uid = Column(VARCHAR(8), nullable=False, server_default=text("''"))
    post_postcount = Column(TINYINT, nullable=False, server_default=text("'1'"))
    post_edit_time = Column(INTEGER, nullable=False, server_default=text("'0'"))
    post_edit_reason = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    post_edit_user = Column(INTEGER, nullable=False, server_default=text("'0'"))
    post_edit_count = Column(SMALLINT, nullable=False, server_default=text("'0'"))
    post_edit_locked = Column(TINYINT, nullable=False, server_default=text("'0'"))
    post_reputation = Column(Integer, nullable=False, server_default=text("'0'"))
    post_visibility = Column(
        TINYINT, nullable=False, index=True, server_default=text("'0'")
    )
    post_delete_time = Column(INTEGER, nullable=False, server_default=text("'0'"))
    post_delete_reason = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    post_delete_user = Column(INTEGER, nullable=False, server_default=text("'0'"))


class PhpbbPrivmsg(Base):
    __tablename__ = "phpbb_privmsgs"

    msg_id = Column(INTEGER, primary_key=True)
    root_level = Column(
        MEDIUMINT, nullable=False, index=True, server_default=text("'0'")
    )
    author_id = Column(INTEGER, nullable=False, index=True, server_default=text("'0'"))
    icon_id = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    author_ip = Column(
        VARCHAR(40), nullable=False, index=True, server_default=text("''")
    )
    message_time = Column(
        INTEGER, nullable=False, index=True, server_default=text("'0'")
    )
    enable_bbcode = Column(TINYINT, nullable=False, server_default=text("'1'"))
    enable_smilies = Column(TINYINT, nullable=False, server_default=text("'1'"))
    enable_magic_url = Column(TINYINT, nullable=False, server_default=text("'1'"))
    enable_sig = Column(TINYINT, nullable=False, server_default=text("'1'"))
    message_subject = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    message_text = Column(MEDIUMTEXT, nullable=False)
    message_edit_reason = Column(
        VARCHAR(255), nullable=False, server_default=text("''")
    )
    message_edit_user = Column(INTEGER, nullable=False, server_default=text("'0'"))
    message_attachment = Column(TINYINT, nullable=False, server_default=text("'0'"))
    bbcode_bitfield = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    bbcode_uid = Column(VARCHAR(8), nullable=False, server_default=text("''"))
    message_edit_time = Column(INTEGER, nullable=False, server_default=text("'0'"))
    message_edit_count = Column(SMALLINT, nullable=False, server_default=text("'0'"))
    to_address = Column(TEXT, nullable=False)
    bcc_address = Column(TEXT, nullable=False)
    message_reported = Column(TINYINT, nullable=False, server_default=text("'0'"))


class PhpbbPrivmsgsFolder(Base):
    __tablename__ = "phpbb_privmsgs_folder"

    folder_id = Column(MEDIUMINT, primary_key=True)
    user_id = Column(INTEGER, nullable=False, index=True, server_default=text("'0'"))
    folder_name = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    pm_count = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))


class PhpbbPrivmsgsRule(Base):
    __tablename__ = "phpbb_privmsgs_rules"

    rule_id = Column(MEDIUMINT, primary_key=True)
    user_id = Column(INTEGER, nullable=False, index=True, server_default=text("'0'"))
    rule_check = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    rule_connection = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    rule_string = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    rule_user_id = Column(INTEGER, nullable=False, server_default=text("'0'"))
    rule_group_id = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    rule_action = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    rule_folder_id = Column(Integer, nullable=False, server_default=text("'0'"))


t_phpbb_privmsgs_to = Table(
    "phpbb_privmsgs_to",
    metadata,
    Column("msg_id", INTEGER, nullable=False, index=True, server_default=text("'0'")),
    Column("user_id", INTEGER, nullable=False, server_default=text("'0'")),
    Column(
        "author_id", INTEGER, nullable=False, index=True, server_default=text("'0'")
    ),
    Column("pm_deleted", TINYINT, nullable=False, server_default=text("'0'")),
    Column("pm_new", TINYINT, nullable=False, server_default=text("'1'")),
    Column("pm_unread", TINYINT, nullable=False, server_default=text("'1'")),
    Column("pm_replied", TINYINT, nullable=False, server_default=text("'0'")),
    Column("pm_marked", TINYINT, nullable=False, server_default=text("'0'")),
    Column("pm_forwarded", TINYINT, nullable=False, server_default=text("'0'")),
    Column("folder_id", Integer, nullable=False, server_default=text("'0'")),
    Index("usr_flder_id", "user_id", "folder_id"),
)


class PhpbbProfileField(Base):
    __tablename__ = "phpbb_profile_fields"

    field_id = Column(MEDIUMINT, primary_key=True)
    field_name = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    field_type = Column(
        VARCHAR(100), nullable=False, index=True, server_default=text("''")
    )
    field_ident = Column(VARCHAR(20), nullable=False, server_default=text("''"))
    field_length = Column(VARCHAR(20), nullable=False, server_default=text("''"))
    field_minlen = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    field_maxlen = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    field_novalue = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    field_default_value = Column(
        VARCHAR(255), nullable=False, server_default=text("''")
    )
    field_validation = Column(VARCHAR(64), nullable=False, server_default=text("''"))
    field_required = Column(TINYINT, nullable=False, server_default=text("'0'"))
    field_show_on_reg = Column(TINYINT, nullable=False, server_default=text("'0'"))
    field_hide = Column(TINYINT, nullable=False, server_default=text("'0'"))
    field_no_view = Column(TINYINT, nullable=False, server_default=text("'0'"))
    field_active = Column(TINYINT, nullable=False, server_default=text("'0'"))
    field_order = Column(
        MEDIUMINT, nullable=False, index=True, server_default=text("'0'")
    )
    field_show_profile = Column(TINYINT, nullable=False, server_default=text("'0'"))
    field_show_on_vt = Column(TINYINT, nullable=False, server_default=text("'0'"))
    field_show_novalue = Column(TINYINT, nullable=False, server_default=text("'0'"))
    field_show_on_pm = Column(TINYINT, nullable=False, server_default=text("'0'"))
    field_show_on_ml = Column(TINYINT, nullable=False, server_default=text("'0'"))
    field_is_contact = Column(TINYINT, nullable=False, server_default=text("'0'"))
    field_contact_desc = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    field_contact_url = Column(VARCHAR(255), nullable=False, server_default=text("''"))


class PhpbbProfileFieldsDatum(Base):
    __tablename__ = "phpbb_profile_fields_data"

    user_id = Column(INTEGER, primary_key=True, server_default=text("'0'"))
    pf_phpbb_interests = Column(MEDIUMTEXT, nullable=False)
    pf_phpbb_occupation = Column(MEDIUMTEXT, nullable=False)
    pf_phpbb_icq = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    pf_phpbb_website = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    pf_phpbb_yahoo = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    pf_phpbb_location = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    pf_phpbb_facebook = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    pf_phpbb_skype = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    pf_phpbb_twitter = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    pf_phpbb_youtube = Column(VARCHAR(255), nullable=False, server_default=text("''"))


class PhpbbProfileFieldsLang(Base):
    __tablename__ = "phpbb_profile_fields_lang"

    field_id = Column(
        MEDIUMINT, primary_key=True, nullable=False, server_default=text("'0'")
    )
    lang_id = Column(
        MEDIUMINT, primary_key=True, nullable=False, server_default=text("'0'")
    )
    option_id = Column(
        MEDIUMINT, primary_key=True, nullable=False, server_default=text("'0'")
    )
    field_type = Column(VARCHAR(100), nullable=False, server_default=text("''"))
    lang_value = Column(VARCHAR(255), nullable=False, server_default=text("''"))


class PhpbbProfileLang(Base):
    __tablename__ = "phpbb_profile_lang"

    field_id = Column(
        MEDIUMINT, primary_key=True, nullable=False, server_default=text("'0'")
    )
    lang_id = Column(
        MEDIUMINT, primary_key=True, nullable=False, server_default=text("'0'")
    )
    lang_name = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    lang_explain = Column(TEXT, nullable=False)
    lang_default_value = Column(VARCHAR(255), nullable=False, server_default=text("''"))


class PhpbbQaConfirm(Base):
    __tablename__ = "phpbb_qa_confirm"
    __table_args__ = (Index("lookup", "confirm_id", "session_id", "lang_iso"),)

    session_id = Column(CHAR(32), nullable=False, index=True, server_default=text("''"))
    confirm_id = Column(CHAR(32), primary_key=True, server_default=text("''"))
    lang_iso = Column(VARCHAR(30), nullable=False, server_default=text("''"))
    question_id = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    attempts = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    confirm_type = Column(SMALLINT, nullable=False, server_default=text("'0'"))


class PhpbbRank(Base):
    __tablename__ = "phpbb_ranks"

    rank_id = Column(MEDIUMINT, primary_key=True)
    rank_title = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    rank_min = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    rank_special = Column(TINYINT, nullable=False, server_default=text("'0'"))
    rank_image = Column(VARCHAR(255), nullable=False, server_default=text("''"))


class PhpbbReport(Base):
    __tablename__ = "phpbb_reports"

    report_id = Column(INTEGER, primary_key=True)
    reason_id = Column(SMALLINT, nullable=False, server_default=text("'0'"))
    post_id = Column(INTEGER, nullable=False, index=True, server_default=text("'0'"))
    user_id = Column(INTEGER, nullable=False, server_default=text("'0'"))
    user_notify = Column(TINYINT, nullable=False, server_default=text("'0'"))
    report_closed = Column(TINYINT, nullable=False, server_default=text("'0'"))
    report_time = Column(INTEGER, nullable=False, server_default=text("'0'"))
    report_text = Column(MEDIUMTEXT, nullable=False)
    pm_id = Column(INTEGER, nullable=False, index=True, server_default=text("'0'"))
    reported_post_enable_bbcode = Column(
        TINYINT, nullable=False, server_default=text("'1'")
    )
    reported_post_enable_smilies = Column(
        TINYINT, nullable=False, server_default=text("'1'")
    )
    reported_post_enable_magic_url = Column(
        TINYINT, nullable=False, server_default=text("'1'")
    )
    reported_post_text = Column(MEDIUMTEXT, nullable=False)
    reported_post_uid = Column(VARCHAR(8), nullable=False, server_default=text("''"))
    reported_post_bitfield = Column(
        VARCHAR(255), nullable=False, server_default=text("''")
    )


class PhpbbReportsReason(Base):
    __tablename__ = "phpbb_reports_reasons"

    reason_id = Column(SMALLINT, primary_key=True)
    reason_title = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    reason_description = Column(MEDIUMTEXT, nullable=False)
    reason_order = Column(SMALLINT, nullable=False, server_default=text("'0'"))


class PhpbbSearchResult(Base):
    __tablename__ = "phpbb_search_results"

    search_key = Column(VARCHAR(32), primary_key=True, server_default=text("''"))
    search_time = Column(INTEGER, nullable=False, server_default=text("'0'"))
    search_keywords = Column(MEDIUMTEXT, nullable=False)
    search_authors = Column(MEDIUMTEXT, nullable=False)


class PhpbbSearchWordlist(Base):
    __tablename__ = "phpbb_search_wordlist"

    word_id = Column(INTEGER, primary_key=True)
    word_text = Column(
        VARCHAR(255), nullable=False, unique=True, server_default=text("''")
    )
    word_common = Column(TINYINT, nullable=False, server_default=text("'0'"))
    word_count = Column(
        MEDIUMINT, nullable=False, index=True, server_default=text("'0'")
    )


t_phpbb_search_wordmatch = Table(
    "phpbb_search_wordmatch",
    metadata,
    Column("post_id", INTEGER, nullable=False, index=True, server_default=text("'0'")),
    Column("word_id", INTEGER, nullable=False, index=True, server_default=text("'0'")),
    Column("title_match", TINYINT, nullable=False, server_default=text("'0'")),
    Index("unq_mtch", "word_id", "post_id", "title_match", unique=True),
    Index("un_mtch", "word_id", "post_id", "title_match", unique=True),
)


class PhpbbSession(Base):
    __tablename__ = "phpbb_sessions"

    session_id = Column(CHAR(32), primary_key=True, server_default=text("''"))
    session_user_id = Column(
        INTEGER, nullable=False, index=True, server_default=text("'0'")
    )
    session_forum_id = Column(
        MEDIUMINT, nullable=False, index=True, server_default=text("'0'")
    )
    session_last_visit = Column(INTEGER, nullable=False, server_default=text("'0'"))
    session_start = Column(INTEGER, nullable=False, server_default=text("'0'"))
    session_time = Column(
        INTEGER, nullable=False, index=True, server_default=text("'0'")
    )
    session_ip = Column(VARCHAR(40), nullable=False, server_default=text("''"))
    session_browser = Column(VARCHAR(150), nullable=False, server_default=text("''"))
    session_forwarded_for = Column(
        VARCHAR(255), nullable=False, server_default=text("''")
    )
    session_page = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    session_viewonline = Column(TINYINT, nullable=False, server_default=text("'1'"))
    session_autologin = Column(TINYINT, nullable=False, server_default=text("'0'"))
    session_admin = Column(TINYINT, nullable=False, server_default=text("'0'"))


class PhpbbSessionsKey(Base):
    __tablename__ = "phpbb_sessions_keys"

    key_id = Column(
        CHAR(32), primary_key=True, nullable=False, server_default=text("''")
    )
    user_id = Column(
        INTEGER, primary_key=True, nullable=False, server_default=text("'0'")
    )
    last_ip = Column(VARCHAR(40), nullable=False, server_default=text("''"))
    last_login = Column(INTEGER, nullable=False, index=True, server_default=text("'0'"))


class PhpbbSitelist(Base):
    __tablename__ = "phpbb_sitelist"

    site_id = Column(MEDIUMINT, primary_key=True)
    site_ip = Column(VARCHAR(40), nullable=False, server_default=text("''"))
    site_hostname = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    ip_exclude = Column(TINYINT, nullable=False, server_default=text("'0'"))


class PhpbbSmily(Base):
    __tablename__ = "phpbb_smilies"

    smiley_id = Column(MEDIUMINT, primary_key=True)
    code = Column(VARCHAR(50), nullable=False, server_default=text("''"))
    emotion = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    smiley_url = Column(VARCHAR(50), nullable=False, server_default=text("''"))
    smiley_width = Column(SMALLINT, nullable=False, server_default=text("'0'"))
    smiley_height = Column(SMALLINT, nullable=False, server_default=text("'0'"))
    smiley_order = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    display_on_posting = Column(
        TINYINT, nullable=False, index=True, server_default=text("'1'")
    )


class PhpbbStyle(Base):
    __tablename__ = "phpbb_styles"

    style_id = Column(MEDIUMINT, primary_key=True)
    style_name = Column(
        VARCHAR(255), nullable=False, unique=True, server_default=text("''")
    )
    style_copyright = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    style_active = Column(TINYINT, nullable=False, server_default=text("'1'"))
    style_path = Column(VARCHAR(100), nullable=False, server_default=text("''"))
    bbcode_bitfield = Column(
        VARCHAR(255), nullable=False, server_default=text("'kNg='")
    )
    style_parent_id = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    style_parent_tree = Column(TEXT, nullable=False)


class PhpbbTeampage(Base):
    __tablename__ = "phpbb_teampage"

    teampage_id = Column(MEDIUMINT, primary_key=True)
    group_id = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    teampage_name = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    teampage_position = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    teampage_parent = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))


class PhpbbThank(Base):
    __tablename__ = "phpbb_thanks"

    post_id = Column(
        MEDIUMINT,
        primary_key=True,
        nullable=False,
        index=True,
        server_default=text("'0'"),
    )
    poster_id = Column(
        MEDIUMINT, nullable=False, index=True, server_default=text("'0'")
    )
    user_id = Column(
        MEDIUMINT,
        primary_key=True,
        nullable=False,
        index=True,
        server_default=text("'0'"),
    )
    topic_id = Column(MEDIUMINT, nullable=False, index=True, server_default=text("'0'"))
    forum_id = Column(MEDIUMINT, nullable=False, index=True, server_default=text("'0'"))
    thanks_time = Column(INTEGER, nullable=False, server_default=text("'0'"))


class PhpbbTopic(Base):
    __tablename__ = "phpbb_topics"
    __table_args__ = (
        Index("forum_id_type", "forum_id", "topic_type"),
        Index(
            "latest_topics",
            "forum_id",
            "topic_last_post_time",
            "topic_last_post_id",
            "topic_moved_id",
        ),
        Index("fid_time_moved", "forum_id", "topic_last_post_time", "topic_moved_id"),
        Index("forum_vis_last", "forum_id", "topic_visibility", "topic_last_post_id"),
    )

    topic_id = Column(INTEGER, primary_key=True)
    forum_id = Column(MEDIUMINT, nullable=False, index=True, server_default=text("'0'"))
    icon_id = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    topic_attachment = Column(TINYINT, nullable=False, server_default=text("'0'"))
    topic_reported = Column(TINYINT, nullable=False, server_default=text("'0'"))
    topic_title = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    topic_poster = Column(INTEGER, nullable=False, server_default=text("'0'"))
    topic_time = Column(INTEGER, nullable=False, server_default=text("'0'"))
    topic_time_limit = Column(INTEGER, nullable=False, server_default=text("'0'"))
    topic_views = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    topic_status = Column(TINYINT, nullable=False, server_default=text("'0'"))
    topic_type = Column(TINYINT, nullable=False, server_default=text("'0'"))
    topic_first_post_id = Column(INTEGER, nullable=False, server_default=text("'0'"))
    topic_first_poster_name = Column(
        VARCHAR(255), nullable=False, server_default=text("''")
    )
    topic_first_poster_colour = Column(
        VARCHAR(6), nullable=False, server_default=text("''")
    )
    topic_last_post_id = Column(INTEGER, nullable=False, server_default=text("'0'"))
    topic_last_poster_id = Column(INTEGER, nullable=False, server_default=text("'0'"))
    topic_last_poster_name = Column(
        VARCHAR(255), nullable=False, server_default=text("''")
    )
    topic_last_poster_colour = Column(
        VARCHAR(6), nullable=False, server_default=text("''")
    )
    topic_last_post_subject = Column(
        VARCHAR(255), nullable=False, server_default=text("''")
    )
    topic_last_post_time = Column(
        INTEGER, nullable=False, index=True, server_default=text("'0'")
    )
    topic_last_view_time = Column(INTEGER, nullable=False, server_default=text("'0'"))
    topic_moved_id = Column(INTEGER, nullable=False, server_default=text("'0'"))
    topic_bumped = Column(TINYINT, nullable=False, server_default=text("'0'"))
    topic_bumper = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    poll_title = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    poll_start = Column(INTEGER, nullable=False, server_default=text("'0'"))
    poll_length = Column(INTEGER, nullable=False, server_default=text("'0'"))
    poll_max_options = Column(TINYINT, nullable=False, server_default=text("'1'"))
    poll_last_vote = Column(INTEGER, nullable=False, server_default=text("'0'"))
    poll_vote_change = Column(TINYINT, nullable=False, server_default=text("'0'"))
    topic_visibility = Column(
        TINYINT, nullable=False, index=True, server_default=text("'0'")
    )
    topic_delete_time = Column(INTEGER, nullable=False, server_default=text("'0'"))
    topic_delete_reason = Column(
        VARCHAR(255), nullable=False, server_default=text("''")
    )
    topic_delete_user = Column(INTEGER, nullable=False, server_default=text("'0'"))
    topic_posts_approved = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    topic_posts_unapproved = Column(
        MEDIUMINT, nullable=False, server_default=text("'0'")
    )
    topic_posts_softdeleted = Column(
        MEDIUMINT, nullable=False, server_default=text("'0'")
    )


class PhpbbTopicsPosted(Base):
    __tablename__ = "phpbb_topics_posted"

    user_id = Column(
        INTEGER, primary_key=True, nullable=False, server_default=text("'0'")
    )
    topic_id = Column(
        INTEGER, primary_key=True, nullable=False, server_default=text("'0'")
    )
    topic_posted = Column(TINYINT, nullable=False, server_default=text("'0'"))


class PhpbbTopicsTrack(Base):
    __tablename__ = "phpbb_topics_track"

    user_id = Column(
        INTEGER, primary_key=True, nullable=False, server_default=text("'0'")
    )
    topic_id = Column(
        INTEGER,
        primary_key=True,
        nullable=False,
        index=True,
        server_default=text("'0'"),
    )
    forum_id = Column(MEDIUMINT, nullable=False, index=True, server_default=text("'0'"))
    mark_time = Column(INTEGER, nullable=False, server_default=text("'0'"))


t_phpbb_topics_watch = Table(
    "phpbb_topics_watch",
    metadata,
    Column("topic_id", INTEGER, nullable=False, index=True, server_default=text("'0'")),
    Column("user_id", INTEGER, nullable=False, index=True, server_default=text("'0'")),
    Column(
        "notify_status", TINYINT, nullable=False, index=True, server_default=text("'0'")
    ),
)


t_phpbb_user_group = Table(
    "phpbb_user_group",
    metadata,
    Column(
        "group_id", MEDIUMINT, nullable=False, index=True, server_default=text("'0'")
    ),
    Column("user_id", INTEGER, nullable=False, index=True, server_default=text("'0'")),
    Column(
        "group_leader", TINYINT, nullable=False, index=True, server_default=text("'0'")
    ),
    Column("user_pending", TINYINT, nullable=False, server_default=text("'1'")),
)


t_phpbb_user_notifications = Table(
    "phpbb_user_notifications",
    metadata,
    Column("item_type", VARCHAR(165), nullable=False, server_default=text("''")),
    Column("item_id", INTEGER, nullable=False, server_default=text("'0'")),
    Column("user_id", INTEGER, nullable=False, index=True, server_default=text("'0'")),
    Column("method", VARCHAR(165), nullable=False, server_default=text("''")),
    Column("notify", TINYINT, nullable=False, server_default=text("'1'")),
    Index("itm_usr_mthd", "item_type", "item_id", "user_id", "method", unique=True),
    Index("usr_itm_tpe", "user_id", "item_type", "item_id"),
    Index("uid_itm_id", "user_id", "item_id"),
)


class PhpbbUser(Base):
    __tablename__ = "phpbb_users"

    user_id = Column(INTEGER, primary_key=True)
    user_type = Column(TINYINT, nullable=False, index=True, server_default=text("'0'"))
    group_id = Column(MEDIUMINT, nullable=False, server_default=text("'3'"))
    user_permissions = Column(MEDIUMTEXT, nullable=False)
    user_perm_from = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    user_ip = Column(VARCHAR(40), nullable=False, server_default=text("''"))
    user_regdate = Column(INTEGER, nullable=False, server_default=text("'0'"))
    username = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    username_clean = Column(
        VARCHAR(255), nullable=False, unique=True, server_default=text("''")
    )
    user_password = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    user_passchg = Column(INTEGER, nullable=False, server_default=text("'0'"))
    user_email = Column(
        VARCHAR(100), nullable=False, index=True, server_default=text("''")
    )
    user_birthday = Column(
        VARCHAR(10), nullable=False, index=True, server_default=text("''")
    )
    user_lastvisit = Column(INTEGER, nullable=False, server_default=text("'0'"))
    user_lastmark = Column(INTEGER, nullable=False, server_default=text("'0'"))
    user_lastpost_time = Column(INTEGER, nullable=False, server_default=text("'0'"))
    user_lastpage = Column(VARCHAR(200), nullable=False, server_default=text("''"))
    user_last_confirm_key = Column(
        VARCHAR(10), nullable=False, server_default=text("''")
    )
    user_last_search = Column(INTEGER, nullable=False, server_default=text("'0'"))
    user_warnings = Column(TINYINT, nullable=False, server_default=text("'0'"))
    user_last_warning = Column(INTEGER, nullable=False, server_default=text("'0'"))
    user_login_attempts = Column(TINYINT, nullable=False, server_default=text("'0'"))
    user_inactive_reason = Column(TINYINT, nullable=False, server_default=text("'0'"))
    user_inactive_time = Column(INTEGER, nullable=False, server_default=text("'0'"))
    user_posts = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    user_lang = Column(VARCHAR(30), nullable=False, server_default=text("''"))
    user_timezone = Column(VARCHAR(100), nullable=False, server_default=text("''"))
    user_dateformat = Column(
        VARCHAR(64), nullable=False, server_default=text("'d M Y H:i'")
    )
    user_style = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    user_rank = Column(MEDIUMINT, nullable=False, server_default=text("'0'"))
    user_colour = Column(VARCHAR(6), nullable=False, server_default=text("''"))
    user_new_privmsg = Column(Integer, nullable=False, server_default=text("'0'"))
    user_unread_privmsg = Column(Integer, nullable=False, server_default=text("'0'"))
    user_last_privmsg = Column(INTEGER, nullable=False, server_default=text("'0'"))
    user_message_rules = Column(TINYINT, nullable=False, server_default=text("'0'"))
    user_full_folder = Column(Integer, nullable=False, server_default=text("'-3'"))
    user_emailtime = Column(INTEGER, nullable=False, server_default=text("'0'"))
    user_topic_show_days = Column(SMALLINT, nullable=False, server_default=text("'0'"))
    user_topic_sortby_type = Column(
        VARCHAR(1), nullable=False, server_default=text("'t'")
    )
    user_topic_sortby_dir = Column(
        VARCHAR(1), nullable=False, server_default=text("'d'")
    )
    user_post_show_days = Column(SMALLINT, nullable=False, server_default=text("'0'"))
    user_post_sortby_type = Column(
        VARCHAR(1), nullable=False, server_default=text("'t'")
    )
    user_post_sortby_dir = Column(
        VARCHAR(1), nullable=False, server_default=text("'a'")
    )
    user_notify = Column(TINYINT, nullable=False, server_default=text("'0'"))
    user_notify_pm = Column(TINYINT, nullable=False, server_default=text("'1'"))
    user_notify_type = Column(TINYINT, nullable=False, server_default=text("'0'"))
    user_allow_pm = Column(TINYINT, nullable=False, server_default=text("'1'"))
    user_allow_viewonline = Column(TINYINT, nullable=False, server_default=text("'1'"))
    user_allow_viewemail = Column(TINYINT, nullable=False, server_default=text("'1'"))
    user_allow_massemail = Column(TINYINT, nullable=False, server_default=text("'1'"))
    user_options = Column(INTEGER, nullable=False, server_default=text("'230271'"))
    user_avatar = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    user_avatar_type = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    user_avatar_width = Column(SMALLINT, nullable=False, server_default=text("'0'"))
    user_avatar_height = Column(SMALLINT, nullable=False, server_default=text("'0'"))
    user_sig = Column(MEDIUMTEXT, nullable=False)
    user_sig_bbcode_uid = Column(VARCHAR(8), nullable=False, server_default=text("''"))
    user_sig_bbcode_bitfield = Column(
        VARCHAR(255), nullable=False, server_default=text("''")
    )
    user_jabber = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    user_actkey = Column(VARCHAR(32), nullable=False, server_default=text("''"))
    reset_token = Column(VARCHAR(64), nullable=False, server_default=text("''"))
    reset_token_expiration = Column(INTEGER, nullable=False, server_default=text("'0'"))
    user_newpasswd = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    user_form_salt = Column(VARCHAR(32), nullable=False, server_default=text("''"))
    user_new = Column(TINYINT, nullable=False, server_default=text("'1'"))
    user_reminded = Column(TINYINT, nullable=False, server_default=text("'0'"))
    user_reminded_time = Column(INTEGER, nullable=False, server_default=text("'0'"))
    user_reputation = Column(Integer, nullable=False, server_default=text("'0'"))
    user_rep_new = Column(Integer, nullable=False, server_default=text("'0'"))
    user_rep_last = Column(Integer, nullable=False, server_default=text("'0'"))
    user_rs_notification = Column(TINYINT, nullable=False, server_default=text("'1'"))
    user_rs_default_power = Column(Integer, nullable=False, server_default=text("'0'"))
    user_last_rep_ban = Column(INTEGER, nullable=False, server_default=text("'0'"))
    board_announcements_status = Column(
        TINYINT, nullable=False, server_default=text("'1'")
    )
    collapsible_categories = Column(TEXT)


class PhpbbWarning(Base):
    __tablename__ = "phpbb_warnings"

    warning_id = Column(MEDIUMINT, primary_key=True)
    user_id = Column(INTEGER, nullable=False, server_default=text("'0'"))
    post_id = Column(INTEGER, nullable=False, server_default=text("'0'"))
    log_id = Column(INTEGER, nullable=False, server_default=text("'0'"))
    warning_time = Column(INTEGER, nullable=False, server_default=text("'0'"))


class PhpbbWord(Base):
    __tablename__ = "phpbb_words"

    word_id = Column(INTEGER, primary_key=True)
    word = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    replacement = Column(VARCHAR(255), nullable=False, server_default=text("''"))


class PhpbbZebra(Base):
    __tablename__ = "phpbb_zebra"

    user_id = Column(
        INTEGER, primary_key=True, nullable=False, server_default=text("'0'")
    )
    zebra_id = Column(
        INTEGER, primary_key=True, nullable=False, server_default=text("'0'")
    )
    friend = Column(TINYINT, nullable=False, server_default=text("'0'"))
    foe = Column(TINYINT, nullable=False, server_default=text("'0'"))
