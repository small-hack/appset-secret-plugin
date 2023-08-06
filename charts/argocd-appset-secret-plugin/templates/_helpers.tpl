{{/*
Expand the name of the chart.
*/}}
{{- define "argocd-appset-secret-plugin.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "argocd-appset-secret-plugin.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "argocd-appset-secret-plugin.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "argocd-appset-secret-plugin.labels" -}}
helm.sh/chart: {{ include "argocd-appset-secret-plugin.chart" . }}
{{ include "argocd-appset-secret-plugin.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "argocd-appset-secret-plugin.selectorLabels" -}}
app.kubernetes.io/name: {{ include "argocd-appset-secret-plugin.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "argocd-appset-secret-plugin.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "argocd-appset-secret-plugin.fullname" .) .Values.serviceAccount.name }}
{{- end }}
{{- end }}


{{/*

curl http://localhost:4355/api/v1/getparams.execute -H "Authorization: Bearer $PLUGIN_TOKEN" -d \
'{
  "applicationSetName": "fake-appset",
  "input": {
    "parameters": {
      "secret_vars": ["param1"]}
  }
}'

http://{{ include "argocd-appset-secret-plugin.fullname" . }}/api/v1/getparams.execute -H  \"Content-type:application/json\" -H \"Authorization: Bearer $TOKEN\" --data-urlencode \"{\"applicationSetName\": \"fake-appset\", \"input\": {\"parameters\": {\"secret_vars\": [\"app_name\"]}}}\"
*/}}
{{- define "argocd-appset-secret-plugin.testCommand" -}}
http://{{ include "argocd-appset-secret-plugin.fullname" . }}/api/v1/getparams.execute -H \"Authorization: Bearer $TOKEN\" -d \"{\"applicationSetName\": \"fake-appset\"}\"
{{- end }}

{{- define "argocd-appset-secret-plugin.tokenSecret" -}}
{{- if not .Values.token.existingSecret }}
{{- printf "%s-token" (include "argocd-appset-secret-plugin.fullname" .) }}
{{- else }}
{{ .Values.token.existingSecret }}
{{- end }}
{{- end }}

{{- define "argocd-appset-secret-plugin.varSecret" -}}
{{- if not .Values.secretVars.existingSecret }}
{{- printf "%s-secret-vars" (include "argocd-appset-secret-plugin.fullname" .) }}
{{- else }}
{{ .Values.secretVars.existingSecret }}
{{- end }}
{{- end }}
