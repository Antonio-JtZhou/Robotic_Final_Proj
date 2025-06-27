# Robotic Final Project

## 📦 Project Structure
├── map/ # Data generation for path planning 

├── test/ # Model evaluation, including local models and API-based inference 

├── README.md # This file 

## 🚀 Project Description
This project explores the application of large language models (LLMs) in robot path planning tasks. We develop a data generation module and evaluate different models, including:

- Locally fine-tuned models
- API-based inference models

## 🔧 Modules Overview

- **map/**  
  This folder contains tools for generating synthetic path planning datasets with various map sizes and obstacle configurations.

- **test/**  
  This folder is used for evaluating model performance, supporting:
  - Local inference with fine-tuned models
  - Remote inference via API
  - Comparison between different models

## 🔥 Model Fine-Tuning
We use [LlamaFactory](https://github.com/hiyouga/LlamaFactory) for fine-tuning LLMs. Please refer to the official LlamaFactory repository for detailed usage and instructions.

