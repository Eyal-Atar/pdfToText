; PDF Processor - Inno Setup Installer Script
; יוצר קובץ התקנה מקצועי לWindows

#define MyAppName "PDF Processor"
#define MyAppVersion "1.0"
#define MyAppPublisher "PDF Tools"
#define MyAppExeName "PDF_Processor.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-4A5B-8C9D-0E1F2A3B4C5D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=installer_output
OutputBaseFilename=PDF_Processor_Setup
SetupIconFile=
Compression=lzma
SolidCompression=yes
WizardStyle=modern
DisableDirPage=no
DisableProgramGroupPage=yes
; תמיכה בעברית - RTL
LanguageDetectionMethod=locale
ShowLanguageDialog=auto

; Hebrew UI
[LangOptions]
LanguageName=Hebrew
LanguageID=$040D
RightToLeft=yes

[Languages]
Name: "hebrew"; MessagesFile: "compiler:Languages\Hebrew.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; הקובץ העיקרי - ה-EXE
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; קיצור דרך בתפריט התחל
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
; קיצור דרך בשולחן העבודה (אם נבחר)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; אפשרות להריץ את התוכנית אחרי ההתקנה
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// בדיקה אם יש גרסה קודמת מותקנת
function InitializeSetup(): Boolean;
begin
  Result := True;
end;

