# ApplicationSet Secret Plugin Generator

<a href="https://github.com/small-hack/appset-secret-plugin/releases"><img src="https://img.shields.io/github/v/release/small-hack/appset-secret-plugin?style=plastic&labelColor=blue&color=028A0F&logo=GitHub&logoColor=white"></a> [![](https://img.shields.io/docker/pulls/jessebot/argocd-appset-secret-plugin.svg)](https://cloud.docker.com/u/jessebot/repository/docker/jessebot/argocd-appset-secret-plugin)

[appset-secret-plugin](https://github.com/small-hack/appset-secret-plugin) is an Argo CD [ApplicationSet Plugin Generator](https://argo-cd.readthedocs.io/en/latest/operator-manual/applicationset/Generators-Plugin/) (_only available in Argo CD `v2.8.0` or newer_) to fetch variables from an existing [Kubernetes Secret](https://kubernetes.io/docs/concepts/configuration/secret/) that is mounted as a file in our plugin generator deployment.

🆕 Now we reload your Kubernetes Secret at a configurable interval!

## Usage

First, [install Argo CD](https://argo-cd.readthedocs.io/en/stable/getting_started/#1-install-argo-cd) on your cluster.

### Install with helm

For helm, see the [`README`](./charts/appset-secret-plugin/README.md) for full details of the allowed values in [`values.yaml`](./charts/appset-secret-plugin/values.yaml), but this is the gist for testing:

```console
helm repo add appset-secret-plugin https://small-hack.github.io/appset-secret-plugin
helm install my-release-name appset-secret-plugin/appset-secret-plugin
```

You'll likely want to pass in a value for an existing Kubernetes Secret containing your secret keys you want to be available to the Plugin Generator. To do that, let's say the name of your Kubernetes Secret is `my-secret-name`, you can try this:

```console
helm install my-release-name appset-secret-plugin/appset-secret-plugin \
   --set secretVars.existingSecret=my-secret-name
```

### Install with Kustomize

See the [README](./kustomize/README.md) in the kustomize directory. ⚠️This method has not been tested in over a year.

# Testing

You can create a Kubernetes Secret for your queriable variables, like this:

```yaml
apiVersion: v1
kind: Secret
metadata:
  # configurable with secretVars.existingSecret helm parameter
  name: argocd-secret-vars
  # this needs to be where-ever argocd is running
  namespace: argocd
  labels:
    app.kubernetes.io/part-of: argocd
    # can be configured to use a different label and value with by setting
    # configReloader.label and configReloader.labelValue helm parameters
    argocd-appset-secret-plugin: 1
type: stringData
data:
  # configurable with secretVars.secretKey helm parameter
  secret_vars.yaml: |
    app_name: "beepboop"
```

Here's an example Argo CD `ApplicationSet`, using the secret plugin generator, to apply:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: my-application-set
spec:
  goTemplate: true
  goTemplateOptions: ["missingkey=error"]
  generators:
    - plugin:
        configMapRef:
          name: secret-var-plugin-generator
        input:
          parameters:
            secret_vars:
              # this grabs a parameter called app_name from the secret above
              - app_name
  template:
    metadata:
      name: "from-appset-{{.app_name}}"
    spec:
      project: default
      source:
        repoURL: https://github.com/argoproj/argocd-example-apps.git
        path: guestbook
      destination:
        server: https://kubernetes.default.svc
        namespace: default
```

You can apply the example ApplicationSet and Secret with:

```bash
kubectl apply -f example/appset_and_secret.yaml
```

### Status
This is beta project still, but I'm working on getting to stable. Please open a GitHub Issue with your method of installation, your distro of k8s and the version of your k8s tooling (kustomize, helm, etc), if you're having any trouble. Also, always happy to look at PRs :)
