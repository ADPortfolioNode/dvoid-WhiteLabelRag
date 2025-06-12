@echo off
REM Batch file to run full verification for WhiteLabelRAG project

echo Starting Full Verification...
python "%~dp0scripts\final-verification.py"

if %ERRORLEVEL% neq 0 (
    echo.
    echo FULL VERIFICATION FAILED! Please check the output above.
    exit /b 1
) else (
    echo.
    echo FULL VERIFICATION PASSED! Ready for go-live.
    exit /b 0
)
