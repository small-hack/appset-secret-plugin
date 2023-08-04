# ApplicationSet Environment Variable Plugin Generator
This is an Argo CD [ApplicationSet Plugin Generator](https://argo-cd.readthedocs.io/en/latest/operator-manual/applicationset/Generators-Plugin/) to fetch environment variables from an existing Kubernetes Secret, called `argocd-env-vars` by default.

**NOTE**: We will only fetch environment variables beginning with `ARGOCD_ENV_VAR_PLUGIN_`.

## Testing

First, install Argo CD on your cluster.

Second, install the plugin generator's manifests. The manifests assume that Argo CD is installed in the `argocd` namespace, and you want to install the plugin generator in the same namespace.

```bash
kustomize build | kubectl apply -f -
```

Here's an example k8s secret that we would reference:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: argocd-env-vars
  namespace: argocd
  labels:
    app.kubernetes.io/part-of: argocd
type: Opaque
data:
  # The secret value must be base64 encoded **once**.
  # This value corresponds to: `printf "beepboop" | base64`.
  ARGOCD_ENV_VAR_PLUGIN_APP_NAME: "YmVlcGJvb3A="
```

Here's an example ApplicationSet to apply:
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
          name: env-var-plugin-generator
        input:
          parameters:
            env_vars: ["ARGOCD_ENV_VAR_PLUGIN_APP_NAME"]
  template:
    metadata:
      name: "from-appset-{{.ARGOCD_ENV_VAR_PLUGIN_APP_NAME}}"
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
