# Support other languages

The api supports several languages. You can set what language you want the response to be in by either changing the client language `client.lang` or passing the language as a method argument

The default language is English - `en-us`

## Quick example


```py
client = genshin.GenshinClient(lang="fr-fr")
user = await client.get_user(710785423)

client = genshin.GenshinClient()
client.lang = "ko-kr"
user = await client.get_user(710785423)

client = genshin.GenshinClient()
user = await client.get_user(710785423, lang="zh-tw")
```

## Supported Llanguages

This list may be gotten with `genshin.LANGS`

| Code  | Language   |
| ----- | ---------- |
| de-de | Deutsch    |
| en-us | English    |
| es-es | Español    |
| fr-fr | Français   |
| id-id | Indonesia  |
| ja-jp | 日本語     |
| ko-kr | 한국어     |
| pt-pt | Português  |
| ru-ru | Pусский    |
| th-th | ภาษาไทย    |
| vi-vn | Tiếng Việt |
| zh-cn | 简体中文   |
| zh-tw | 繁體中文   |
