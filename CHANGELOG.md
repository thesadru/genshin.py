# Changelog

# 1.6.1 (2023-08-12)

## Fixes

- Support providing geetest headers.
- Use the newest version of pydantic.

# 1.6.0 (2023-06-11)

## What's new

- Star rail daily rewards, battle chronicle and wish history.

## Fixes

- Raise errors on geetest instead of silently failing.
- Fix v2 cookie compatibility.

# 1.5.2 (2023-03-31)

## Fixes

- Allow v2 cookies.

# 1.5.1 (2023-02-10)

## What's new

- Added event announcments.
- Migrated to gitlab for icon data.

## Fixes

- Fixed some CN endpoints.
- Fixed getting low-level honkai users.

# 1.5.0 (2022-12-21)

## What's new

- Added genshin chronicle TCG endpoints.
- Added teapot replica endpoints.
- Aded an official source for banner IDs.
- Made the hoyolab ID optional.

## Fixes

- Fixed false positives when using multiple cookies.
- Added turkish and italian to the list of languages.

# 1.4.0 (2022-11-16)

## What's new

- Added geshin lineup.
- Added cn calculator endpoints.
- Added new icon types for genshin characters.

## Fixes

- Invalid cookies are no longer kept.
- Cookie tokens are now automatically refreshed.

# 1.3.0 (2022-10-15)

## What's new

- Character data may be updated using 3rd party databases.

## Fixes

- Character names are no longer in a different language.
- Authkeys can be grabbed from local files again.

# 1.2.4 (2022-09-12)

## Fixes

- Added dendoruculus to chronicle stats.
- Added new genshin and honkai characters.

# 1.2.3 (2022-08-05)

## What's new

- Added the golden apple archipelago activity.

## Fixes

- Updated ds salt for cn daily rewards.
- Exclude partial and empty characters from responses.

# 1.2.2 (2022-07-05)

## What's new

- Added user info to genshin stats.

## Fixes

- Fixed enabling of real-time notes and calculator sync.
- Do not require cookies for authkey endpoints.

# 1.2.1 (2022-05-28)

## Fixes

- Increased page size of diaries to 100.
- Automatically enable real-time notes when used for the first time.

# 1.2.0 (2022-05-19)

## What's new

- Added `client.uid` as a simpler alias for `client.uids`.
- Allowed explicit UIDs in diary and calculator endpoints.
- Implemented an international cookie manager.
- Added `client.proxy`.
- Implemented very basic wiki endpoints.
- Implemented hoyolab community check-in.

## Changes

- The password is now hidden in `python -m genshin login`
- Stored timedeltas instead of datetimes in real-time notes.

## Fixes

- Fixed honkai stats for users without any unlocked abyss.

# 1.1.0 (2022-04-22)

## What's new

- Added the Parametric Transformer to notes.
- Provided a direct `Client.uid` property for easier use with `default_game`.
- Added missing activities.

## Changes

- Improved the structure of Exploration models.
- Removed `is_chinese` with `recognize_region` which now requires a `genshin.Game`.

## Fixes

- Character model validation now works for foreign languages.

# 1.0.1 (2022-04-15)

## Fixes

- Added mi18n to the cache.
- Optimized `_get_uid`.

# 1.0.0 (2022-04-13)

## What's new

- Added honkai endpoints.
- Added login with username and password (`Client.login_with_password`)
- Made the entire project be mypy and pyright strict compliant.

## Changes

- Caching is now handled through `Client.cache`
- Moved `MultiCookieClient` functionality to `Client.cookie_manager`

## Fixes

- Reduced the amount of unexpected ratelimit exceptions
- Made every single model be re-serializable.

## Deprecation

- `GenshinClient.cookies` were removed in favor of `cookie_manager`
- `GenshinClient` and subclasses were merged into `Client`
- `genshin_accounts` -> `get_game_accounts`
- `get_record_card` -> `get_record_cards`
- `get_[partial|full]_user` -> `get_[partial|full]_genshin_user`

# 0.4.0 (2022-02-03)

## What's new

- Added Serenitea Pot's Jar of Riches to Real-Time Notes
- Implemented `set_top_characters`
- Added models for A Study in Potions

## Changes

- Made the Enhancement Progression Calculator use the builder pattern

# 0.3.1 (2022-01-10)

## Deprecation

- Removed all_characters since the API no longer supports this feature

## Fixes

- Images are now accounted for during character data completion
- Diary log no longer repeatedly returns the first page in some cases

# 0.3.0 (2021-12-25)

## What's new

- Added full support for the Genshin Impact Enhancement Progression Calculator
- Improved debug mode to be slightly more descriptive

## Fixes

- Fixed minor API inconsistencies including domain mismatches
- Ensured some specific models no longer break when being revalidated

# 0.2.0 (2021-12-03)

## What's new

- Added partial support for i18n
- Added a way to specify the characters you want to get with `get_user`
- Improved rate limit handling for certain endpoints
- Made paginators awaitable

## Fixes

- Fixed breaking API changes caused by the second banner
- Deprecated authkeys in support pages
- Fixed pydantic bug with ClassVar not being recognized properly

# 0.1.0 (2021-11-05)

## What's new

- Implemented the Traveler's Diary
- Cache uids for daily rewards and similar endpoints.
- Support artifact levels
- Add an `enabled` field for artifact set effects

## Fixes

- Migrate server domains in accordance with the recent HoYoLAB server migration
- Remove invalid authkey validation
- Make permanent caches persist
- No longer attempt to close non-existent sessions in `MultiCookieClient`
- Fix minor problems with model validation

# 0.0.2 (2021-10-25)

## What's new

- Implemented Real-Time notes
- Added Labyrinth Warriors to activities
- Made all `datetime` objects timezone aware.
- Added public privacy settings to record cards.
- Added basic support for Redis caches
- Added new CLI commands
- Added pdoc-generated API documentation
  - Started using ReST-style docstrings
  - Added module docstrings
- Made `debug` a property instead of an `__init__` param

## Fixes

- Chinese daily reward claiming will no longer consistently raise errors due to invalid headers.
- `get_banner_details` no longer requires gacha ids. They will be fetched from a user-maintained database from now on.
- `genshin.models.base.BaseCharacter` is now a string instead of `CharacterIcon`
- `genshin.models.base.GenshinModel.dict()` now also includes properties as it is immutable.

## Documentation

- Documented a large part of the library with at least simple examples
