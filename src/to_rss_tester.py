import to_rss

name = "test3"
path=f"~/Downloads/{name}.xml"

# to_rss.create_rss(path=path, title=name, subtitle=f"{name} subtitle")
# print(f"Created {path}")

post_title = "Test post"
post_author="Hussein Esmail"
post_date="2021-05-03T15:05:35+00:00"
post_url="https://google.com"
post_guid="2"
post_body="body"
to_rss.add_to_rss(path=path, title=post_title, author=post_author, date=post_date, url=post_url, guid=post_guid, body=post_body)
print(f"Added post: {post_title}")