from kubernetes import client, config
from kubernetes.client.exceptions import ApiException

# Load kubeconfig
config.load_kube_config()

# API clients
apps_api = client.AppsV1Api()
core_api = client.CoreV1Api()

namespace = "default"

# ------------------------
# Deployment Definition
# ------------------------
deployment = client.V1Deployment(
    metadata=client.V1ObjectMeta(name="my-flask-app"),
    spec=client.V1DeploymentSpec(
        replicas=1,
        selector=client.V1LabelSelector(
            match_labels={"app": "my-flask-app"}
        ),
        template=client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(
                labels={"app": "my-flask-app"}
            ),
            spec=client.V1PodSpec(
                containers=[
                    client.V1Container(
                        name="flask-container",
                        image="cloudnative:latest",
                        image_pull_policy="IfNotPresent",
                        ports=[
                            client.V1ContainerPort(
                                container_port=5000,
                                name="http"
                            )
                        ]
                    )
                ]
            )
        )
    )
)

# Create Deployment
try:
    apps_api.create_namespaced_deployment(
        namespace=namespace,
        body=deployment
    )
    print("Deployment created")
except ApiException as e:
    if e.status == 409:
        print("Deployment already exists")
    else:
        raise


# ------------------------
# Service Definition
# ------------------------
service = client.V1Service(
    metadata=client.V1ObjectMeta(name="my-flask-service"),
    spec=client.V1ServiceSpec(
        type="NodePort",
        selector={"app": "my-flask-app"},
        ports=[
            client.V1ServicePort(
                name="http",
                port=5000,
                target_port=5000,
                node_port=30007
            )
        ]
    )
)

# Create Service
try:
    core_api.create_namespaced_service(
        namespace=namespace,
        body=service
    )
    print("Service created")
except ApiException as e:
    if e.status == 409:
        print("Service already exists")
    else:
        raise
