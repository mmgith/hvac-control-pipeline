import sys
import os
import getopt
import yaml
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from pprint import pprint

configMapDict = {
    "HOST": os.environ["HVAC_HOST"],
    "TICKETS": os.environ["HVAC_TICKETS"],
    "T_MAX": os.environ["T_MAX"],
    "T_MIN": os.environ["T_MIN"],
}

secretDict = {
    "TOKEN": os.environ["HVAC_TOKEN"],
}


def create_configmap_object(namespace):
    metadata = client.V1ObjectMeta(
        name="hvac-env",
        namespace=namespace,
    )
    configmap = client.V1ConfigMap(
        api_version="v1",
        kind="ConfigMap",
        data=configMapDict,
        metadata=metadata,
    )
    return configmap


def create_configmap(api_instance, configmap, namespace):
    try:
        api_response = api_instance.create_namespaced_config_map(
            namespace=namespace,
            body=configmap,
        )
        pprint(api_response)

    except ApiException as e:
        print(
            "Exception when calling CoreV1Api->create_namespaced_config_map: %s\n" % e
        )


def create_secret_object(namespace):
    metadata = client.V1ObjectMeta(
        name="hvac-secret",
        namespace=namespace,
    )
    secret = client.V1Secret(
        api_version="v1",
        kind="Secret",
        string_data=secretDict,
        data={},
        metadata=metadata,
    )
    return secret


def create_secret(api_instance, secret, namespace):
    try:
        api_response = api_instance.create_namespaced_secret(
            namespace=namespace,
            body=secret,
        )
        pprint(api_response)

    except ApiException as e:
        print("Exception when calling CoreV1Api->create_namespaced_secret: %s\n" % e)


def create_deployment(api_instance, namespace, docker_image):

    with open(os.path.join(os.path.dirname(__file__), "./templates/deploy.yaml")) as f:
        dep = yaml.safe_load(f)
        if docker_image != "":
            dep["spec"]["template"]["spec"]["containers"][0]["image"] = docker_image

    try:
        api_response = api_instance.delete_namespaced_deployment(
            name=dep["metadata"]["name"],
            namespace=namespace,
        )
        pprint(api_response)

    except ApiException as e:
        print("Exception when calling CoreV1Api->create_namespaced_secret: %s\n" % e)

    try:
        api_response = api_instance.create_namespaced_deployment(
            namespace=namespace,
            body=dep,
        )
        pprint(api_response)

    except ApiException as e:
        print("Exception when calling CoreV1Api->create_namespaced_secret: %s\n" % e)


def main(argv):

    arg_config_file = ""
    arg_namespace = ""
    arg_docker_image = ""
    arg_help = "***.py -c <config file path> -n <namespace> -i <docker image>".format(
        argv[0]
    )

    try:
        opts, args = getopt.getopt(
            argv[1:], "hc:n:i:", ["help", "config=", "namespace=", "image="]
        )
    except:
        print(arg_help)
        sys.exit(2)

    if len(opts) < 2:
        print(f"Wrong arguments, you can run it with : {arg_help}")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(arg_help)  # print the help message
            sys.exit(2)
        elif opt in ("-c", "--config"):
            arg_config_file = arg
        elif opt in ("-n", "--namespace"):
            arg_namespace = arg
        elif opt in ("-i", "--image"):
            arg_docker_image = arg

    config.load_kube_config(config_file=arg_config_file)
    api_instance = client.CoreV1Api()
    app_instance = client.AppsV1Api()

    configmap = create_configmap_object(arg_namespace)
    secret = create_secret_object(arg_namespace)

    create_configmap(api_instance, configmap, arg_namespace)
    create_secret(api_instance, secret, arg_namespace)
    create_deployment(app_instance, arg_namespace, arg_docker_image)


if __name__ == "__main__":
    main(sys.argv)
