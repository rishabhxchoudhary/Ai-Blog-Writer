# Blog Writer - Trend Scout Agent

This project contains the **Trend Scout** agent that pulls fresh topics from Hacker News every hour and stores them in a PostgreSQL database.

## 📁 Project Structure

```
Blog Writer/
├── agents/
│   ├── __init__.py
│   └── trend_scout.py          # Main Trend Scout agent
├── common/
│   ├── __init__.py
│   └── types.py                # Shared data models (Trend)
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Shared test fixtures
│   ├── test_trend_scout.py     # Main agent tests
│   ├── test_trend_scout_integration.py  # Integration tests
│   ├── test_trend_scout_mocked.py       # Mocked dependency tests
│   └── test_trend_model.py     # Data model tests
├── main.py                     # Original entry point
├── setup_db.py                 # Database setup script
├── pyproject.toml             # Project configuration
├── requirements.txt           # Dependencies
├── pytest.ini                # Pytest configuration
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

Using uv (recommended):

```bash
uv sync
```

Or using pip:

```bash
pip install -r requirements.txt
```

### 2. Set Up Database

Make sure PostgreSQL is running and create the database:

```bash
createdb blog
createuser blog --password  # Set password to 'pw'
```

Then run the database setup script:

```bash
python setup_db.py
```

### 3. Run the Trend Scout Agent

```bash
python agents/trend_scout.py
```

## 🧪 Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Exclude slow tests
pytest -m "not slow"
```

### Run Specific Test Files

```bash
# Test the main agent functionality
pytest tests/test_trend_scout.py

# Test data model
pytest tests/test_trend_model.py

# Test integration scenarios
pytest tests/test_trend_scout_integration.py

# Test with mocked dependencies
pytest tests/test_trend_scout_mocked.py
```

### Test Coverage

```bash
pytest --cov=agents --cov=common
```

### Verbose Output

```bash
pytest -v
```

## 🔧 Agent Configuration

The Trend Scout agent can be configured by modifying the following parameters in `agents/trend_scout.py`:

- **`n` parameter**: Number of top stories to fetch (default: 30)
- **Database DSN**: Connection string for PostgreSQL
- **HN API URL**: Hacker News API endpoint

## 📊 Database Schema

The agent stores trends in a PostgreSQL table with the following structure:

```sql
CREATE TABLE trends (
    id VARCHAR(32) PRIMARY KEY,      -- MD5 hash of HN item ID
    title TEXT NOT NULL,             -- Article title
    url TEXT,                        -- Article URL (nullable for Ask HN posts)
    source VARCHAR(50) NOT NULL,     -- Source identifier ('hn')
    score INTEGER NOT NULL,          -- HN score/points
    ts TIMESTAMP NOT NULL,           -- Original timestamp from HN
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔄 Scheduling

The agent is designed to be run hourly. You can schedule it using:

### Cron

```bash
# Add to crontab (crontab -e)
0 * * * * cd /path/to/blog-writer && python agents/trend_scout.py
```

### Prefect (if you're using Prefect for orchestration)

```python
from prefect import flow, task
from prefect.schedules import IntervalSchedule
from datetime import timedelta

@task
def run_trend_scout():
    # Import and run the agent
    import subprocess
    subprocess.run(["python", "agents/trend_scout.py"])

@flow(schedule=IntervalSchedule(interval=timedelta(hours=1)))
def trend_scout_flow():
    run_trend_scout()
```

## 🧪 Test Framework

The project uses **pytest** with comprehensive test coverage:

### Test Categories

1. **Unit Tests** (`test_trend_scout.py`):

   - Individual function testing
   - Mock external dependencies
   - Error handling scenarios

2. **Integration Tests** (`test_trend_scout_integration.py`):

   - Full pipeline testing
   - Database interaction
   - API integration

3. **Model Tests** (`test_trend_model.py`):

   - Pydantic model validation
   - Data serialization
   - Edge cases

4. **Mocked Tests** (`test_trend_scout_mocked.py`):
   - Tests that work without external dependencies
   - Core logic validation
   - Parameter testing

### Test Fixtures

Shared fixtures are defined in `tests/conftest.py`:

- `mock_db_pool`: Mock database connection pool
- `sample_trend`: Sample Trend object
- `sample_trends_list`: List of sample trends

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**:

   ```
   Make sure PostgreSQL is running and the database 'blog' exists
   ```

   Solution: Run `createdb blog` and ensure PostgreSQL is started

2. **Import Errors in Tests**:

   ```
   Import "agents.trend_scout" could not be resolved
   ```

   Solution: Run tests from the project root directory

3. **Missing Dependencies**:
   ```
   Import "httpx" could not be resolved
   ```
   Solution: Install dependencies with `uv sync` or `pip install -r requirements.txt`

### Running Individual Components

Test just the database setup:

```bash
python setup_db.py
```

Test just the data model:

```bash
python -c "from common.types import Trend; print('Model imported successfully')"
```

## 📈 Monitoring

The agent provides basic logging output:

- Number of trends processed
- Database operation status
- Error messages for debugging

For production use, consider adding:

- Structured logging (JSON format)
- Metrics collection
- Alert notifications
- Health check endpoints

## 🔮 Future Enhancements

Potential improvements for the Trend Scout agent:

1. **Multiple Sources**: Add Reddit, Twitter, etc.
2. **Content Analysis**: Analyze trend content for topics
3. **Deduplication**: Detect similar articles across sources
4. **Sentiment Analysis**: Score trend sentiment
5. **Export Options**: JSON, CSV export functionality
6. **Real-time Updates**: WebSocket for live trend updates
