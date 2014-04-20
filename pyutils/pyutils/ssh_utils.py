#coding: utf8
from __future__ import print_function

from getpass import getpass, getuser

try:
    import pexpect
except ImportError:
    pexpect = None


from zmq.ssh.tunnel import _split_server

"""
Ssh tunnel通常能实现3种功能
1)   加密网络传输
2)   绕过防火墙
3)   让位于广域网的机器连接到局域网内的机器

上图描述的是第1和第2种功能 
实现上图功能，可以用2种方法
方法1在209.132.177.50上操作
# ssh -Nf -L 10000:localhost:80 209.132.177.100
方法2在209.132.177.100上操作
# ssh -Nf -R 10000:localhost:80 209.132.177.50
上面两条命令的解释
打开主机209.132.177.50的10000端口，定向到209.132.177.100的80端口。
这样我们访问209.132.177.50的10000端口就等于访问209.132.177.100的80端口了。
其实背地里是做了如下动作
1)   209.132.177.50的ssh在209.132.177.50打开了10000端口，并且连接到209.132.177.100的22端口，
2)   209.132.177.100的sshd在22端口收到该请求，把通过该请求的连接都 转发到localhost的80端口。
3)   209.132.177.50的客户端从随即高端口连接到209.132.177.50的10000端口进行浏览，即浏览到209.132.177.100的80端口的内容
-Nf是为了让ssh tunnel挂到后台执行。否则ssh会直接打开到209.132.177.100的终端。
上面这种架构适合于翻防火墙以及加密通讯。
"""

#copy from pyzmq.ssh.tunnel, add reverse option

def openssh_tunnel(lport, rport, server, remoteip='127.0.0.1', keyfile=None, password=None, timeout=60, reverse=False):
    """Create an ssh tunnel using command-line ssh that connects port lport
    on this machine to localhost:rport on server.  The tunnel
    will automatically close when not in use, remaining open
    for a minimum of timeout seconds for an initial connection.
    
    This creates a tunnel redirecting `localhost:lport` to `remoteip:rport`,
    as seen from `server`.
    
    keyfile and password may be specified, but ssh config is checked for defaults.
    
    Parameters
    ----------
    
    lport : int
        local port for connecting to the tunnel from this machine.
    rport : int
        port on the remote machine to connect to.
    server : str
        The ssh server to connect to. The full ssh server string will be parsed.
        user@server:port
    remoteip : str [Default: 127.0.0.1]
        The remote ip, specifying the destination of the tunnel.
        Default is localhost, which means that the tunnel would redirect
        localhost:lport on this machine to localhost:rport on the *server*.
        
    keyfile : str; path to public key file
        This specifies a key to be used in ssh login, default None.
        Regular default ssh keys will be used without specifying this argument.
    password : str; 
        Your ssh password to the ssh server. Note that if this is left None,
        you will be prompted for it if passwordless key based login is unavailable.
    timeout : int [default: 60]
        The time (in seconds) after which no activity will result in the tunnel
        closing.  This prevents orphaned tunnels from running forever.
    """
    if pexpect is None:
        raise ImportError("pexpect unavailable, use paramiko_tunnel")
    if reverse:
        reverse_flag = '-R'
        lport, rport = rport, lport
    else:
        reverse_flag = '-L'
    ssh="ssh "
    if keyfile:
        ssh += "-i " + keyfile
    username, server, port = _split_server(server)
    server = username + "@" + server 
    cmd = ssh + " -f -p %i %s 127.0.0.1:%i:%s:%i %s sleep %i"%(port, reverse_flag, lport, remoteip, rport, server, timeout)
    tunnel = pexpect.spawn(cmd)
    failed = False
    while True:
        try:
            tunnel.expect('[Pp]assword:', timeout=.1)
        except pexpect.TIMEOUT:
            continue
        except pexpect.EOF:
            if tunnel.exitstatus:
                print(tunnel.exitstatus)
                print(tunnel.before)
                print(tunnel.after)
                raise RuntimeError("tunnel '%s' failed to start"%(cmd))
            else:
                return tunnel.pid
        else:
            if failed:
                print("Password rejected, try again")
                password=None
            if password is None:
                password = getpass("%s's password: "%(server))
            tunnel.sendline(password)
            failed = True
    

