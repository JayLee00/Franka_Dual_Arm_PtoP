# Diffusion Policy 학습 지시서
> 이 파일의 지시대로 학습을 실행하고, 결과 파일 3개를 저장해 주세요.

---

## 1. 필요한 파일 목록

이 md 파일과 함께 다음 파일들이 전달되었는지 확인하세요.

```
diffusion_train.py                              ← 학습 스크립트
2026_02_28_16_47_very_good_gain_10.hdf5        ← 학습 데이터 (10 demos)
2026_02_28_01_17_good_data_demo3to9.hdf5       ← 학습 데이터 (demo 3~9)
2026_02_28_01_26_01_good_data_demo0to2.hdf5    ← 학습 데이터 (demo 0~2)
```

총 20개 데모 (~100,000 윈도우) 를 학습에 사용합니다.

---

## 2. Python 패키지 설치

```bash
pip install torch h5py numpy
```

GPU 가 있으면 PyTorch CUDA 버전을 설치하세요 (학습 속도 10배 이상 빨라짐):
```bash
# CUDA 12.x 기준
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

---

## 3. 파일 배치

아래 디렉토리 구조로 파일을 배치하세요:

```
작업폴더/
├── diffusion_train.py
└── hdf5/
    ├── 2026_02_28_16_47_very_good_gain_10.hdf5
    ├── 2026_02_28_01_17_good_data_demo3to9.hdf5
    └── 2026_02_28_01_26_01_good_data_demo0to2.hdf5
```

---

## 4. 학습 실행

`작업폴더/` 에서 아래 명령어를 실행하세요:

```bash
python3 diffusion_train.py \
    --files \
        ./hdf5/2026_02_28_16_47_very_good_gain_10.hdf5 \
        ./hdf5/2026_02_28_01_17_good_data_demo3to9.hdf5 \
        ./hdf5/2026_02_28_01_26_01_good_data_demo0to2.hdf5 \
    --demo_filter \
        "2026_02_28_01_17_good_data_demo3to9:3-9" \
        "2026_02_28_01_26_01_good_data_demo0to2:0-2" \
    --out_dir ./dp_model \
    --epochs 600 \
    --batch 256 \
    --lr 1e-4
```

> **참고**
> - `2026_02_28_16_47_very_good_gain_10.hdf5` 는 demo_0 ~ demo_9 전체 사용
> - `good_data_demo3to9` 파일은 demo 3~9 만 사용
> - `good_data_demo0to2` 파일은 demo 0~2 만 사용

---

## 5. 학습 완료 기준

아래와 같은 출력이 나오면 정상입니다:

```
[  1/600] train=0.98xxx  val=0.97xxx  lr=1.00e-04
[ 20/600] train=0.45xxx  val=0.48xxx  lr=9.xx e-05 ★
...
[DONE] best val loss : 0.0xxxx
[DONE] 모델  : ./dp_model/dp_best.pt
```

`val loss` 가 `0.1` 이하로 떨어지면 충분히 학습된 것입니다.

---

## 6. 가져와야 할 결과 파일 (3개)

학습 완료 후 `dp_model/` 폴더에서 아래 3개 파일을 저장해 주세요:

```
dp_model/dp_best.pt        ← 학습된 모델 (가중치)
dp_model/obs_norm.npz      ← 관찰 정규화 파라미터
dp_model/act_norm.npz      ← 액션 정규화 파라미터
```

이 3개 파일만 있으면 로봇 PC에서 바로 실행 가능합니다.

---

## 7. 문제 발생 시

### CUDA out of memory
```bash
# batch 크기 줄이기
python3 diffusion_train.py ... --batch 128
```

### ModuleNotFoundError: h5py
```bash
pip install h5py
```

### HDF5 파일 열기 오류 (OSError: truncated)
해당 파일이 손상된 것입니다. 해당 파일을 `--files` 목록에서 제거하고 재실행하세요.
