# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.1] - 2022-04-26  
### Added
- api: 批量删除media列表 `delete /api/admin/media/`
- api: 上传不与对象绑定的图片 `post /api/admin/media {... is_static=True}`

### Changed
- 公告添加标签字段
- 公告添加联系方式字段
- 
## [0.0.1] - 2022-05-06
### Added
- model: `AnnouncementTag` 及其api(get,post,delete,update)
- api: 通过id获取文件 `/api/admin/media/{id}/stream`
### Changed
- admin 公告和数据库会返回名称和id，而不是只有id
- 公告返回数据时，如果有数据库，会返回id,name(标题),publisher(发布者)
- `AnnouncementTag`,`DatabaseCategory`,`DatabaseSource`,`DatabaseSubject` 会返回id
- 公告返回tags包含名称，而不是只有id
- ip标识已访问，第二次不会返回400错误
### Fixed
- `is_static`拼写错误