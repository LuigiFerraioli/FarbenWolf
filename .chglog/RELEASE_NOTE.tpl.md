{{ range .Versions }}
<a name="{{ .Tag.Name }}"></a>
## [{{ .Tag.Name }}] - {{ datetime "2006-01-02" .Tag.Date }}
{{ range .CommitGroups -}}
### {{ .Title }}
{{ range .Commits -}}
- {{ .Subject }}
{{ end }}
{{ end }}
{{ if .Tag.Previous }}
[{{ .Tag.Name }}]: {{ $.Info.RepositoryURL }}/compare/{{ .Tag.Previous.Name }}...{{ .Tag.Name }}
{{ end }}
{{ end }}