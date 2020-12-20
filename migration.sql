--- 在执行数据库迁移前请先备份原数据库


--- 版本
--- 20.4.19 to 20.5.1
create table videos_dg_tmp
(
	id INTEGER not null
		primary key,
	slug VARCHAR(255),
	code TEXT not null,
	tags VARCHAR(255) not null,
	title VARCHAR(255) not null,
	params TEXT not null,
	output TEXT not null,
	status INTEGER not null,
	created_at DATETIME not null,
	updated_at DATETIME
);

insert into videos_dg_tmp(id, slug, code, tags, title, params, created_at, updated_at, output, status) select id, slug, code, tags, title, params, created_at, updated_at, '' as output, 0 as status from videos;

drop table videos;

alter table videos_dg_tmp rename to videos;

create unique index video_slug
	on videos (slug);

create index video_status
	on videos (status);

