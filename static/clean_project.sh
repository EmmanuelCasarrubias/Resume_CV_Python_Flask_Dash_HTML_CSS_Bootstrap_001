#!/bin/bash
echo "Iniciando limpieza del proyecto..."
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
rm -rf ./venv ./.pytest_cache ./__pycache__
echo "Limpieza completada."
