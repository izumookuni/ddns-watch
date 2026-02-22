#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DDNS IP变化监测工具
监测域名IP变化并发送邮件通知
"""

import os
import socket
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from cryptography.fernet import Fernet
import base64
import hashlib


def get_encryption_key(secret_key: str) -> bytes:
    """
    将SECRET_KEY转换为Fernet可用的密钥
    使用SHA256哈希并转换为base64格式
    """
    hash_obj = hashlib.sha256(secret_key.encode())
    key = base64.urlsafe_b64encode(hash_obj.digest())
    return key


def encrypt_ip(ip: str, secret_key: str) -> bytes:
    """加密IP地址"""
    key = get_encryption_key(secret_key)
    f = Fernet(key)
    return f.encrypt(ip.encode())


def decrypt_ip(encrypted_ip: bytes, secret_key: str) -> str:
    """解密IP地址"""
    key = get_encryption_key(secret_key)
    f = Fernet(key)
    return f.decrypt(encrypted_ip).decode()


def get_current_ip(hostname: str) -> str:
    """获取域名当前指向的IP地址"""
    try:
        ip = socket.gethostbyname(hostname)
        return ip
    except socket.gaierror as e:
        raise Exception(f"无法解析域名 {hostname}: {e}")


def read_stored_ip(file_path: str, secret_key: str) -> str | None:
    """读取存储的IP地址"""
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, 'rb') as f:
            encrypted_ip = f.read()
        return decrypt_ip(encrypted_ip, secret_key)
    except Exception as e:
        print(f"读取存储的IP失败: {e}")
        return None


def save_ip(file_path: str, ip: str, secret_key: str):
    """保存IP地址到文件"""
    encrypted_ip = encrypt_ip(ip, secret_key)
    with open(file_path, 'wb') as f:
        f.write(encrypted_ip)


def send_email(
    smtp_url: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    receive_mail: str,
    hostname: str,
    old_ip: str | None,
    new_ip: str
):
    """发送IP变化通知邮件"""
    # 创建邮件
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = receive_mail
    msg['Subject'] = f"【DDNS通知】{hostname} IP地址已变更"

    # 邮件正文
    if old_ip:
        body = f"""
域名IP地址已变更通知

域名: {hostname}
原IP地址: {old_ip}
新IP地址: {new_ip}

此邮件由DDNS监测系统自动发送，请勿回复。
"""
    else:
        body = f"""
域名IP地址首次记录

域名: {hostname}
IP地址: {new_ip}

此邮件由DDNS监测系统自动发送，请勿回复。
"""

    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # 发送邮件
    try:
        with smtplib.SMTP(smtp_url, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, receive_mail, msg.as_string())
        print(f"邮件通知已发送至 {receive_mail}")
    except Exception as e:
        raise Exception(f"发送邮件失败: {e}")


def main():
    """主函数"""
    # 从环境变量获取配置
    hostname = os.environ.get('HOST_NAME')
    smtp_url = os.environ.get('SMTP_URL')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_user = os.environ.get('SMTP_USER')
    smtp_password = os.environ.get('SMTP_PASSWORD')
    receive_mail = os.environ.get('RECEIVE_MAIL')
    secret_key = os.environ.get('SECRET_KEY')

    # 验证必要的环境变量
    required_vars = ['HOST_NAME', 'SMTP_URL', 'SMTP_USER', 'SMTP_PASSWORD', 'RECEIVE_MAIL', 'SECRET_KEY']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        raise Exception(f"缺少必要的环境变量: {', '.join(missing_vars)}")

    # IP存储文件路径
    ip_file = 'current_ip'

    print(f"开始监测域名: {hostname}")

    # 获取当前IP
    current_ip = get_current_ip(hostname)
    print(f"当前IP: {current_ip}")

    # 读取存储的IP
    stored_ip = read_stored_ip(ip_file, secret_key)
    print(f"存储的IP: {stored_ip or '无'}")

    # 比较IP
    if stored_ip != current_ip:
        print("检测到IP变化!")
        
        # 发送邮件通知
        send_email(
            smtp_url=smtp_url,
            smtp_port=smtp_port,
            smtp_user=smtp_user,
            smtp_password=smtp_password,
            receive_mail=receive_mail,
            hostname=hostname,
            old_ip=stored_ip,
            new_ip=current_ip
        )

        # 更新存储的IP
        save_ip(ip_file, current_ip, secret_key)
        print(f"IP已更新: {stored_ip or '无'} -> {current_ip}")
    else:
        print("IP未变化，无需更新")


if __name__ == '__main__':
    main()
