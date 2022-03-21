# quick start
* python3.8+

* 安装虚拟环境(optional)
```powershell
pip install virtualenv
virtualenv .venv
.venv/Scripts/activate
```
* 安装库
```shell
pip install -r requirements.txt
```
* 生成数据库和静态文件
```
python .\manage.py makemigrations  
python .\manage.py migrate
python .\manage.py collectstatic
```
* 生成超级用户(optional)
```shell
python .\manage.py createsuperuser
```
* 启动
```shell
python .\manage.py runserver
// or
uvicorn library_portal.asgi:application
```