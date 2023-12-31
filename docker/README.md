# Argo CD ApplicationSet Secret Plugin Generator Container
This is the docker image for this plugin, which is published to:
https://hub.docker.com/r/jessebot/argocd-appset-secret-plugin

## Building

```bash
docker build . -t jessebot/argocd-appset-secret-plugin:dev
```

## Testing

Generate a fake token
```bash
openssl rand -base64 12 > token && export TOKEN=`/bin/cat token`
```

Create some test values you'd like to get in your fake ApplicationSet:

```bash
echo 'param1: "success"' > secret_vars.yaml
```

Run the docker container:

```bash
docker run \
  -v ./secret_vars.yaml:/var/run/secret-plugin/secret_vars.yaml \
  -v ./token:/var/run/argocd/token \
  -p 4355:4355 \
  jessebot/argocd-appset-secret-plugin:dev
```

Send a request for a vairable in your secret_vars.yaml:

```bash
curl http://localhost:4355/api/v1/getparams.execute -H "Authorization: Bearer $TOKEN" -d \
'{
  "applicationSetName": "fake-appset",
  "input": {
    "parameters": {
      "secret_vars": ["param1"]}
  }
}'
```

it should return this:

```curl
HTTP/1.0 200 OK
Server: BaseHTTP/0.6 Python/3.11.4
Date: Sat, 05 Aug 2023 13:20:33 GMT

{"output": {"parameters": [{"param1": "success"}]}}
```
