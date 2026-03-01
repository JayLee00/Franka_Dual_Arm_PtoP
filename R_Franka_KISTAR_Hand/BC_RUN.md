# BC(Behavior Cloning) 실행 PC에서 실행하기

## 1. 가져갈 파일

학습 PC의 `diffusion/bc_model/` 안에 있는 **3개 파일**을 실행 PC로 복사합니다.

```
bc_model/
├── bc_best.pt        ← 학습된 모델
├── state_norm.npz    ← 입력 정규화
└── action_norm.npz   ← 출력 정규화
```

추론만 할 때 쓰는 스크립트도 함께 가져가면 됩니다.

```
diffusion/bc_run.py   ← 실행 PC용 추론 전용 스크립트
```

정리하면, 실행 PC에는 예를 들어 다음처럼 두면 됩니다.

```
실행PC/어떤폴더/
├── bc_run.py
└── bc_model/
    ├── bc_best.pt
    ├── state_norm.npz
    └── action_norm.npz
```

## 2. 실행 PC 환경

- Python 3
- 패키지: `torch`, `numpy`

```bash
pip install torch numpy
```

GPU 쓰려면 CUDA 버전 PyTorch 설치.

## 3. 실행 방법

### (1) 다른 제어 스크립트에서 함수로 사용

제어 루프 안에서 **한 번만** 로드하고, 매 스텝마다 `predictor(state)`만 호출하는 방식이 좋습니다.

```python
import numpy as np
from bc_run import load_bc_predictor

# 한 번만 로드 (경로는 실제 배치한 위치로)
predictor = load_bc_predictor("./bc_model", device="cuda")  # 또는 "cpu"

# 매 제어 스텝마다:
# state = 현재 관절각(16) + 역감(12) + 촉각(60) = 88차원
state = np.concatenate([
    hand_joint_pos,    # (16,) 현재 관절 각도
    hand_kinesthetic,  # (12,) 역감 센서
    hand_tactile,      # (60,) 촉각 센서
], axis=0).astype(np.float32)

target_angles = predictor(state)   # (16,) 목표 관절 각도 → Hand에 전달
```

### (2) CLI로 동작 확인

`bc_run.py`가 있는 디렉터리에서:

```bash
python3 bc_run.py --model_dir ./bc_model
# GPU 사용
python3 bc_run.py --model_dir ./bc_model --device cuda
```

0으로 채운 88차원 state로 한 번 예측해서, 출력 shape과 값이 나오면 정상 동작입니다.

## 4. 입력 차원 (state)

- **88-dim**: 관절 16 + 역감 12 + 촉각 60 (현재 학습에 사용한 설정)
- **32-dim**: 촉각을 4-dim binary로 줄인 경우 — 이 모델은 **지금은 88-dim**으로 학습했으므로, 실행할 때도 **88-dim**으로 넣어야 합니다.

학습 시 `--tactile_binary`로 32-dim 모델을 만들었다면, 실행 PC에서도 촉각을 4-dim으로 만든 state(32-dim)를 넣어야 합니다.

## 5. 요약

| 항목 | 내용 |
|------|------|
| 복사할 것 | `bc_model/` 3개 파일 + (선택) `bc_run.py` |
| 의존성 | `torch`, `numpy` |
| 추론 | `load_bc_predictor(model_dir)` → `predictor(state)` → (16,) 목표 각도 |
