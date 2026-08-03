# VAFOX Huyan IA V1.1 代码来源确认

## 1. 当前仓库地址（remote URL）

- 当前工作副本没有配置 Git remote（`git remote -v` 无输出）。
- `.git/FETCH_HEAD` 记录本工作副本最近一次从以下仓库的 `main` 分支获取：

  ```text
  https://github.com/huyanyong2026/foxbrain-faos
  ```

## 2. commit `8efd3af` 的完整 commit hash

**无法从当前工作副本确认。** 当前仓库的全部本地对象中不存在以 `8efd3af` 开头的 commit；`git rev-parse '8efd3af^{commit}'` 返回“unknown revision”。因此不能可靠地补全该短 hash，也不应推测或伪造完整 hash。

生产拉取前，应在能够访问远端仓库的环境中运行：

```bash
git fetch https://github.com/huyanyong2026/foxbrain-faos '+refs/heads/*:refs/remotes/source/*' --tags --prune
git rev-parse '8efd3af^{commit}'
```

只有第二条命令成功输出的 40 位值，才是可用于部署的完整 commit hash。

## 3. 所在分支名称

**无法确认 `8efd3af` 所在分支。** 该 commit 不在当前工作副本中，因而 `git branch -a --contains 8efd3af` 无法查询。已确认的来源分支仅为 `.git/FETCH_HEAD` 所记录的 `main`；当前本地检出分支为 `work`，不能据此断言 `8efd3af` 属于其中任一分支。

远端可访问后，可用以下命令确认：

```bash
git fetch https://github.com/huyanyong2026/foxbrain-faos '+refs/heads/*:refs/remotes/source/*'
git branch -r --contains '8efd3af^{commit}'
```

## 4. 生产服务器拉取所需仓库地址

仓库地址：

```text
https://github.com/huyanyong2026/foxbrain-faos
```

全新部署：

```bash
git clone https://github.com/huyanyong2026/foxbrain-faos
cd foxbrain-faos
git fetch --all --tags --prune
```

已有工作副本但尚未配置 remote：

```bash
git remote add origin https://github.com/huyanyong2026/foxbrain-faos
git fetch origin --tags --prune
```

已有 `origin`：

```bash
git remote set-url origin https://github.com/huyanyong2026/foxbrain-faos
git fetch origin --tags --prune
```

> 在完整 hash 和所属远端分支得到确认前，不应将 `8efd3af` 作为已验证的生产部署版本。
