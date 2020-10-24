# params-register-task-definition

Docs:

- [AWS CLI - ecs register-task-definition](https://docs.aws.amazon.com/cli/latest/reference/ecs/register-task-definition.html)
- [AWS Developer guide - Amazon ECS Task Definitions](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definitions.html)

## Parameter list

arg | description
---|---
--family \<value\> | タスク定義の名前
[--task-role-arn \<value\>] | Task にアタッチする IAM Role
[--execution-role-arn \<value\>] | ECS Agent がタスクを実行するときに使用する IAM Role
[--network-mode \<value\>] | タスクの中で起動する docker コンテナのネットワークモード。none/brigde/awsvpc/host のいずれか。**Fargate の場合は `awsvpc` を指定しなければならない。**
--container-definitions \<value\> | 'コンテナ定義' のリスト（後述）
[--volumes \<value\>] | 'ボリューム定義' のリスト。Docker volume か、 EFS のストレージを使う場合に指定する ([参考](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/using_data_volumes.html))。
[--placement-constraints \<value\>] | Fargate ではサポートされない。コントロールプレーンが新しい Service/Task をどこで起動すべきか、決定するためのロジックをユーザー側で制約を付けるための項目。
[--requires-compatibilities \<value\>] | Task が満たすべき launch type を指定。 ECS/FARGATE のいずれかもしくは両方が指定可能。デフォルト値は 'ECS'
[--cpu \<value\>] | Task が使用する _CPU ユニット_ を指定。EC2 launch type ではオプショナル引数
[--memory \<value\>] | Task が使用するメモリ(MiB)を指定
[--tags \<value\>] | -
[--pid-mode \<value\>] | `docker run` の引数として使用可能な `--pid` に相当するもの
[--ipc-mode \<value\>] | `docker run` の引数として使用可能な [`--ipc`](https://docs.docker.com/engine/reference/run/#ipc-settings---ipc) に相当するもの（詳細は解説不可能）。 none/task/host が指定可能
[--proxy-configuration \<value\>] | App Mesh proxy の設定情報
[--inference-accelerators \<value\>] | Elastic Inference Accelerators を利用する場合の設定 ([doc](https://docs.aws.amazon.com/ja_jp/AmazonECS/latest/developerguide/deep-learning-containers.html))
[--cli-input-json \<value\>] | -
[--generate-cli-skeleton \<value\>] | -

タスク定義は、**どのようなコンテナが ECS で稼働するのか**を ECS に伝えます。タスク定義作成時に設定できることを日本語表現に置き換えると次のような内容になるでしょう。

- コンテナイメージ
- コンテナが使用する CPU, メモリリソース（タスク単位あるいはコンテナ単体での指定が可能）
- (未訳) The launch type to use, which determines the infrastructure on which your tasks are hosted
- Task の中で使用する Docker のネットワーキングモード
- タスクのロギング設定
- コンテナが実行終了した／fail した場合に、Task の実行は継続すべきかどうか
- コンテナが実行開始したときに、実行されるべきコマンド
- Any data volumes that should be used with the containers in the task
- タスクに対して割り当てる IAM Role

どのようなコンテナが起動するのか、あるいはコンテナ自身がどのような Spec で起動してほしいのか(what)、といった情報がタスク定義における関心事であり、そのコンテナを「どこで(where)、どのように(how)ローンチしたいのか」についてはタスク定義の概念から外れることがわかると思います。

案件のユースケースに対して、対応する設定は可能なのか／可能であるならどこで指定すれば良いのか？...そのようなケースに遭遇したら、この原則を（後述のサービス作成のパラメータ仕様とともに）覚えておくとよいでしょう。

### Network mode 'awsvpc' (--network-mode)

EC2 起動タイプで `awsvpc` ネットワークモードを利用する場合は、コンテナインスタンスは ECS-optimized AMI を用いたものであるか、もしくは `ecs-init` パッケージをインストールした Amazon Linux である必要がある

> Currently, only Amazon ECS-optimized AMIs, other Amazon Linux variants with the ecs-init package, or AWS Fargate infrastructure support the awsvpc network mode.

### Container definitions (--container-definition)

タスクの中で動かすコンテナの設定。複数コンテナの指定も可能。

このパラメータだけを見ても設定可能な項目が多いので [container-definition.md](container-definition.md) に別記します。

### Volume configuration (--volume)

[Developer guide (ECS) - Using data volumes in tasks](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/using_data_volumes.html)

Fargate の場合は、ボリュームとして "[Fargate Task Storage](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/fargate-task-storage.html)" もしくは "EFS" を利用可能。 Fargate Task Storage は Docker volume のようなもの。

タスク内のコンテナで共有可能なストレージを利用したい場合に検討すると良いでしょう。

#### Fargate Task Storage

[Developer guide (ECS) - Fargate Task Storage](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/using_data_volumes.html)

Fargate プラットフォームのバージョンが 1.4 (2020/10 時点の最新バージョン) の場合は、1つのタスクあたり 20GB が使用可能。上記のドキュメントで設定方法の例も記載されているので詳しくはそちらを参照。

#### Amazon EFS Volumes

[Developer guide (ECS) - Amzon EFS Volumes](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/efs-volumes.html)

### CPU Unit (--cpu) and Memory (--memory)

Fargate の場合は、以下の通り指定可能なレンジが存在する。
 
> If you are using the Fargate launch type, this field is required and you must use one of the following values, which determines your range of > supported values for the memory parameter:
> 
> 256 (.25 vCPU) - Available memory values: 512 (0.5 GB), 1024 (1 GB), 2048 (2 GB) <br/>
> 512 (.5 vCPU) - Available memory values: 1024 (1 GB), 2048 (2 GB), 3072 (3 GB), 4096 (4 GB) <br/>
> 1024 (1 vCPU) - Available memory values: 2048 (2 GB), 3072 (3 GB), 4096 (4 GB), 5120 (5 GB), 6144 (6 GB), 7168 (7 GB), 8192 (8 GB) <br/>
> 2048 (2 vCPU) - Available memory values: Between 4096 (4 GB) and 16384 (16 GB) in increments of 1024 (1 GB) <br/>
> 4096 (4 vCPU) - Available memory values: Between 8192 (8 GB) and 30720 (30 GB) in increments of 1024 (1 GB) <br/>

### PID Mode

`docker run` のオプション `--pid` に相当する設定項目([参考 - docker docs](https://docs.docker.com/engine/reference/run/#pid-settings---pid)

host/task のいずれかが指定可能で、 "process namespace" をホスト／タスクのスコープで共有することができます。

() 通常は、コンテナ内の PID 空間は独立しており、また共有する必要もないものです。プロセスの名前空間を共有するということは、そのプロセスに対してコミュニケーションできるということを意味するためです。しかし、それでもコンテナ自身の外の世界と PID 空間を利用したいシーンは存在し、[docker docs]((https://docs.docker.com/engine/reference/run/#pid-settings---pid)) ではデバッガを接続したい場合にコンテナとホスト間での PID 空間の共有が必要になる、と述べています（下記）。

> In certain cases you want your container to share the host’s process namespace, basically allowing processes within the container to see all of the processes on the system. For example, you could build a container with debugging tools like strace or gdb, but want to use these tools when debugging processes within the container.

※ process namespace 自体は Linux の用語であり、 [manpage](https://linuxjm.osdn.jp/html/LDP_man-pages/man7/pid_namespaces.7.html) でも解説を見ることができます。
