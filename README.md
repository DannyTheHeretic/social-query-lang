#  Social Query Language

An SQL interface for interacting with the Bluesky social network.

## Features
- Allows bluesky login to use api endpoints that require auth
- Uses public API endpoints where possible to allow for use without logging in
- Displays images in the form of ascii art
- Provides error messages for malformed SQL statements

## Usage

### How to run
1. In the project folder run
```python
pip install -r requirements.txt
```
2. Once the dependencies are installed run the following command to start the server
```cmd
cd src && python -m http.server
```
3. Open the address displayed in the command prompt to view the website

### Useful Fields
You can use * in place of selecting fields to view all fields returned from the API, but here are a few useful ones:
|Post fields|User fields (following/followers tables)|
|--------|-----------|
|post_author_displayName|handle|
|post_record_text|displayName|
|post_likeCount|avatar|
|post_images|description|
|post_replyCount|

  
### Example Queries

```sql
SELECT * FROM feed WHERE author='tess.bsky.social'
```
- This will get all fields from all posts from the author's feed

```sql
SELECT post_author_displayName, post_record_text FROM likes WHERE author='tess.bsky.social'
```
- This will get only the selected fields from all posts from the author's likes

```sql
SELECT description FROM followers WHERE author='tess.bsky.social'
```
- This will get the bio of all followers of the author

```sql
SELECT * FROM tables
```
- This will get all available table names

### Available Tables
1. feed
2. timeline
3. profile
4. suggestions
5. suggested_feed
6. likes
7. followers
8. following
9. mutuals