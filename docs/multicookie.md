# Multi-Cookie Clients

Mihoyo has very strict ratelimits in place. You are allowed to only request data for 30 users per day. This means most projects are practically unusable with a single cookie. To solve this issue you may set multiple cookies at once using `genshin.MultiCookieClient`. This client requires a list of cookies instead of a dict. Whenever a cookie hits its ratelimit a different one is used.

Since creating multiple alt accounts to get your cookies is a slow and tedious process you may try any of the countless automated account creates such as [thesadru/genshin-account-creator](https://github.com/thesadru/genshin-account-creator).

## Quick example.

```py
client = genshin.MultiCookieClient()
client.set_cookies([{...}, {...}, ...])

user = await client.get_user(710785423)
```
