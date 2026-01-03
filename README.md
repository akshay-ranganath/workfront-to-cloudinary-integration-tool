# Workfront to Cloudinary Integration Tool

A Python-based automation tool that synchronizes documents from Adobe Workfront tasks to Cloudinary DAM. This tool monitors Workfront tasks with a specific status, downloads their associated documents, uploads them to Cloudinary, and updates both systems with the results.

## Features

- 🔍 **Automatic Task Discovery**: Searches for Workfront tasks marked for Cloudinary upload
- 📥 **Document Download**: Retrieves documents from Workfront tasks
- ☁️ **Cloudinary Upload**: Uploads documents to Cloudinary and retains metadata as well
- 🔄 **Status Synchronization**: Updates both Workfront documents and tasks with upload results
- 🧹 **Cleanup**: Automatically removes temporary files after processing
- 🔐 **Secure Authentication**: OAuth JWT-based authentication with Workfront

## Project Structure

```
workfront-to-cloudinary-integration-tool/
├── main.py                            # Main entry point - orchestrates workflow
├── config.py                          # Configuration management
├── authenticate.py                    # Workfront OAuth authentication
├── workfront_api.py                   # Workfront API client
├── cloudinary_service.py              # Cloudinary service
├── document_processor.py              # Document processing workflow
├── requirements.txt                   # Python dependencies
├── LICENSE                            # MIT License
├── .env                               # Environment variables (not in repo)
├── .gitignore                         # Git ignore rules
└── README.md                          # This file
```

### Module Descriptions

- **`main.py`**: Main entry point for the workflow. Orchestrates the complete process with proper error handling and logging.
- **`config.py`**: Centralized configuration management. Loads and validates all environment variables.
- **`authenticate.py`**: Handles Workfront OAuth authentication using JWT flow. Generates session IDs for API calls.
- **`workfront_api.py`**: Workfront API client with methods for searching tasks, downloading documents, and updating status.
- **`cloudinary_service.py`**: Cloudinary service wrapper for uploading files and managing assets.
- **`document_processor.py`**: Document processing pipeline that coordinates download -> upload -> update workflow.
- **`requirements.txt`**: Python package dependencies with version constraints.

### Architecture Benefits

The modular architecture provides:
- ✅ **Separation of Concerns**: Each module has a single, well-defined responsibility
- ✅ **Testability**: Individual modules can be tested in isolation
- ✅ **Reusability**: Components can be reused in other scripts or tools
- ✅ **Maintainability**: Changes are localized to specific modules
- ✅ **Error Handling**: Consistent exception handling across modules

## Prerequisites

- Python 3.7+
- Workfront account with OAuth credentials
- Cloudinary account with API credentials
- Access to Workfront tasks and documents

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd workfront-to-cloudinary-integration-tool
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   This will install the following required packages:
   - `cloudinary` (≥1.36.0) - Cloudinary Python SDK for media asset management
   - `requests` (≥2.31.0) - HTTP library for API requests
   - `PyJWT` (≥2.8.0) - JWT token generation for Workfront OAuth
   - `python-dotenv` (≥1.0.0) - Environment variable management

4. **Create `.env` file** with required environment variables (see below)

## Environment Variables

Create a `.env` file in the project root with the following variables:

### Workfront Configuration
```bash
# Workfront API Settings
WORKFRONT_BASE_URL=https://your-instance.my.workfront.com/attask/api
WORKFRONT_API_KEY=your_api_key_here

# Workfront OAuth Settings (for authentication)
WORKFRONT_BASE=your-instance
WORKFRONT_CLIENT_ID=your_client_id
WORKFRONT_CLIENT_SECRET=your_client_secret
WORKFRONT_CUSTOMER_ID=your_customer_id
WORKFRONT_USER_ID=your_user_id
WORKFRONT_PRIVATE_KEY=-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----

# Cloudinary configuration
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### Task Status Codes

On Workfront, we need to set the task status to `complete` or `fail`. For this, we need the exact 3 letter code that is used in workfront. Here is an example. We need the values `TASK_COMPLETE` and `TASK_ERROR` defined in the environment(`.env`) file.

```bash
# Status codes to set when tasks complete or fail
TASK_COMPLETE=CPL
TASK_ERROR=ERR
```

## Usage

### Running the Workflow

Execute the main workflow script:

```bash
python main.py
```

### What Happens During Execution

1. **Task Discovery**: Searches for Workfront tasks with status "UPL" (Upload to Cloudinary)
2. **Validation**: Checks that discovered tasks have documents attached
3. **Authentication**: Obtains a Workfront session ID using OAuth
4. **Processing**: For each task:
   - Downloads all attached documents
   - Uploads them to Cloudinary (organized in `workfront/` folder)
   - Updates Workfront document descriptions with Cloudinary URLs
   - Updates task status to either complete or error
5. **Cleanup**: Removes temporary files

### Example Output

```
2026-01-03 10:15:23 - __main__ - INFO - 🚀 Starting Workfront to Cloudinary document upload workflow

