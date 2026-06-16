#define MyAppName "EmotionCam"
#define MyAppVersion "1.0.0"
#define MyAppExeName "EmotionCam.exe"

[Setup]
AppId={{B1449D19-39DE-499B-B2C9-585169BBED39}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={localappdata}\Programs\EmotionCam
DefaultGroupName=EmotionCam
PrivilegesRequired=lowest
OutputDir=output
OutputBaseFilename=EmotionCam-Setup-{#MyAppVersion}
SetupIconFile=..\app\assets\icon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}
LicenseFile=..\README.md

[Files]
Source: "..\dist\EmotionCam\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\EmotionCam"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\EmotionCam"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch EmotionCam"; Flags: nowait postinstall skipifsilent
