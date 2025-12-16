"""
vfs-docker - Docker Virtual Filesystem

Projects Docker containers, images, volumes, and networks onto a filesystem structure.

## Filesystem Structure

```
/docker/
├── .info.json                          # Docker daemon info
├── .version.json                       # Docker version
├── containers/
│   ├── running/                        # Symlinks to running containers
│   ├── stopped/                        # Symlinks to stopped containers
│   └── {container-id}/                 # Or {name} if unique
│       ├── .container.json             # docker inspect output
│       ├── name.txt                    # Container name
│       ├── image.txt                   # Image name
│       ├── status.txt                  # running/stopped/paused
│       ├── created.txt                 # Creation timestamp
│       ├── ports.json                  # Port mappings
│       ├── env.json                    # Environment variables
│       ├── labels.json                 # Container labels
│       ├── mounts.json                 # Volume mounts
│       ├── networks.json               # Network connections
│       ├── logs/
│       │   ├── stdout.log              # Stdout logs (streamable)
│       │   ├── stderr.log              # Stderr logs
│       │   └── combined.log            # Both streams
│       ├── stats.json                  # Live stats (CPU, memory, network)
│       ├── top.txt                     # Running processes
│       ├── diff.json                   # Filesystem changes
│       └── fs/                         # Container filesystem
│           └── {path}                  # Files from container
├── images/
│   ├── by-repo/
│   │   └── {repo}/
│   │       └── {tag} -> ../../{id}
│   └── {image-id}/
│       ├── .image.json                 # docker inspect output
│       ├── name.txt                    # repo:tag
│       ├── size.txt                    # Image size
│       ├── created.txt                 # Creation timestamp
│       ├── dockerfile                  # Reconstructed Dockerfile (best effort)
│       ├── history.json                # Layer history
│       ├── labels.json                 # Image labels
│       └── layers/
│           └── {layer-id}/
│               ├── .layer.json
│               └── diff/               # Layer contents
├── volumes/
│   └── {volume-name}/
│       ├── .volume.json                # docker volume inspect
│       ├── driver.txt                  # Volume driver
│       ├── labels.json
│       └── data/                       # Volume contents (if local)
│           └── {path}
├── networks/
│   └── {network-id}/
│       ├── .network.json               # docker network inspect
│       ├── name.txt
│       ├── driver.txt
│       ├── scope.txt                   # local/swarm/global
│       ├── containers/                 # Connected containers
│       │   └── {container-id} -> ../../containers/{id}
│       └── config.json                 # IPAM config
├── compose/                            # Docker Compose projects
│   └── {project}/
│       ├── docker-compose.yml
│       ├── .env
│       └── services/
│           └── {service}/
│               ├── .service.json
│               └── containers/
│                   └── {id} -> ../../../containers/{id}
└── swarm/                              # Swarm mode (if enabled)
    ├── .swarm.json
    ├── nodes/
    ├── services/
    ├── tasks/
    └── secrets/

## Capabilities

- READ: List containers, images, read logs
- WRITE: Update container (restart, pause)
- CREATE: Create containers, networks, volumes
- DELETE: Remove containers, images, volumes

## Configuration

```python
DockerVFS(
    socket_path="/var/run/docker.sock",
    # Or TCP
    host="tcp://localhost:2375",
    tls_verify=True,
    cert_path="~/.docker/certs",
    cache_ttl=30,               # Shorter TTL for dynamic data
    stream_logs=True,           # Enable log streaming
)
```
"""

from .provider import DockerVFS
from .types import DockerContainer, DockerImage, DockerVolume, DockerNetwork

__all__ = ["DockerVFS", "DockerContainer", "DockerImage", "DockerVolume", "DockerNetwork"]
__version__ = "0.1.0"

Provider = DockerVFS


def get_provider_class():
    return DockerVFS


def register(registry):
    registry.register(
        name="docker",
        provider_class=DockerVFS,
        description="Docker containers, images, volumes, networks",
        required_config=[],
        optional_config=["socket_path", "host", "tls_verify", "cache_ttl"],
    )
