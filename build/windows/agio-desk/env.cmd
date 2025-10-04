@echo off

set PATH=%PATH%;%~dp0bin

set PYTHONPATH=%~dp0libs
rem set PYTHONPATH=G:\install_dir

for /f "usebackq delims=" %%i in (`where uv`) do set "pyexec=%%i"
set AGIO_DEFAULT_WORKSPACE_PY_EXECUTABLE=%pyexec% run python

rem PROD
set AGIO_PLATFORM_URL=https://platform.agio.services
set AGIO_DEFAULT_CLIENT_ID=b5431a17-4c52-43cf-b71b-ac700b43985f
set OAUTHLIB_INSECURE_TRANSPORT=1
set AGIO_WORKSPACE_ID=e250ea39-5feb-459b-8b2e-f57228c99fb1
set AGIO_COMPANY_ID=9f8dd69b-d292-46e6-9fa4-1dc94e1af02f


rem STAGE 
rem set "AGIO_PLATFORM_URL=https://farm-stage.agio.services"
rem set "AGIO_DEFAULT_CLIENT_ID=31e6138b-0eae-40c7-bc16-df628b6701ef"
rem set "OAUTHLIB_INSECURE_TRANSPORT=1"
rem set AGIO_WORKSPACE_ID=5872ca9a-c4bf-4a42-8a4c-97e4edbbe263
rem set AGIO_COMPANY_ID=8215ee97-f7fb-48eb-b207-b945db9c65a95a9


rem LOCAL
rem set "AGIO_PLATFORM_URL=http://192.168.0.206"
rem set "AGIO_DEFAULT_CLIENT_ID=1f68476a-2dc0-4153-b687-8f822cdc2a91"
rem set "OAUTHLIB_INSECURE_TRANSPORT=1"
rem set AGIO_WORKSPACE_ID=ef429011-0db2-46cd-8c5e-1b2106c130bb
rem set AGIO_COMPANY_ID=8215ee97-f7fb-48eb-b207-b945db9c65a9

