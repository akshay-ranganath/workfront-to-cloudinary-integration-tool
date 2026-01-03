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
├── authenticate.py                     # Workfront OAuth authentication module
├── workfront-workflow-demo-code.py    # Main workflow script
├── requirements.txt                   # Python dependencies
├── .env                               # Environment variables (not in repo)
└── README.md                          # This file
```

### File Descriptions

- **`authenticate.py`**: Handles Workfront authentication using OAuth JWT flow. Generates session IDs for API calls.
- **`workfront-workflow-demo-code.py`**: Main workflow script that orchestrates the entire process from task discovery to document upload.
- **`requirements.txt`**: Python package dependencies with version constraints.

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
python workfront-workflow-demo-code.py
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
INFO:__main__:Starting Workfront to Cloudinary document upload workflow...
INFO:__main__:✅ GET Successful
INFO:__main__:Found 3 tasks with status 'Upload to Cloudinary'
INFO:__main__:Validating tasks have documents...
INFO:__main__:Task ABC123 has 2 documents
INFO:authenticate:✅ Session ID retrieved successfully
INFO:__main__:Successfully authenticated with Workfront
INFO:__main__:Processing task ABC123 with 2 documents
INFO:__main__:Downloaded document DOC456 to /tmp/tmpxyz123
INFO:__main__:Document DOC456 updated with Cloudinary url https://res.cloudinary.com/...
INFO:__main__:✅ PUT Successful
INFO:__main__:Task ABC123 updated to status: CPL
INFO:__main__:All tasks have been processed. Workflow complete.
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

Documents are uploaded with the following structure. This is just for demo purpose. If you want to change, please update the function `upload_to_cloudinary` in the file `workfront-workflow-demo-code.py`.

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

### Adding New Features

The code is organized into logical sections:

1. **API Utility Functions** (`api_request`): Generic Workfront API calls
2. **Authentication** (`authenticate.py`): OAuth JWT flow
3. **Document Handling**: Download, upload, cleanup
4. **Workfront Updates**: Document and task status updates
5. **Main Workflow**: Orchestration logic

### Logging Levels

Change logging level in the scripts:
```python
logging.basicConfig(level=logging.DEBUG)  # For detailed logs
logging.basicConfig(level=logging.INFO)   # For normal operation
```

## Known Limitations

- Task status is determined by the last document processed (TODO: improve to track all documents)
- Processes up to 100 tasks per run (set by `$$LIMIT=100` parameter)
- JWT tokens expire after 3 minutes (automatically regenerated on each run)
- Currently only processes tasks with status "UPL"

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

[Add your license information here]

## Contributing

[Add contribution guidelines here]

## Support

For issues or questions, please contact [your contact information].

