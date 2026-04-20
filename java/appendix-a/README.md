# README

首先需要获取WSL的IP地址，以便Server和Client能够连接到RabbitMQ。
        
            
toolName: run_command
            
status: success
          
command: wsl hostname -I undefined
          
现在需要修改Server.java和Client.java文件，将RabbitMQ的连接地址设置为WSL的IP地址172.18.176.57。
        
            
toolName: edit_file_search_replace
            
status: success
          
            
filePath: D:\develops\git\github\java\sourcecode\java\appendix-a\src\main\java\Server.java
          
changes: undefined
          
现在需要修改Client.java文件，同样将RabbitMQ的连接地址设置为WSL的IP地址172.18.176.57。
        
            
toolName: edit_file_search_replace
            
status: success
          
            
filePath: D:\develops\git\github\java\sourcecode\java\appendix-a\src\main\java\Client.java
          
changes: undefined
          
现在需要重新编译项目，然后运行Server和Client。
        
            
toolName: run_command
            
status: success
          
command: mvn compile undefined
          
现在需要启动Server，它会持续运行并等待RPC调用。
        
            
toolName: run_command
            
status: running
          
command: mvn exec:java -Dexec.mainClass="Server" undefined
          
需要检查Server是否成功启动，等待几秒钟后查看运行状态。
        
            
toolName: check_command_status
            
status: success
          
          
Server正在启动中，需要等待更长时间让它完成依赖下载和启动过程。
        
            
toolName: check_command_status
            
status: success
          
          
命令格式有误，需要修正exec:java命令的参数格式。
        
            
toolName: run_command
            
status: running
          
command: mvn exec:java -Dexec.mainClass=Server undefined
          
PowerShell对Maven参数解析有问题，我需要直接使用java命令运行编译后的class文件。
        
            
toolName: run_command
            
status: running
          
command: java -cp target/classes Server undefined
          
需要先复制依赖到本地目录，然后在运行时包含这些依赖。
        
            
toolName: run_command
            
status: success
          
command: mvn dependency:copy-dependencies -DoutputDirectory=lib undefined
          
现在使用包含所有依赖的classpath来运行Server。
        
            
toolName: run_command
            
status: running
          
command: java -cp "target/classes;lib/*" Server undefined
          
Server连接RabbitMQ失败，因为认证失败。需要在WSL中检查RabbitMQ状态并创建正确的用户。
        
            
toolName: run_command
            
status: running
          
command: wsl sudo rabbitmqctl status undefined
          
WSL需要密码，我需要先检查RabbitMQ是否运行，然后创建所需的用户。
        
            
toolName: run_command
            
status: success
          
command: wsl ps aux | grep rabbitmq undefined
          
需要在WSL中检查RabbitMQ状态并创建用户。先使用PowerShell的方式检查。
        
            
toolName: run_command
            
status: success
          
command: wsl "ps aux | grep rabbitmq" undefined
          
需要在WSL中直接运行命令来检查RabbitMQ状态并创建用户。
        
            
toolName: run_command
            
status: success
          
command: wsl -e bash -c "ps aux | grep rabbitmq" undefined
          
RabbitMQ正在运行，现在需要在WSL中创建rpc_user用户并设置密码。
        
            
toolName: run_command
            
status: success
          
command: wsl -e bash -c "sudo rabbitmqctl add_user rpc_user rpcme" undefined
          
现在需要给rpc_user用户设置权限，让它能够访问默认的虚拟主机。
        
            
toolName: run_command
            
status: success
          
command: wsl -e bash -c "sudo rabbitmqctl set_permissions -p / rpc_user '.*' '.*' '.*'" undefined
          
现在用户已创建并设置了权限，重新运行Server。
        
            
toolName: run_command
            
status: running
          
command: java -cp "target/classes;lib/*" Server undefined
          
Server已经成功启动，现在需要打开一个新终端来运行Client。
        
            
toolName: run_command
            
status: success
          
command: java -cp "target/classes;lib/*" Client undefined
          
Client已经成功运行并接收到了Server的响应，现在需要检查Server的状态，看看它是否正确处理了请求。
        
            
toolName: check_command_status
            
status: success
          
          
我已经成功完成了运行Server和Client的任务，具体过程如下：

1. **获取WSL IP地址**：通过`wsl hostname -I`命令获取到WSL的IP地址为`172.18.176.57`

2. **配置连接信息**：
   - 修改了Server.java和Client.java文件，将RabbitMQ的连接地址设置为WSL的IP地址

3. **创建RabbitMQ用户**：
   - 在WSL中创建了`rpc_user`用户，密码为`rpcme`
   - 给该用户设置了在默认虚拟主机`/`上的所有权限

4. **运行Server**：
   - Server成功启动并等待RPC调用
   - 当Client发送请求时，Server接收到并处理了请求

5. **运行Client**：
   - Client成功发送了一个包含时间戳的JSON请求
   - 接收到了Server返回的响应：`Pong!1.7766537E9`

整个RPC通信流程已经成功实现，Server和Client都能正常连接到WSL中的RabbitMQ并进行通信。

Server运行状态：
- 已成功启动，显示"Waiting for RPC calls..."
- 接收到Client的请求，显示"Received API call...replying..."

Client运行状态：
- 成功发送请求，显示"Sent 'ping' RPC call. Waiting for reply..."
- 成功接收到响应，显示"RPC Reply --- Pong!1.7766537E9"

项目现在已经完全可以正常运行，使用的是WSL中的RabbitMQ服务。
