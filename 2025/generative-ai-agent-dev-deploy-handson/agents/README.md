# deploy with python command
```__
python3 -m app.agent_engine_app --project __PROJECT_NAME__ --agent-name __AGENT_NAME__
```


# deploy with cloud build
こちらは cloud build を使ったデプロイの方法です。
cloud build の trigger を設定すると 自動デプロイが組み込めます。

```
gcloud builds submit . --config cloudbuild.yaml
     --substitutions=_PROJECT_ID=gossy-workstations,_REGION=us-central1,_AGENT_NAME=my-
     awesome-agent
```

https://cloud.google.com/build/docs/triggers
