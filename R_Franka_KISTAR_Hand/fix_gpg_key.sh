#!/bin/bash

# Kitware GPG 키 문제 해결 스크립트

echo "🔑 Kitware GPG 키를 추가합니다..."

# 방법 1: 키링 파일 사용 (권장)
if curl -fsSL https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | \
   sudo gpg --dearmor -o /usr/share/keyrings/kitware-archive-keyring.gpg 2>/dev/null; then
    echo "✅ 키링 파일 방식으로 키 추가 성공"
else
    echo "⚠️  키링 파일 방식 실패, 기존 방법 시도..."
    # 방법 2: 기존 apt-key 방법
    sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 16FAAD7AF99A65E2 2>/dev/null || \
    sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 16FAAD7AF99A65E2 2>/dev/null || \
    echo "❌ GPG 키 추가 실패"
fi

echo "🔄 패키지 목록 업데이트..."
sudo apt update

