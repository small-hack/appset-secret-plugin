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
helm repo add appset-secret-plugin repo_url
helm install my-release appset-secret-plugin
```

### Install with Kustomize
See the [README](./kustomize/README.md) in the kustomize directory.
