from dingtalk import SecretClient, AppKeyClient

# 旧 access_token 获取方式
#client = SecretClient('ding80f082a716941ab235c2f4657eb6378f', '1040330141093c05b09b12ca4712fea8')

client = AppKeyClient('ding80f082a716941ab235c2f4657eb6378f',
                      'dingzxe9guswfsidedvv',
                      'myajd8byuS97KqK3Qy2wRn3c4WRqsAHMFWSpEdMl9svESO4JkrQtNN93g-2FsWJZ')  # 新 access_token 获取方式
print(client.get_access_token().access_token)
users = client.user.list(1)
print(users)
departments = client.department.list(fetch_child=True)
print(departments)
