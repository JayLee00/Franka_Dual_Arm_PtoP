#!/bin/bash
# SHM 정리 스크립트

SHM_KEY=0x3940

echo "=== SHM 정리 스크립트 ==="
echo ""

# SHM 키를 10진수로 변환
SHM_KEY_DEC=$((SHM_KEY))
echo "SHM 키: $SHM_KEY (10진수: $SHM_KEY_DEC)"
echo ""

# 현재 SHM 상태 확인
echo "1. 현재 SHM 상태:"
ipcs -m 2>/dev/null | grep -E "$SHM_KEY_DEC|key" | head -5
if [ $? -ne 0 ]; then
    echo "   현재 실행 중인 SHM이 없습니다."
fi
echo ""

# SHM ID 찾기
SHM_ID=$(ipcs -m 2>/dev/null | grep "$SHM_KEY_DEC" | awk '{print $2}')
if [ -z "$SHM_ID" ]; then
    echo "✅ 해당 키($SHM_KEY)를 사용하는 SHM이 없습니다."
    exit 0
fi

echo "2. 발견된 SHM ID: $SHM_ID"
echo ""

# 연결된 프로세스 확인
ATTACHED=$(ipcs -m -i $SHM_ID 2>/dev/null | grep "nattch" | awk '{print $3}')
if [ ! -z "$ATTACHED" ] && [ "$ATTACHED" != "0" ]; then
    echo "⚠️  경고: SHM에 $ATTACHED개의 프로세스가 연결되어 있습니다."
    echo "   연결된 프로세스:"
    lsof 2>/dev/null | grep "shm" | grep "$SHM_ID" || echo "   (프로세스 정보를 가져올 수 없습니다)"
    echo ""
    echo "❌ 연결된 프로세스가 있어서 SHM을 제거할 수 없습니다."
    echo "   모든 프로세스를 종료한 후 다시 실행하세요."
    exit 1
fi

# SHM 제거 확인
echo "3. SHM 제거:"
read -p "   SHM을 제거하시겠습니까? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ipcrm -m $SHM_ID 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ SHM 제거 완료 (ID: $SHM_ID)"
    else
        echo "❌ SHM 제거 실패"
        exit 1
    fi
else
    echo "   SHM 제거 취소"
fi

echo ""
echo "=== 완료 ==="

