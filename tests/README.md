# Test Suite

This directory contains the comprehensive test suite for the TwistyVoice AI promotional calling system.

## Test Structure

### Core Engine Tests
- `test_promotion_engine.py` - Tests for the promotional campaign engine
- `test_promotional_workflow.py` - End-to-end promotional workflow tests

### Campaign-Specific Tests
- `test_back_to_school_campaign.py` - Back-to-school campaign functionality tests

### System Integration Tests
- `test_call_verified.py` - Call verification and validation tests
- `test_workflow.py` - General workflow and process tests

### API and Route Tests
- `test_router_inclusion.py` - API router inclusion and configuration tests
- `test_routes_import.py` - Route import and endpoint tests

## Running Tests

### Run All Tests
```bash
# From project root
python -m pytest tests/

# Or using the test runner
python run_tests.py
```

### Run Specific Test Files
```bash
# Test a specific component
python -m pytest tests/test_promotion_engine.py

# Run with verbose output
python -m pytest tests/test_promotion_engine.py -v

# Run with coverage report
python -m pytest tests/ --cov=src --cov-report=html
```

### Run Tests by Category
```bash
# Run only workflow tests
python -m pytest tests/ -k "workflow"

# Run only campaign tests
python -m pytest tests/ -k "campaign"
```

## Test Configuration

Tests use the following configuration:
- **Test Database**: Isolated SQLite database for testing
- **Mock Services**: External API calls are mocked by default
- **Test Data**: Fixtures and sample data are loaded automatically

## Prerequisites

Before running tests:
1. Install test dependencies: `pip install -r requirements.txt`
2. Ensure environment variables are set (tests use `.env` or defaults)
3. Database migrations should be up to date

## Test Coverage

The test suite aims to cover:
- ✅ Core promotional engine logic
- ✅ Campaign creation and management
- ✅ Call workflow processes
- ✅ API endpoint functionality
- ✅ Data validation and error handling
- ⚠️ Integration with external services (mocked)

## Adding New Tests

When adding new features, please:
1. Create corresponding test files following the naming convention `test_*.py`
2. Use descriptive test function names
3. Include both positive and negative test cases
4. Mock external API calls appropriately
5. Add proper docstrings and comments