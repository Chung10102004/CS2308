# BioRerank — mọi bước chạy bằng `make <đích>`. Xem HUONG_DAN.md.
SHELL := /bin/bash
PY := .venv/bin/python
export JAVA_HOME ?= /usr/lib/jvm/java-21-openjdk-amd64
export PATH := $(CURDIR)/.venv/bin:$(PATH)
CONFIRM ?= 0
SKIP_LARGE ?= 0
API_FLAGS := $(if $(filter 1,$(CONFIRM)),--confirm,) $(if $(filter 1,$(SKIP_LARGE)),--skip-large,)

.PHONY: ensemble help setup data bm25 metadata pack local kaggle-upload kaggle-run kaggle-pull lambdamart eval tables figures \
        corpus errors report demo test check-api api-dry api-run all-after-api

help:
	@grep -E '^[a-z0-9-]+:.*## ' Makefile | sed 's/:.*## /\t/' | column -t -s $$'\t'

setup: ## Tạo .venv và cài thư viện (torch bản CPU)
	python3 -m venv .venv
	$(PY) -m pip install -q --upgrade pip
	$(PY) -m pip install -q torch==2.15.0 --index-url https://download.pytorch.org/whl/cpu
	$(PY) -m pip install -q -r requirements.txt

data: ## Tải dữ liệu, chia tập, kiểm rò rỉ
	$(PY) scripts/prepare_data.py download

bm25: ## BM25 top-100 (Pyserini) cho mọi bộ + dựng index SciFact-Open
	$(PY) -m src.retrieval.bm25

metadata: ## Metadata TREC-COVID (CORD-19 + PubMed)
	$(PY) scripts/prepare_data.py metadata

pack: ## Đóng gói dữ liệu + code cho Kaggle
	$(PY) -m src.data.pack

local: data bm25 metadata pack ## Toàn bộ phần dữ liệu chạy local

kaggle-upload: pack ## Tải gói lên dataset riêng tư trên Kaggle
	$(PY) scripts/kaggle_job.py upload

kaggle-run: ## Chạy 4 task GPU trên Kaggle (tối đa 2 GPU cùng lúc) và tải kết quả về
	$(PY) scripts/kaggle_pipeline.py --push biowordvec_cut medcpt_feat bilstm & \
	$(PY) scripts/kaggle_pipeline.py --push crossenc; wait

kaggle-pull: ## Tải lại output của mọi task Kaggle
	for t in crossenc medcpt_feat biowordvec_cut bilstm crossenc_rankify crossenc_dev qwen3 bilstm2 bilstm2_abl; do $(PY) scripts/kaggle_job.py pull --task $$t; done

lambdamart: ## R1 LambdaMART (cần output medcpt_feat)
	$(PY) -m src.rerank.lambdamart --mode all

eval: ## Chấm E0–E4 từ mọi run đang có
	$(PY) scripts/run_experiment.py

tables: ## Bảng Markdown → report/tables/
	$(PY) scripts/make_tables.py

figures: ## Hình → report/figures/
	$(PY) scripts/make_figures.py

corpus: ## Phân tích ngữ liệu → report/figures/fig_data_*.png
	$(PY) scripts/corpus_analysis.py

ensemble: ## RRF ensemble, tổ hợp chọn trên dev (cần run dev của cross-encoder/Qwen3)
	-$(PY) scripts/ensemble.py

report: ensemble eval tables figures corpus errors ## Chấm lại + sinh lại toàn bộ bảng và hình

errors: ## Ca tốt / ca không tốt so với BM25
	$(PY) scripts/error_analysis.py

demo: ## Demo RAG Gradio tại http://127.0.0.1:7860
	$(PY) -m src.demo.rag_app

test: ## Unit test (API dùng client giả, không tốn tiền)
	$(PY) -m pytest -q tests

check-api: ## Kiểm tra API.json, model ID, gọi thử rất nhỏ
	$(PY) scripts/check_api.py

api-dry: ## Ước tính chi phí mọi thí nghiệm API (không gọi API)
	$(PY) scripts/run_api.py --dry-run $(if $(filter 1,$(SKIP_LARGE)),--skip-large,)

api-run: ## Chạy thí nghiệm API: make api-run CONFIRM=1 [SKIP_LARGE=1]
	$(PY) scripts/run_api.py $(API_FLAGS)
	$(MAKE) report

all-after-api: report ## Sau khi chạy API: chấm lại và sinh bảng/hình
