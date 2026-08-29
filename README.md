# Cinema Follower

> [!NOTE]
> Currently in development

The website allows to:
1. Follow people (actors, directors, etc.) and track their new projects (movies and TV shows separately).
2. Receive notifications about digital releases of tracked movies.

Stack:
- Flask
- themoviedb
- Google Auth
- SQLAlchemy + sqlite
- Redis
- RQ

## Current state

- [ ] Followed people
  - [x] UI
  - [x] Follow
  - [x] Unfollow
  - [ ] Follow only specific jobs
  - [ ] Sorting and filter
  - [ ] Text note
- [ ] Movie feed
  - [x] UI
  - [x] Infinite scrolling
  - [ ] Sorting and filter
- [ ] TV feed
- [ ] Digital releases
