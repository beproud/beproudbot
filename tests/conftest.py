def pytest_runtest_setup(item):
    dbtest = item.get_marker('dbtest')
    if dbtest:
        # テスト用のデータベースを構築する
        # ファクトリーやテストでSession使えるようになる
        from db import Base, init_dbsession
        conf = {
            'sqlalchemy.url': 'sqlite://',
        }
        init_dbsession(conf)
        Base.metadata.create_all()
