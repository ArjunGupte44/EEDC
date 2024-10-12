# Code Release for 2025 ICSE-NIER Submission: E2COOL - Towards Energy Efficient Code Optimizations with Large Language Models
## About
This repository contains all the artifacts of the project “E2COOL: Towards Energy Efficient Code Optimizations with Large Language Models.” It includes scripts, implementation details, and instructions necessary to reproduce the results and experiments discussed in our submission.

Our artifact includes the following
Item | Corresponding content in the paper | Dir Path | Relevant Scripts
--- | --- | --- | --- |
Energy Aware Prompting (EAP) | Section III.B, especially Figure 1 and 2 | llm/src | llm/src/new_llm_optimize.py
Energy Optimization Evaluation (EOE) | Section III.B, especially Figure 2 | energy/src | llm/src/regression_test.py, energy/src/evaluator.py
Software Benchmark | Section III.C | /benchmarks | energy/src/benchmark.py
Power Consumption Measurement | Section III.C | /RAPL | energy/src/measure_energy.py

## Table of Contents
- [Setting up the pipeline](#setting-up-the-pipeline)
- [Running the pipeline](#running-the-pipeline)
- [Manual analysis and evaluation](#manual-analysis-and-evaluation)
- [Reproduce Results](#reproduce-results)
- [Included Scripts](#included-scripts)
- [Code Dependencies](#code-dependencies)
## Setting up the pipeline
To set up the pipeline for energy-efficient code optimization, follow these steps:
1. **Clone the repository:**
   ```bash
   git clone <repository-link>
   cd <project-directory>
2. **Install the required dependencies using the Makefile**
    ```bash
   make setup
3. **Create .env in root directory**
    This should include:
    ```bash
    API_KEY=your_openai_api_key_here
    USER_PREFIX=/path/to/EEDC
## Running the pipeline
4. **Run the main script**
    ```bash
    make run

## Manual analysis and evaluation


Optimizing energy and memory efficiency for software engineering
Prompts for improving algorithmic and memory efficiency of code, respectively.
https://colab.research.google.com/drive/1u8U8VdsJZEs6JsemhYzJIMkLyUZ4fbnL#scrollTo=P6aHBE_Sb8Fj

Run "make all" in root directory to run master script. This will install all system and python dependencies.
You will also need to insert an OpenAI API key in llm/src/llm_optimize.py

tokyo:
ssh [alias]@dl-tokyo.ecn.purdue.edu
password: [password not pin],push

