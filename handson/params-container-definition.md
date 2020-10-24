# container-definition

`ecs register-task-definition` のオプションとして指定する `--container-definitions` の仕様について解説します。

## 基本的なパラメータ

[Developr guide (ECS) - Task Definition Parameters - Standard Container Definition Parameters](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definition_parameters.html#standard_container_definition_params)

以下の4要素に関する設定が基本的なパラメータとなります。

- Name
- Image
- Memory
- Port Mappings

param | description
---|---
name | コンテナの名前、同一の Task definition の中で複数コンテナを定義し、それらのコンテナ同士をリンクさせる場合はこの名前で参照が可能になる
image | イメージの指定。 `repository-url/image:tag` または `repository-url/image@digest` の形式で指定。ECR の場合は `<aws_account_id>.dkr.ecr.<region>.amazonaws.com/<repository>:<tag-or-digest>` の形式でも指定可能
memory | MiB 単位でコンテナが使用可能なメモリの上限を指定する（ハードリミット）
memoryReservation | MiB 単位でコンテナが使用可能なメモリの上限を指定する（ソフトリミット）
portMappings | コンテナホストとコンテナ間のポートマッピング

### memory

Fargate の場合、指定は任意。
Memory で指定したメモリ以上をコンテナが確保しようとした場合、**そのコンテナは kill されます**。

Task definition の `Memory` パラメータの値を超えないように指定する必要があります。

### memoryReservation

`docker run` の `--memory-reservation` に相当。

[docker docs](https://docs.docker.com/engine/reference/run/#runtime-constraints-on-resources)

`memory` がハードリミットであるのに対して、 `memoryReservation` はソフトリミットとしてコンテナが使用できるメモリの上限を設定するものです。
ホストのメモリ状況に余裕があれば、必要に応じてコンテナは `memoryReservation` 以上のメモリを使用することがある。しかし、ホストのメモリが切迫してきた場合には、ソフトリミットの値に基づいてメモリの確保を制限しようとします。

参考: [Qiita - Dockerのメモリ制限に関するメモ](https://qiita.com/irotoris/items/944aba5e448a8e723ff6#--memory-reservation)

### portMappings

※ここでは `awsvpc` ネットワークモードを使用する場合のみ解説します。

コンテナホストとコンテナ間のポートマッピングを設定します。コンテナホストとコンテナを繋ぐ NAT のようなものです。

`awsvpc` ネットワークモードでは、 `containerPort` のみを指定すべきです。
`hostPort` は空白にするか、 `contarinerPort` と同じ値にする必要があります。

このパラメータはマッピングオブジェクトのリストとして指定します。1つのマッピングオブジェクトは次の属性を持ちます。

attr | type | required? | description
---|---|---
containerPort | int | yes | コンテナ自身が公開するポート
hostPort | int | no | コンテナインスタンス(コンテナホスト) 側のポート。省略または 0 を指定した場合は動的なポートマッピング (49153–65535) を行う
protocol | str | no | ポートマッピングに使用するプロトコル。 tcp/udp のいずれかが使用可能 (default=tcp)。

```json
[
    {
        "containerPort": 8000,
    }
]
```

## Advanced

[Developer guide (ECS) - Task definitions - advanced Container Definition Parameters](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definition_parameters.html#advanced_container_definition_params)


### Health Check

コンテナがホストに対して公開するヘルスチェック用の設定。

`docker run` の引数に対応する。 ([docker docs](https://docs.docker.com/engine/reference/run/#healthcheck))

### Environment

param | type | description
---|---|---
cpu | - | -
gpu | - | -
essential | bool | (default false) true にすると、そのコンテナが落ちた時にタスクに含まれる他のすべてのコンテナが停止するようになる 
entryPoint | - | `docker run` の `--entrypoint` にマップする
command | - | `docker run` の `[COMMAND]` にマップする
workingDirectory | - | `docker run` の `--workdir` にマップする
environmentFiles | - | `docker run` の `--env-file` にマップする
environment | - | `docker run` の `--env` にマップする
secrets | - | -

`secrets` を利用することで、 Parameter Store のパラメータを環境変数として読み込むことが可能になる。設定例は次の通り。

```json
"secrets": [
    {
        "name": "environment_variable_name",
        "valueFrom": "arn:aws:ssm:region:aws_account_id:parameter/parameter_name"
    }
]
```

### Network Settings

---

### Storage and Logging

- readonlyRootFilesystem
- mountPoints
- logConfiguration
- firelensConfiguration

#### logConfiguration

[LogConfiguration](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_LogConfiguration.html) タイプのオブジェクト

docker では、コンテナ作成時の `LogConfig` 、または `docker run` の `--log-driver` オプションに対応する。
完全な docker 互換ではなく、AWS ECS における拡張として `awslogs` , `awsfirelens` という値も使用可能。

fargate の場合は `awslogs`, `splunk`, `awsfirelens` の3つが指定可能。

`awslogs` では、コンテナのログは CloudWatch Logs へ転送される。 `awslogs` を使った場合の設定の例は次の通り。

```json
"logConfiguration": {
    "logDriver": "awslogs",
    "options": {
        "awslogs-group": "/ecs/my-app",
        "awslogs-region": "ap-northeast-1",
        "awslogs-stream-prefix": "ecs"
    }
}
```


#### firelensConfiguration

...

[AWS Docs](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/using_firelens.html)）

### Security

...

### Resource Limits

...

### Docker Labels

...
