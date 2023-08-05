# ApplicationSet Environment Variable Plugin Generator
This is an Argo CD [ApplicationSet Plugin Generator](https://argo-cd.readthedocs.io/en/latest/operator-manual/applicationset/Generators-Plugin/) (_only available in Argo CD `v2.8.0` or newer_) to fetch environment variables from an existing Kubernetes Secret, called `argocd-env-vars` by default.

**NOTE**
We will only fetch environment variables beginning with `ARGOCD_ENV_VAR_PLUGIN_`.

## Testing

<details>
  <summary>First, install Argo CD on your cluster. See More.</summary>
  
  This feature is currently only available in an (unsupported) pre-release state. We last tested this with `v2.8.0-rc7`. To use a(n unsupported) pre-release, like `v2.8.0-rc7` with helm, override the `global.image.tag` parameter with the version of your choice in your values.yaml. Then, make sure you grab the updated ApplicationSet CRD for the tag you want to use e.g. [`v2.8.0-rc7`](https://github.com/argoproj/argo-cd/tree/v2.8.0-rc7/manifests/crds).

</details>

<details>
  <summary>Second, install the plugin generator's manifests using the below command. See more.</summary>

The manifests assume that Argo CD is installed in the `argocd` namespace, and you want to install the plugin generator in the same namespace. This kustomize command will [generate a `ConfigMap`](https://github.com/jessebot/argocd-applicationset-env-var-plugin/blob/main/kustomization.yaml#L7) with the [main.py](./main.py) in this repo, to be used for the ENTRYPOINT script for the Docker container in the small [deployment](./manifests/deployment.yaml) we create.

</details>

```bash
kustomize build | kubectl apply -f -
```

Finally, you can create a Kubernetes Secret for your variables, like this:
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

Here's an example ApplicationSet, using the generator, to apply:
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
