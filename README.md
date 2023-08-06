# ApplicationSet Secret Plugin Generator
This is an Argo CD [ApplicationSet Plugin Generator](https://argo-cd.readthedocs.io/en/latest/operator-manual/applicationset/Generators-Plugin/) (_only available in Argo CD `v2.8.0` or newer_) to fetch variables from an existing [Kubernetes Secret](https://kubernetes.io/docs/concepts/configuration/secret/) that is mounted as file in our plugin generator deployment.

## Usage

<details>
  <summary>First, install Argo CD on your cluster. See More.</summary>
  
  This feature is currently only available in an (unsupported) pre-release state. We last tested this with `v2.8.0-rc7` which is the newest at time of writing. Check the [Releases page](https://github.com/argoproj/argo-cd/releases) for the latest version. To use a(n unsupported) pre-release, like `v2.8.0-rc7` with helm, override the `global.image.tag` parameter with the version of your choice in your values.yaml. Then, make sure you grab the updated ApplicationSet CRD for the tag you want to use e.g. [`v2.8.0-rc7`](https://github.com/argoproj/argo-cd/tree/v2.8.0-rc7/manifests/crds).

</details>

### Install with helm
For helm, see the [README](./charts/argocd-appset-secret-plugin/README.md) for full details of the allowed values in values.yaml, but this is the gist:

```bash
helm repo add appset-secret-plugin https://jessebot.github.io/argocd-appset-secret-plugin
helm install my-release appset-secret-plugin
```

### Install with Kustomize
See the [README](./kustomize/README.md) in the kustomize directory.

# Testing
You can create a Kubernetes Secret for your queriable variables, like this:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: argocd-secret-vars
  namespace: argocd
  labels:
    app.kubernetes.io/part-of: argocd
type: stringData
data:
  secret_vars.yaml: |
    app_name: "beepboop"
```

Here's an example ApplicationSet, using the secret plugin generator, to apply:
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
          name: secret-plugin-generator
        input:
          parameters:
            secret_vars: ["app_name"]
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
