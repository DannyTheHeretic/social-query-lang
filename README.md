## The Social Query Language (SQL-BSky)

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![BlueSky](https://img.shields.io/badge/BlueSky-AT_Protocol-00D4FF.svg)](https://bsky.app)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE.txt)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

A retro terminal-style SQL interface for querying the BlueSky social network. Experience social media through the lens of structured query language with authentic CRT visual effects.

## Features

- **Dual Authentication**: Full BlueSky login or anonymous "stealth mode"
- **Public API Access**: Query public content without authentication
- **ASCII Art Images**: View embedded images as beautiful ASCII art
- **Real-time Validation**: Live SQL syntax checking as you type
- **Retro CRT Interface**: Authentic 1980s terminal experience with visual effects
- **Fast Performance**: Optimized queries with scrolling support
- **Easter Eggs**: Hidden surprises for the adventurous

## Quick Start

### Installation

1. Clone the repository:
   ```bash
   git clone git@github.com:A5rocks/code-jam-12.git

   # move to the dir
   cd code-jam-12
   ```
2. Start the development server:
   ```bash
   python3 dev.py
   ```

3. That's it! Open your browser to: [http://localhost:8000](http://localhost:8000)

### First Steps

1. **Choose Authentication Mode**:
   - **Authenticated**: Login with BlueSky credentials for full access
   - **Stealth Mode**: Browse public content anonymously

2. **Try Your First Query**:
   ```sql
   SELECT * FROM tables
   ```

3. **Explore Public Profiles**:
   ```sql
   SELECT * FROM profile WHERE actor = 'bsky.app'
   ```

## Query Reference

### Available Tables

| Table | Description | Auth Required | Parameters |
|-------|-------------|---------------|------------|
| `tables` | List all available tables | No | None |
| `profile` | User profile information | No | `actor` (optional) |
| `feed` | Posts from a specific user | No | `author` (required) |
| `timeline` | Your personal timeline | Yes | None |
| `suggestions` | Suggested users to follow | No | None |
| `suggested_feed` | Recommended feeds | No | None |
| `followers` | User's followers | No | `actor` (required) |
| `following` | Who user follows | No | `actor` (required) |
| `mutuals` | Mutual connections | No | `actor` (required) |
| `likes` | User's liked posts | Yes | `actor` (required) |

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

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

---

**1987 Iridescent Ivies** - *Experience social media like it's 1987!*
