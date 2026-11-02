# GitHub Actions 验证

模板：`deploy/ci/verify.yml`。

当前 GitHub token（`gho_...`）只有 `gist`、`read:org`、`repo`，没有
`workflow` scope，因此无法推送 `.github/workflows/verify.yml`。启用步骤：

```bash
gh auth refresh -s workflow
mkdir -p .github/workflows
cp deploy/ci/verify.yml .github/workflows/verify.yml
git add .github/workflows/verify.yml
git commit -m "ci: enable verify workflow"
git push origin main
```

本地等价检查（不改文件，CI 的同一组命令）：

```bash
bash tools/verify.sh
```

注意：`tools/verify.sh` 末尾会跑 `git diff --exit-code`；如果
`assets/tm-offline-kb.js`、`index.html` 的内联 KB 或 `sitemap.xml` 与生成器
不一致，会失败并要求先运行生成器。
