@echo off
title GRIS Planner
echo ========================================================
echo   GRIS PLANNER - SCP ^| PROCESSAMENTO DE DADOS
echo   Regulacao e Informatizacao SUS
echo ========================================================
echo.
echo Iniciando servidor local do Planner...
echo Abrindo navegador em http://localhost:5000
echo.
echo Para fechar o servidor, feche esta janela ou pressione Ctrl+C.
echo.

start "" "http://localhost:5000"
python -m http.server 5000 --directory public
