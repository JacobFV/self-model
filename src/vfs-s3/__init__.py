"""
vfs-s3 - AWS S3 Virtual Filesystem

Projects S3 buckets and objects onto a filesystem structure.

## Filesystem Structure

```
/s3/
├── {bucket-name}/
│   ├── .bucket.json                    # Bucket metadata
│   │   # region, versioning, encryption, lifecycle
│   ├── .policy.json                    # Bucket policy
│   ├── .cors.json                      # CORS configuration
│   ├── .lifecycle.json                 # Lifecycle rules
│   ├── .logging.json                   # Access logging config
│   ├── {prefix}/                       # "Folders" (common prefixes)
│   │   └── {key}                       # Objects
│   └── {key}                           # Objects at root
│
│   # Versioning (if enabled)
├── {bucket-name}/.versions/
│   └── {key}/
│       ├── .versions.json              # Version list
│       ├── {version-id}                # Specific version content
│       └── latest -> {version-id}      # Symlink to latest
│
│   # Delete markers (versioned buckets)
├── {bucket-name}/.delete-markers/
│   └── {key}.json
│
└── .buckets.json                       # List all buckets

## Object Extended Attributes

- user.s3.etag              # ETag
- user.s3.version_id        # Version ID
- user.s3.storage_class     # STANDARD, GLACIER, etc.
- user.s3.content_type      # Content-Type
- user.s3.content_encoding  # Content-Encoding
- user.s3.metadata          # User metadata JSON
- user.s3.tagging           # Object tags JSON
- user.s3.acl               # ACL JSON

## Special Files

Writing to special paths triggers S3 operations:
- {bucket}/.multipart/{key}     # Multipart upload
- {bucket}/.presign/{key}       # Generate presigned URL (read returns URL)

## Capabilities

- READ: List buckets, objects, download content
- WRITE: Upload objects, update metadata
- CREATE: Create buckets, upload objects
- DELETE: Delete objects, buckets

## Configuration

```python
S3VFS(
    # Uses default AWS credential chain if not specified
    aws_access_key_id=None,
    aws_secret_access_key=None,
    aws_session_token=None,
    region_name="us-east-1",
    profile_name=None,          # AWS profile
    endpoint_url=None,          # For S3-compatible services (MinIO, etc.)
    cache_ttl=300,
    show_versions=True,         # Include .versions/ for versioned buckets
)
```
"""

from .provider import S3VFS
from .types import S3Bucket, S3Object, S3Version

__all__ = ["S3VFS", "S3Bucket", "S3Object", "S3Version"]
__version__ = "0.1.0"

Provider = S3VFS


def get_provider_class():
    return S3VFS


def register(registry):
    registry.register(
        name="s3",
        provider_class=S3VFS,
        description="AWS S3 buckets and objects",
        required_config=[],  # Uses AWS credential chain
        optional_config=["region_name", "profile_name", "endpoint_url", "cache_ttl"],
    )
