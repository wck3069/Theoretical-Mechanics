#!/usr/bin/env bash
# 校园 Wi-Fi 可达性自检：在连上校园 Wi-Fi 的机器上跑这一条命令即可。
# 用法: bash deploy/wifi-selftest.sh
p(){ printf '%-42s HTTP %s  %ss\n' "$1" "$(curl -s -m 12 -o /dev/null -w '%{http_code}' "$2" 2>/dev/null)" "$(curl -s -m 12 -o /dev/null -w '%{time_total}' "$2" 2>/dev/null)"; }
echo "出口 IP: $(curl -s -m 10 https://ifconfig.me 2>/dev/null || echo 取不到)"
p "国内对照(必通)"      https://www.baidu.com/
p "Cloudflare 边缘"     https://www.cloudflare.com/cdn-cgi/trace
p "GitHub Pages 镜像"   https://wck3069.github.io/Theoretical-Mechanics/
p "门禁 Quick Tunnel"   https://newbie-installation-cute-grounds.trycloudflare.com/
p "IPv4 直连 CF(绕 DNS)" https://104.16.231.132/
echo
echo "怎么读："
echo "  国内对照通 + Cloudflare/GitHub 不通  => Wi-Fi 出口过滤境外，只有校园内地址能用（映射是必须项）"
echo "  全通但隧道那条很慢/超时             => 多半是 AAAA 记录陷阱，用 curl -4 复测即可确认"
echo "  映射生效后追加一行:"
echo "    p \"映射后的入口\"            http://58.194.171.148:8443/"