2026-01-03 10:15:23 - __main__ - INFO - ✅ Configuration validated successfully
2026-01-03 10:15:23 - __main__ - INFO - Initializing services...
2026-01-03 10:15:23 - __main__ - INFO - ✅ Services initialized

2026-01-03 10:15:23 - __main__ - INFO - Authenticating with Workfront...
2026-01-03 10:15:24 - authenticate - INFO - ✅ Session ID retrieved successfully
2026-01-03 10:15:24 - __main__ - INFO - ✅ Authentication successful

2026-01-03 10:15:24 - __main__ - INFO - Searching for tasks with status 'UPL'...
2026-01-03 10:15:24 - workfront_api - INFO - ✅ GET Successful
2026-01-03 10:15:24 - __main__ - INFO - Found 3 tasks for processing

2026-01-03 10:15:24 - __main__ - INFO - 
============================================================
2026-01-03 10:15:24 - __main__ - INFO - Processing Task 1/3: ABC123
2026-01-03 10:15:24 - __main__ - INFO - Documents: 2
2026-01-03 10:15:24 - __main__ - INFO - ============================================================
2026-01-03 10:15:24 - document_processor - INFO - Processing 2 documents for task ABC123
2026-01-03 10:15:24 - document_processor - INFO - Processing document DOC456 (image.jpg)
2026-01-03 10:15:24 - workfront_api - INFO - ✅ Downloaded document DOC456
2026-01-03 10:15:25 - cloudinary_service - INFO - ✅ File uploaded successfully: https://res.cloudinary.com/...
2026-01-03 10:15:25 - workfront_api - INFO - ✅ PUT Successful
2026-01-03 10:15:25 - workfront_api - INFO - Document DOC456 updated successfully
2026-01-03 10:15:26 - document_processor - INFO - ✅ All documents processed successfully for task ABC123
2026-01-03 10:15:26 - workfront_api - INFO - ✅ PUT Successful
2026-01-03 10:15:26 - workfront_api - INFO - Task ABC123 updated to status 'CPL'

2026-01-03 10:15:30 - __main__ - INFO - 
============================================================
2026-01-03 10:15:30 - __main__ - INFO - WORKFLOW SUMMARY
2026-01-03 10:15:30 - __main__ - INFO - ============================================================
2026-01-03 10:15:30 - __main__ - INFO - Total Tasks Processed: 3
2026-01-03 10:15:30 - __main__ - INFO - Successful Tasks: 3
2026-01-03 10:15:30 - __main__ - INFO - Failed Tasks: 0
2026-01-03 10:15:30 - __main__ - INFO - Total Documents: 5
2026-01-03 10:15:30 - __main__ - INFO - ============================================================

2026-01-03 10:15:30 - __main__ - INFO - ✅ Workflow completed successfully
```

## Workflow Details

### Task Status Flow

```
[UPL] Upload to Cloudinary
  ↓
[Processing Documents]
  ↓
