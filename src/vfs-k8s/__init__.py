"""
vfs-k8s - Kubernetes Virtual Filesystem

Projects Kubernetes clusters, namespaces, and resources onto a filesystem structure.

## Filesystem Structure

```
/k8s/
├── {context}/                          # kubectl context
│   ├── .context.json                   # Context info
│   ├── .cluster.json                   # Cluster info
│   ├── version.json                    # Server version
│   ├── namespaces/
│   │   └── {namespace}/
│   │       ├── .namespace.yaml
│   │       │
│   │       ├── pods/
│   │       │   └── {pod-name}/
│   │       │       ├── .pod.yaml           # Full pod spec
│   │       │       ├── status.txt          # Running/Pending/Failed
│   │       │       ├── phase.txt
│   │       │       ├── conditions.json
│   │       │       ├── events.json         # Pod events
│   │       │       ├── logs/
│   │       │       │   └── {container}.log # Container logs
│   │       │       └── containers/
│   │       │           └── {container}/
│   │       │               ├── .container.yaml
│   │       │               ├── state.json
│   │       │               ├── log.txt
│   │       │               └── exec        # Write to exec commands
│   │       │
│   │       ├── deployments/
│   │       │   └── {name}/
│   │       │       ├── .deployment.yaml
│   │       │       ├── replicas.txt        # Desired replicas (writable)
│   │       │       ├── status.json
│   │       │       ├── conditions.json
│   │       │       └── pods/               # Owned pods
│   │       │           └── {pod} -> ../../pods/{pod}
│   │       │
│   │       ├── statefulsets/
│   │       │   └── {name}/
│   │       │       ├── .statefulset.yaml
│   │       │       └── ...
│   │       │
│   │       ├── daemonsets/
│   │       │   └── {name}/
│   │       │       └── ...
│   │       │
│   │       ├── replicasets/
│   │       │   └── {name}/
│   │       │       └── ...
│   │       │
│   │       ├── jobs/
│   │       │   └── {name}/
│   │       │       └── ...
│   │       │
│   │       ├── cronjobs/
│   │       │   └── {name}/
│   │       │       └── ...
│   │       │
│   │       ├── services/
│   │       │   └── {name}/
│   │       │       ├── .service.yaml
│   │       │       ├── type.txt            # ClusterIP/NodePort/LoadBalancer
│   │       │       ├── cluster-ip.txt
│   │       │       ├── external-ip.txt
│   │       │       ├── ports.json
│   │       │       └── endpoints.json
│   │       │
│   │       ├── ingresses/
│   │       │   └── {name}/
│   │       │       ├── .ingress.yaml
│   │       │       ├── hosts.json
│   │       │       └── rules.json
│   │       │
│   │       ├── configmaps/
│   │       │   └── {name}/
│   │       │       ├── .configmap.yaml
│   │       │       └── data/
│   │       │           └── {key}           # Each key as a file
│   │       │
│   │       ├── secrets/
│   │       │   └── {name}/
│   │       │       ├── .secret.yaml        # Without data
│   │       │       ├── type.txt
│   │       │       └── data/
│   │       │           └── {key}           # Base64-decoded values
│   │       │
│   │       ├── pvcs/
│   │       │   └── {name}/
│   │       │       ├── .pvc.yaml
│   │       │       ├── status.txt
│   │       │       └── volume.txt          # Bound PV name
│   │       │
│   │       ├── serviceaccounts/
│   │       │   └── {name}.yaml
│   │       │
│   │       ├── roles/
│   │       │   └── {name}.yaml
│   │       │
│   │       ├── rolebindings/
│   │       │   └── {name}.yaml
│   │       │
│   │       ├── networkpolicies/
│   │       │   └── {name}.yaml
│   │       │
│   │       └── events/
│   │           └── {timestamp}-{reason}.txt
│   │
│   ├── cluster/                        # Cluster-scoped resources
│   │   ├── nodes/
│   │   │   └── {node}/
│   │   │       ├── .node.yaml
│   │   │       ├── status.json
│   │   │       ├── conditions.json
│   │   │       ├── capacity.json
│   │   │       ├── allocatable.json
│   │   │       └── pods/               # Pods on this node
│   │   ├── pvs/
│   │   │   └── {name}.yaml
│   │   ├── clusterroles/
│   │   │   └── {name}.yaml
│   │   ├── clusterrolebindings/
│   │   │   └── {name}.yaml
│   │   └── crds/
│   │       └── {name}.yaml
│   │
│   └── custom/                         # Custom resources
│       └── {group}/
│           └── {version}/
│               └── {kind}/
│                   └── {namespace}/
│                       └── {name}.yaml
│
└── .contexts.json                      # Available contexts
```

## Capabilities

- READ: List resources, view specs, read logs
- WRITE: Update resources, scale deployments
- CREATE: Apply manifests, create resources
- DELETE: Delete resources

## Configuration

```python
K8sVFS(
    kubeconfig="~/.kube/config",
    context=None,               # Use current context if not specified
    namespace=None,             # Default namespace filter
    cache_ttl=60,
    stream_logs=True,
)
```
"""

from .provider import K8sVFS
from .types import K8sPod, K8sDeployment, K8sService, K8sConfigMap, K8sSecret

__all__ = ["K8sVFS", "K8sPod", "K8sDeployment", "K8sService", "K8sConfigMap", "K8sSecret"]
__version__ = "0.1.0"

Provider = K8sVFS


def get_provider_class():
    return K8sVFS


def register(registry):
    registry.register(
        name="k8s",
        provider_class=K8sVFS,
        description="Kubernetes pods, deployments, services, configmaps",
        required_config=[],
        optional_config=["kubeconfig", "context", "namespace", "cache_ttl"],
    )
