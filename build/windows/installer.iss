[Setup]
AppName=agio.desk
AppVersion=0.0.1
DefaultDirName=C:\agio-desk
DefaultGroupName=agio
OutputDir=.
OutputBaseFilename=agio-desk-setup
Compression=lzma
SolidCompression=yes
SetupIconFile=agio-desk\libs\agio\resources\core\agio-icon.ico

[Files]
Source: "agio-desk\*"; DestDir: "{app}"; Flags: recursesubdirs; Excludes: "__pycache__; .git; .venv\*; *.pyc"

[Icons]
Name: "{autoprograms}\agio.desk"; Filename: "{app}\run.exe"; IconFilename: "{app}\libs\agio\resources\core\agio-icon.ico"
Name: "{userdesktop}\agio.desk"; Filename: "{app}\run.exe"; IconFilename: "{app}\libs\agio\resources\core\agio-icon.ico"

[Code]
// Функция для проверки пути на недопустимые символы (пробелы, кириллица, не-ASCII)
function CheckPathForInvalidChars(const APath: String): Boolean;
var
i: Integer;
begin
Result := True;
for i := 1 to Length(APath) do
begin
// Проверка на пробелы
if APath[i] = ' ' then
begin
Result := False;
Break;
end;
// Проверка на не-ASCII символы (коды > 127)
if Ord(APath[i]) > 127 then
begin
Result := False;
Break;
end;
end;
end;

// Функция, которая будет вызвана перед началом установки
function NextButtonClick(CurPageID: Integer): Boolean;
var
NewPath: String;
begin
Result := True;
if CurPageID = wpSelectDir then
begin
NewPath := WizardForm.DirEdit.Text;
if not CheckPathForInvalidChars(NewPath) then
begin
MsgBox('Путь установки не должен содержать пробелов, кириллицы или других специальных символов.', mbError, MB_OK);
Result := False;
end;
end;
end;