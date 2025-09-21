# interview
面试题

本项目用了FastAPI, 整个测试跑通了

1. 在宿主机启动了推流服务器,使用的是mediamtx
2. 在docker上,建立了python3.10的环境,并写了 post event 和 get task 两个方法
3. 使用线程池做异步(测试用),如果需要高性能,需要加celery
