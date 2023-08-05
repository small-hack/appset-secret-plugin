# Kustomize Testing

Second, clone the repo and modify the [kustomize.yaml](./kustomization.yaml) secretGenerator section to be a better token than `supersecret`:

```yaml
secretGenerator:
  - name: arogocd-generator-plugin-token
    literals:
      - token=supersecret
```

<details>
  <summary>Third, install the plugin generator's manifests using the below command. See more.</summary>

The manifests assume that Argo CD is installed in the `argocd` namespace, and you want to install the plugin generator in the same namespace. This kustomize command your secret above to be used for the ENTRYPOINT script for the Docker container in the small [deployment](./manifests/deployment.yaml) we create.

</details>

```bash
kustomize build | kubectl apply -f -
```

Finally, you can create a Kubernetes Secret for your queriable variables, like this:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: argocd-secret-vars
  namespace: argocd
  labels:
    app.kubernetes.io/part-of: argocd
type: Opaque
data:
  # The secret value must be base64 encoded **once**.
  # This value corresponds to: `printf "beepboop" | base64`.
  app_name: "YmVlcGJvb3A="
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
