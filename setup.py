from setuptools import setup, find_packages

setup(
    name='dg_spider',
    version='1.0',
    packages=find_packages(),
    entry_points={'scrapy': ['settings = dg_spider.settings']},

    # 静态文件
    package_data={
        'dg_spider': ['resources/**/*'],
    },
    # exclude_package_data={
    #     'flask': ['application/*', 'flask.app.py'],
    # },
)

