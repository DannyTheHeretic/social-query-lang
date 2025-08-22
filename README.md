## The Social Query Language (SQL-BSky)

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![BlueSky](https://img.shields.io/badge/BlueSky-AT_Protocol-00D4FF.svg)](https://bsky.app)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE.txt)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

A retro terminal-style SQL interface for querying the BlueSky social network. Experience social media through the lens of structured query language with authentic CRT visual effects.

![App Initialization](assets/Init_sql_app.gif)

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

> [!NOTE]
> If the page is slow, try disabling the CRT effect at this point.

2. **Try Your First Query**:
   ```sql
   SELECT * FROM tables
   ```

   ![Running Test Query](assets/run_test_query.gif)

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
SELECT * FROM feed WHERE author='bsky.app'
```
- This will get all fields from all posts from the author's feed

```sql
SELECT description FROM followers WHERE author='bsky.app'
```
- This will get the bio of all followers of the author

```sql
SELECT * FROM tables
```
- This will get all available table names

## Known Issues

> [!WARNING]  
> Please be aware of these current limitations before using the application.

> [!NOTE]  
> Queries to non-existent tables or fields will return empty rows instead of proper error messages.

**Example:**
```sql
-- Both of these return empty rows (same behavior)
SELECT likes FROM feed WHERE author = "bsky.app"
SELECT apples FROM feed WHERE author = "bsky.app"
```

### KeyError in Feed Processing  
> [!IMPORTANT]  
> There's a known KeyError where the system looks for `"feeds"` but should be looking for `"feed"`. This is a human error we discovered after the Code Jam programming time had ended, so we weren't able to fix it, but we're aware of the issue and it may cause some like-table-related queries to fail unexpectedly.

##### Table `likes` Not Functional
> [!CAUTION]
> The `likes` table is currently broken and behaves like a non-existent table. This is due to the KeyError
## Team - Iridescent Ivies

- **A5rocks** - [GitHub](https://github.com/A5rocks) (Team Leader)
- **TheHeretic** - [GitHub](https://github.com/DannyTheHeretic)
- **Walkercito** - [GitHub](https://github.com/Walkercito)
- **Joshdtbx** - [GitHub](https://github.com/giplgwm)
- **Mimic** - [GitHub](https://github.com/Drakariboo)

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

---

**Thank you for exploring our project!!**
