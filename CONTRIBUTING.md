## テスト

```bash
$ pip install tox
$ tox
```

- tox の install はアプリケーションの virtualenv と同じである必要はありません
- `$ tox` は `tox.ini` と同じディレクトリで実行してください

## ChangeLog.txtの更新

- masterbranch に修正を反映させる時に ChangeLog.txt には以下形式で内容を記入ください

```
Release Notes - <masterbranchにmergeした日>
-----------------------------------------------
- [<branch名>] <issue名 or 修正概要名>
```
