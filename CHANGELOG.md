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