[CPL] Complete  OR  [ERR] Error
```

### Cloudinary Organization

Documents are uploaded with the following structure. This is just for demo purpose. If you want to change, please update the `upload_file` method in `cloudinary_service.py`.

- **Asset Folder**: `workfront/`
- **Public ID**: Workfront document ID
- **Display Name**: Original document name
- **Resource Type**: Auto-detected based on file type

### Error Handling

- Missing environment variables: Raises `ValueError` with details
- Authentication failures: Logs error and raises exception
- Upload failures: Sets task status to error code and continues with next task
- Temporary files: Always cleaned up, even on errors

## Development

### Module Architecture

The codebase has the following architecture:

```
┌─────────────────────────────────────────────────────┐
│                     main.py                         │
│              (Workflow Orchestration)               │
└──────────────┬─────────────┬────────────────────────┘
               │             │
     ┌─────────┴──────┐     │
     │                │     │
┌────▼─────┐    ┌────▼──────▼────────┐    ┌──────────────┐
│ config.py│◄───│document_processor.py│───►│ authenticate │
└──────────┘    └────┬──────┬─────────┘    └──────────────┘
                     │      │
              ┌──────┴──┐ ┌─┴─────────────┐
              │workfront│ │cloudinary     │
              │_api.py  │ │_service.py    │
              └─────────┘ └───────────────┘
```

### Extending the Code

1. **API Endpoints**: Add methods to `workfront_api.py` or `cloudinary_service.py`
2. **Processing Logic**: Extend `document_processor.py`
3. **Configuration Options**: Add to `config.py` with environment variable
4. **Workflow Changes**: Modify `main.py` orchestration

### Code Style Guidelines

- Use type hints for function parameters and return values
- Use descriptive variable and function names
- Add docstrings to all public functions and classes
- Use custom exceptions for error handling (`WorkfrontAPIError`, `CloudinaryServiceError`)
- Log important operations with appropriate levels (DEBUG, INFO, WARNING, ERROR)

### Logging Levels

Change logging level in `main.py`:
```python
logging.basicConfig(level=logging.DEBUG)  # For detailed logs
logging.basicConfig(level=logging.INFO)   # For normal operation
```

### Running Tests

To test individual modules:

```python
# Test configuration
from config import Config
Config.validate_all()

# Test authentication
from authenticate import get_workfront_session_id
session_id = get_workfront_session_id()

# Test Workfront API
from workfront_api import WorkfrontAPI
api = WorkfrontAPI()
tasks = api.search_tasks('UPL', limit=10)
```

## Configuration Options

You can customize the workflow behavior with these optional environment variables:

```bash
# Asset organization in Cloudinary
CLOUDINARY_ASSET_FOLDER=workfront  # Default folder for uploads

# Task status codes (if different from defaults)
TASK_STATUS_UPLOAD=UPL  # Status code for tasks to process
TASK_COMPLETE=CPL       # Status code for successful completion
TASK_ERROR=ERR          # Status code for failed tasks

# Processing limits
MAX_TASKS_PER_RUN=100   # Maximum tasks to process per execution
```

## Known Limitations

- Processes up to 100 tasks per run (configurable via `MAX_TASKS_PER_RUN`)
- JWT tokens expire after 3 minutes (automatically regenerated on each run)
- Currently only processes tasks with status "UPL" (configurable via `TASK_STATUS_UPLOAD`)
- Task is marked as failed if ANY document fails to upload

## Troubleshooting

### Authentication Errors
- Verify all `WORKFRONT_*` environment variables are set correctly
- Check that private key includes proper newlines (`\n`)
- Ensure OAuth application is properly configured in Workfront

### Upload Failures
- Verify Cloudinary credentials are correct
- Check file size limits for your Cloudinary plan
- Ensure proper network connectivity

### No Tasks Found
- Verify tasks exist with status "UPL" in Workfront
- Check that tasks have `isComplete=false`
- Confirm API key has permission to access tasks

## Security Notes

- Never commit `.env` file or credentials to version control
- Keep private keys secure and rotate regularly
- Use environment-specific credentials for dev/staging/production
- Consider using a secrets manager for production deployments

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### What this means:
- ✅ Use commercially
- ✅ Modify freely
- ✅ Distribute
- ✅ Private use
- ✅ No restrictions on what you can do with it

The only requirement is to include the copyright notice and license in copies of the software.

## Contributing

[Add contribution guidelines here]

## Support

For issues or questions, please contact [your contact information].

