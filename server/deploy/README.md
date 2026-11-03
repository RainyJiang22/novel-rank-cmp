# NovelRank 独立部署与回滚

当前入口：`https://47.251.189.239/novelrank`，接口文档为 [/novelrank/docs](https://47.251.189.239/novelrank/docs)。实际检查结果见 [云部署记录](../../docs/features/rankings/v0.1.0/server/deployment.md)。

## 隔离边界

| 项目 | 配置 |
| --- | --- |
| 源码 | `/opt/novelrank/releases/<release-id>`；`/opt/novelrank/current` 指向当前版本 |
| Python | 独立 `/opt/novelrank/venv`，Python 3.11+，只安装 `server/requirements.txt` |
| 系统用户 / 服务 | `novelrank` / `novelrank.service` |
| 监听 | `127.0.0.1:18766`，单 Uvicorn worker；不开放新公网端口 |
| 资源 | `MemoryMax=256M`、`CPUQuota=50%`（单核的 50%）、`TasksMax=64`、`Nice=10` |
| 应用并发 | Uvicorn 并发上限 32；来源请求并发 4、同站间隔 0.5 秒；按需请求，无后台扫榜 |
| Nginx 限流 | 独立 `novelrank_requests` / `novelrank_connections` zone，每 IP 3 请求/秒、burst 10、连接 8 |
| 配置 / 日志 | `/etc/novelrank/`、`/var/log/novelrank/`；日志轮转只匹配本服务文件 |

现有 HTTPS 根路径继续代理原应用并使用原认证。只在 `/novelrank` 和 `/novelrank/` 关闭继承的 Basic Auth，提供公开排名 API；不修改证书、原 upstream、认证文件、数据库、原虚拟环境或防火墙。

Nginx 的 `limit_req`、`limit_conn` 在下层没有相应指令时会继承上层配置，因此新 location 显式使用独立 zone，避免占用原站点的限流计数器。依据：[limit_req](https://nginx.org/en/docs/http/ngx_http_limit_req_module.html)、[limit_conn](https://nginx.org/en/docs/http/ngx_http_limit_conn_module.html)。这些限制用于控制新服务资源占用；同机服务仍共享宿主机与 Nginx。

## 首次安装

以下是运维步骤，先确认目标文件和端口未被占用；不要直接覆盖已有同名服务。当前机器已完成安装，无需重复执行。

1. 记录已有服务 PID/状态和根路径认证响应；备份当前 HTTPS 配置。确认 `127.0.0.1:18766` 未占用。只上传 `server/app/`、固定依赖和部署模板，不上传 `.venv`、个人 `.env`、SDK 路径、SSH 配置或凭据。
2. 创建专属非登录系统用户 `novelrank`，将源码放入独立 release 目录。使用 `python3.11 -m venv /opt/novelrank/venv`，以该环境的 Python 安装 `server/requirements.txt` 并执行 `pip check`；不要使用系统 pip 或其他服务的 venv。
3. 建立 `/opt/novelrank/current` 指向该 release 的软链。将 [novelrank.service](novelrank.service) 安装为 `/etc/systemd/system/novelrank.service`，执行 `systemctl daemon-reload` 与 `systemctl enable --now novelrank.service`。先验证内部健康检查：

   ```bash
   curl --fail http://127.0.0.1:18766/health
   systemctl show novelrank.service --property=ActiveState,MainPID,MemoryMax,CPUQuotaPerSecUSec,TasksMax
   ```

4. 将 [nginx-limits.conf](nginx-limits.conf) 放在 Nginx **http 上下文**中被加载的独立配置。当前宝塔机器路径为 `/www/server/panel/vhost/nginx/novelrank-limits.conf`；不要在 `server` 或 `location` 内声明 zone。
5. 将 [nginx-location.conf](nginx-location.conf) 安装到 `/etc/novelrank/nginx-location.conf`，在现有目标 HTTPS `server` 内只增加一行：

   ```nginx
   include /etc/novelrank/nginx-location.conf;
   ```

   当前目标文件为 `/www/server/panel/vhost/nginx/ipa-review-https.conf`。不要替换整个 `server` 或 `location /`。`proxy_pass` 末尾的 `/` 用于去除外部 `/novelrank/` 前缀，Uvicorn `--root-path /novelrank` 使 Swagger/OpenAPI 使用正确公开路径。
6. 先执行 `nginx -t`，成功后才 `nginx -s reload`。这是平滑加载，不停止原应用或 Nginx master。若校验失败，撤回本次 include 与新配置，不加载错误配置。
7. 将 [novelrank.logrotate](novelrank.logrotate) 安装到 `/etc/logrotate.d/novelrank`，先 `logrotate -d /etc/logrotate.d/novelrank` 检查。规则只轮转 `/var/log/novelrank/nginx-*.log`，保留 7 份；`copytruncate` 不发送任何 Nginx 信号，轮转瞬间可能丢失少量日志。`maxsize` 在系统 logrotate 调度时检查，并非实时磁盘配额。

可选环境变量放在 `/etc/novelrank/environment`，参考 [服务端变量示例](../.env.example)，不要提交实际配置。服务以只读文件系统权限运行，无数据库和持久化榜单文件；重启仅清除本服务内存缓存。

## 验证与日常检查

从外网正常校验证书，不使用 `-k`：

```bash
curl --fail https://47.251.189.239/novelrank/health
curl --fail https://47.251.189.239/novelrank/api/v1/catalog
curl --fail 'https://47.251.189.239/novelrank/api/v1/rankings?source=fanqie&category=1_261&board=reading'
```

仓库中的链路脚本验证正常查询、缓存、冷却、400/422 及跨来源状态：

```bash
.venv/bin/python docs/features/rankings/api/rankings/request/rankings.py \
  --base-url https://47.251.189.239/novelrank \
  --docs-dir .verification/cloud/api-doc \
  --evidence-label '云端 HTTPS 服务 / 真实上游'
```

返回 HTTP 200 不等同来源可用：同时检查业务 `status`、`message`、`books`。不要为“通过”隐藏上游受限状态。默认测试要求番茄查询取得数据；`--allow-upstream-failure` 只适合显式注明契约验证的场景。

运维只操作新服务：`systemctl status novelrank.service`、`journalctl -u novelrank.service`。配置更新时只重启 `novelrank.service`；应用更新先创建新 release、使用匹配的依赖环境并验证，再切换软链。不要重启或清理其他服务来释放资源。

## 回滚

初次备份位于服务器 `/etc/novelrank/backups/20261103-initial/`。回滚按当前配置做最小变更，避免用旧备份覆盖其他人后续修改：

1. 从目标 HTTPS `server` 中移除仅属于 NovelRank 的 include；移出 `novelrank-limits.conf`，检查差异后执行 `nginx -t`。
2. 检查通过后 `nginx -s reload`；确认原站点仍为原认证响应。
3. `systemctl disable --now novelrank.service`，只停止新服务。保留 release、备份和日志用于排查；不删除原应用目录、数据、证书或用户。
4. 如需回退应用版本，保留公网路由，仅将 `current` 指向已验证的旧 release，并只重启 NovelRank；需要同时匹配依赖版本。

所有实际 SSH 配置、备份、原始探测记录和日志留在本地忽略目录或服务器上。
